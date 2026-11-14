"""Auxiliary declaration syntax shared by evidence ingestion and controllers."""
from .common import canonical


def requirements(contract):
    declarations = contract.get("required_auxiliary_queries", [])
    if not isinstance(declarations, list):
        raise ValueError("auxiliary declarations must be a list")
    result = []
    for raw in declarations:
        item = {"query_id": raw} if isinstance(raw, str) else raw
        if (not isinstance(item, dict) or not isinstance(item.get("query_id"), str)
                or not item["query_id"] or
                ("scope" in item and item["scope"] not in ("endpoint", "every_prefix"))):
            raise ValueError("malformed auxiliary query declaration")
        result.append(dict(item))
    return result


def matches(declaration, sample):
    return (sample.get("query_id") == declaration["query_id"]
            and ("scope" not in declaration or sample.get("scope") == declaration["scope"])
            and ("baseline" not in declaration or
                 canonical(sample.get("baseline")) == canonical(declaration["baseline"])))


def applicable(sample):
    return sample.get("scope") == "every_prefix" or sample.get("terminal") is True
