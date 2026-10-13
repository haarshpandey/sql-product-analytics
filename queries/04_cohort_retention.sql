-- 04: Monthly acquisition cohorts — repeat-purchase rate by cohort
WITH cohorts AS (
    SELECT
        customer_id,
        strftime('%Y-%m', acquired_date) AS cohort_month
    FROM customers
),
buyer_flags AS (
    SELECT
        c.cohort_month,
        c.customer_id,
        COUNT(o.order_id) AS n_orders
    FROM cohorts c
    LEFT JOIN orders o USING (customer_id)
    GROUP BY 1, 2
)
SELECT
    cohort_month,
    COUNT(*) AS customers,
    SUM(CASE WHEN n_orders >= 1 THEN 1 ELSE 0 END) AS buyers,
    ROUND(100.0 * SUM(CASE WHEN n_orders >= 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS buyer_rate_pct,
    SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END) AS repeat_buyers,
    ROUND(100.0 * SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN n_orders >= 1 THEN 1 ELSE 0 END), 0), 1) AS repeat_rate_pct
FROM buyer_flags
GROUP BY 1
ORDER BY 1;
