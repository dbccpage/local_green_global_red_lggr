"""Actual SQLite transformations; only named, bounded operations are supported.

Each branch owns a separate SQLite connection created from its permitted input
slice. Branch workers consume the planner artifact, not original instructions.
The host owns the source catalog. Controllers see it only through a probe.
"""
from __future__ import annotations
import sqlite3
from contextlib import closing
from .common import digest

def _require_integer_money(value):
    if type(value) is not int:
        raise ValueError("money input requires an exact integer")
    return value

def connection(source: dict) -> sqlite3.Connection:
    for table in ("orders", "refunds"):
        for row in source.get(table, []):
            _require_integer_money(row["amount"])
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript("""
      CREATE TABLE customers(customer_id TEXT, region TEXT);
      CREATE TABLE orders(order_id TEXT, customer_id TEXT, amount INTEGER);
      CREATE TABLE refunds(refund_id TEXT, order_id TEXT, amount INTEGER);
    """)
    for table, columns in (("customers",("customer_id","region")),
                            ("orders",("order_id","customer_id","amount")),
                            ("refunds",("refund_id","order_id","amount"))):
        con.executemany(f"INSERT INTO {table} VALUES ({','.join('?' for _ in columns)})",
                        [tuple(row[k] for k in columns) for row in source.get(table,[])])
    return con

def execute_branch(branch: str, source: dict, planner: dict) -> dict:
    op = dict(planner[branch])
    scale = op.get("scale_to_cents", 1)
    if type(scale) is not int or scale <= 0:
        raise ValueError("unsupported scale")
    with closing(connection(source)) as con:
        if branch == "orders":
            if op.get("join_mode", "first") not in ("first", "all"):
                raise ValueError("unsupported join operation")
            where = "" if op.get("join_mode") == "all" else "AND c.rowid=(SELECT min(c2.rowid) FROM customers c2 WHERE c2.customer_id=o.customer_id)"
            rows = [dict(r) for r in con.execute(
                "SELECT o.order_id,o.customer_id,c.region,o.amount*? AS gross_cents "
                "FROM orders o JOIN customers c ON c.customer_id=o.customer_id " + where + " ORDER BY o.order_id,c.rowid", (scale,))]
        elif branch == "refunds":
            sign = op.get("sign",1)
            if type(sign) is not int or sign not in (-1,1):
                raise ValueError("unsupported sign")
            rows = [dict(r) for r in con.execute(
                "SELECT refund_id,order_id,amount*?*? AS refund_cents FROM refunds ORDER BY refund_id",(scale,sign))]
            if op.get("duplicate"):
                rows = rows + rows
        else:
            raise ValueError("unknown branch")
    if op.get("omit_last") and rows:
        rows = rows[:-1]
    money_column = "gross_cents" if branch == "orders" else "refund_cents"
    if any(type(row[money_column]) is not int for row in rows):
        raise ValueError("SQLite money overflow: integer output required")
    return {"branch":branch,"rows":rows,"operation":op,"planner_sha256":digest(planner),
            "source_sha256":digest(source),"local_pass":bool(all(isinstance(r,dict) for r in rows)),
            "observed_source":"sqlite.execute"}

def integrate(branches: dict, proposal: dict) -> list[dict]:
    multiplier = proposal.get("refund_multiplier",1)
    if type(multiplier) is not int:
        raise ValueError("unsupported integration multiplier")
    for branch, column in (("orders", "gross_cents"), ("refunds", "refund_cents")):
        for row in branches[branch]["rows"]:
            _require_integer_money(row[column])
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    try:
        con.executescript("CREATE TABLE gross(order_id TEXT,customer_id TEXT,region TEXT,gross_cents INTEGER);"
                          "CREATE TABLE refunded(order_id TEXT,refund_cents INTEGER);")
        con.executemany("INSERT INTO gross VALUES (?,?,?,?)",[(r["order_id"],r["customer_id"],r["region"],r["gross_cents"]) for r in branches["orders"]["rows"]])
        con.executemany("INSERT INTO refunded VALUES (?,?)",[(r["order_id"],r["refund_cents"]) for r in branches["refunds"]["rows"]])
        rows = [dict(r) for r in con.execute("SELECT g.*,coalesce(r.refund_cents,0) AS refund_cents,"
              "g.gross_cents-?*coalesce(r.refund_cents,0) AS net_cents FROM gross g "
              "LEFT JOIN (SELECT order_id,sum(refund_cents) refund_cents FROM refunded GROUP BY order_id) r "
              "ON g.order_id=r.order_id ORDER BY g.order_id,g.region",(multiplier,))]
        if any(type(row[column]) is not int for row in rows
               for column in ("gross_cents", "refund_cents", "net_cents")):
            raise ValueError("SQLite money overflow: integer output required")
        return rows
    finally:
        con.close()

def probe(name: str, case: dict, branches: dict) -> dict:
    """Actual source queries; availability is enforced by the host before entry."""
    with closing(connection(case["source"])) as con:
        if name == "source_counts":
            return {table:dict(con.execute(f"SELECT count(*) AS rows,count(DISTINCT {key}) AS unique_ids FROM {table}").fetchone())
                    for table,key in (("orders","order_id"),("customers","customer_id"),("refunds","refund_id"))}
        if name == "semantics":
            con.execute("CREATE TABLE metadata(name TEXT PRIMARY KEY,value TEXT)")
            sem = case["semantics"]
            con.executemany("INSERT INTO metadata VALUES (?,?)",[(k,str(sem[k])) for k in ("order_scale_to_cents","refund_scale_to_cents","refund_sign")])
            return {r[0]:int(r[1]) for r in con.execute("SELECT name,value FROM metadata ORDER BY name")}
        if name == "branch_evidence":
            counts = probe("source_counts",case,branches)
            return {"source_counts":counts,"branches":{b:{"rows":len(v["rows"]),
                    "unique_ids":len({r["order_id" if b=="orders" else "refund_id"] for r in v["rows"]}),
                    "negative_amounts":sum(r["gross_cents" if b=="orders" else "refund_cents"]<0 for r in v["rows"])} for b,v in branches.items()}}
        if name == "obligation_evidence":
            con.execute("CREATE TABLE obligation_evidence(id TEXT,available INTEGER)")
            con.executemany("INSERT INTO obligation_evidence VALUES (?,?)",[(o["id"],int(o.get("discharge_available",False))) for o in case["scenario"].get("obligations",[])])
            return {r[0]:{"source":"sqlite.obligation_evidence","verified":bool(r[1])} for r in con.execute("SELECT * FROM obligation_evidence")}
        if name == "migration":
            transition = case["scenario"].get("transition",{"kind":"none"})
            con.execute("CREATE TABLE migrations(kind TEXT)")
            con.execute("INSERT INTO migrations VALUES (?)",(transition.get("kind","none"),))
            kind = con.execute("SELECT kind FROM migrations").fetchone()[0]
            valid = kind == "none" or (
                kind == "validated" and transition.get("from_version") == "v1"
                and transition.get("to_version") == "v2"
                and transition.get("dimension") in ("report_schema","evaluator","specification","representation")
                and transition.get("mapping") == "identity_ledger_columns")
            return {"validated":valid,"transition":transition,"source":"sqlite.migrations"}
        raise ValueError("probe outside frozen vocabulary")
