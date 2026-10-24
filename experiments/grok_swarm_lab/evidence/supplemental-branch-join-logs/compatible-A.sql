-- worker: orders

      CREATE TABLE customers(customer_id TEXT, region TEXT);

      CREATE TABLE orders(order_id TEXT, customer_id TEXT, amount INTEGER);

      CREATE TABLE refunds(refund_id TEXT, order_id TEXT, amount INTEGER);
BEGIN 
INSERT INTO customers VALUES ('c0','north')
INSERT INTO customers VALUES ('c1','south')
INSERT INTO orders VALUES ('o0','c0',100)
INSERT INTO orders VALUES ('o1','c1',200)
SELECT o.order_id,o.customer_id,c.region,o.amount*1 AS gross_cents FROM orders o JOIN customers c ON c.customer_id=o.customer_id AND c.rowid=(SELECT min(c2.rowid) FROM customers c2 WHERE c2.customer_id=o.customer_id) ORDER BY o.order_id,c.rowid
-- worker: refunds

      CREATE TABLE customers(customer_id TEXT, region TEXT);

      CREATE TABLE orders(order_id TEXT, customer_id TEXT, amount INTEGER);

      CREATE TABLE refunds(refund_id TEXT, order_id TEXT, amount INTEGER);
BEGIN 
INSERT INTO refunds VALUES ('r0','o0',50)
INSERT INTO refunds VALUES ('r1','o1',40)
SELECT refund_id,order_id,amount*1*1 AS refund_cents FROM refunds ORDER BY refund_id
-- integration
CREATE TABLE gross(order_id TEXT,customer_id TEXT,region TEXT,gross_cents INTEGER);
CREATE TABLE refunded(order_id TEXT,refund_cents INTEGER);
BEGIN 
INSERT INTO gross VALUES ('o0','c0','north',100)
INSERT INTO gross VALUES ('o1','c1','south',200)
INSERT INTO refunded VALUES ('o0',50)
INSERT INTO refunded VALUES ('o1',40)
SELECT g.*,coalesce(r.refund_cents,0) AS refund_cents,g.gross_cents-1*coalesce(r.refund_cents,0) AS net_cents FROM gross g LEFT JOIN (SELECT order_id,sum(refund_cents) refund_cents FROM refunded GROUP BY order_id) r ON g.order_id=r.order_id ORDER BY g.order_id,g.region
