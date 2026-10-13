-- 01: Monthly revenue, orders, and average order value
SELECT
    strftime('%Y-%m', o.order_date) AS month,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.quantity * p.price), 2) AS revenue,
    ROUND(SUM(oi.quantity * p.price) * 1.0 / COUNT(DISTINCT o.order_id), 2) AS aov
FROM orders o
JOIN order_items oi USING (order_id)
JOIN products p USING (product_id)
GROUP BY 1
ORDER BY 1;
