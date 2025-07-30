
WITH CustomerOrderStats AS (
  SELECT
    customer_id,
    COUNT(order_id) AS total_orders,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_orders,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending_orders,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    AVG(total_amount) AS avg_order_value,
    MAX(order_date) AS last_order_date,
    MIN(order_date) AS first_order_date
  FROM orders
  WHERE
    status != 'fraud'
  GROUP BY
    customer_id
), CustomerProductStats AS (
  SELECT
    oi.order_id,
    p.product_name,
    c.category_name,
    oi.product_id,
    c.category_id,
    o.customer_id
  FROM order_items AS oi
  JOIN products AS p
    ON oi.product_id = p.product_id
  JOIN orders AS o
    ON oi.order_id = o.order_id
  JOIN categories AS c
    ON p.category_id = c.category_id
), CustomerSpending AS (
  SELECT
    o.customer_id,
    SUM(CASE WHEN STRFTIME('%Y', o.order_date) = '2022' THEN o.total_amount ELSE 0 END) AS spending_2022,
    SUM(CASE WHEN STRFTIME('%Y', o.order_date) = '2023' THEN o.total_amount ELSE 0 END) AS spending_2023,
    SUM(CASE WHEN STRFTIME('%Y-%m', o.order_date) = STRFTIME('%Y-%m', DATE('now')) THEN o.total_amount ELSE 0 END) AS spending_this_month
  FROM orders AS o
  GROUP BY
    o.customer_id
), LastOrderInfo AS (
  SELECT
    o.customer_id,
    o.shipping_address AS last_shipping_address,
    o.payment_method AS last_payment_method,
    o.order_date AS last_order_date
  FROM orders AS o
  WHERE
    o.order_date = (
      SELECT
        MAX(order_date)
      FROM orders AS o2
      WHERE
        o2.customer_id = o.customer_id
    )
  GROUP BY
    o.customer_id
)
SELECT
  c.customer_id,
  c.first_name,
  c.last_name,
  c.email,
  c.phone_number,
  c.address,
  c.registration_date,
  COS.total_orders,
  COS.completed_orders,
  COS.pending_orders,
  COS.cancelled_orders,
  COS.avg_order_value,
  COS.last_order_date,
  COS.first_order_date,
  CASE
    WHEN COS.total_orders >= 50
    THEN 'Platinum'
    WHEN COS.total_orders >= 20
    THEN 'Gold'
    WHEN COS.total_orders >= 5
    THEN 'Silver'
    ELSE 'Bronze'
  END AS customer_tier,
  (
    SELECT
      CPS.product_name
    FROM CustomerProductStats AS CPS
    WHERE
      CPS.customer_id = c.customer_id
    GROUP BY
      CPS.product_name
    ORDER BY
      COUNT(*) DESC
    LIMIT 1
  ) AS most_purchased_product,
  (
    SELECT
      CPS.category_name
    FROM CustomerProductStats AS CPS
    WHERE
      CPS.customer_id = c.customer_id
    GROUP BY
      CPS.category_name
    ORDER BY
      COUNT(*) DESC
    LIMIT 1
  ) AS favorite_category,
  CS.spending_2022,
  CS.spending_2023,
  CS.spending_this_month,
  (
    SELECT
      COUNT(*)
    FROM orders
    WHERE
      customer_id = c.customer_id AND STRFTIME('%Y-%m', order_date) = STRFTIME('%Y-%m', DATE('now'))
  ) AS orders_this_month,
  UPPER(c.first_name) || ' ' || UPPER(c.last_name) AS full_name_upper,
  LOWER(c.first_name) || ' ' || LOWER(c.last_name) AS full_name_lower,
  c.first_name || ' ' || SUBSTR(c.last_name, 1, 1) || '.' AS full_name_abbreviated,
  JULIANDAY('now') - JULIANDAY(c.registration_date) AS days_since_registration,
  JULIANDAY('now') - JULIANDAY(LOI.last_order_date) AS days_since_last_order,
  LOI.last_shipping_address,
  LOI.last_payment_method
FROM customers AS c
JOIN CustomerOrderStats AS COS
  ON c.customer_id = COS.customer_id
JOIN CustomerSpending AS CS
  ON c.customer_id = CS.customer_id
JOIN LastOrderInfo AS LOI
  ON c.customer_id = LOI.customer_id
WHERE
  COS.last_order_date >= DATE('now', '-2 years') AND c.email LIKE '%@%' AND LENGTH(c.phone_number) >= 10 AND c.registration_date IS NOT NULL
ORDER BY
  COS.total_orders DESC,
  (
    CS.spending_2022 + CS.spending_2023
  ) DESC,
  c.registration_date DESC,
  c.last_name ASC,
  c.first_name ASC;
