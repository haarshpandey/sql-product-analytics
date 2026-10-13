-- 02: Acquisition-channel performance — customers, buyers, revenue
WITH channel_stats AS (
    SELECT
        c.channel,
        COUNT(DISTINCT c.customer_id) AS customers,
        COUNT(DISTINCT o.customer_id) AS buyers
    FROM customers c
    LEFT JOIN orders o USING (customer_id)
    GROUP BY 1
),
channel_revenue AS (
    SELECT c.channel, ROUND(SUM(oi.quantity * p.price), 2) AS revenue
    FROM customers c
    JOIN orders o USING (customer_id)
    JOIN order_items oi USING (order_id)
    JOIN products p USING (product_id)
    GROUP BY 1
)
SELECT
    s.channel,
    s.customers,
    s.buyers,
    ROUND(100.0 * s.buyers / s.customers, 1) AS conversion_pct,
    COALESCE(r.revenue, 0) AS revenue,
    ROUND(COALESCE(r.revenue, 0) / s.customers, 2) AS revenue_per_customer
FROM channel_stats s
LEFT JOIN channel_revenue r USING (channel)
ORDER BY revenue DESC;
