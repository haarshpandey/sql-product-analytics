-- 05: Top products by revenue and units
SELECT
    p.name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    COUNT(DISTINCT oi.order_id) AS orders,
    ROUND(SUM(oi.quantity * p.price), 2) AS revenue
FROM order_items oi
JOIN products p USING (product_id)
GROUP BY 1, 2
ORDER BY revenue DESC;
