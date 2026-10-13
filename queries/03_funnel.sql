-- 03: Marketing funnel — conversion between steps
WITH steps AS (
    SELECT
        COUNT(DISTINCT CASE WHEN event_type = 'page_view'   THEN customer_id END) AS viewed,
        COUNT(DISTINCT CASE WHEN event_type = 'add_to_cart'  THEN customer_id END) AS carted,
        COUNT(DISTINCT CASE WHEN event_type = 'checkout'     THEN customer_id END) AS checked_out,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase'     THEN customer_id END) AS purchased
    FROM funnel_events
)
SELECT
    viewed,
    carted,
    ROUND(100.0 * carted / viewed, 1) AS view_to_cart_pct,
    checked_out,
    ROUND(100.0 * checked_out / carted, 1) AS cart_to_checkout_pct,
    purchased,
    ROUND(100.0 * purchased / checked_out, 1) AS checkout_to_purchase_pct,
    ROUND(100.0 * purchased / viewed, 1) AS overall_conversion_pct
FROM steps;
