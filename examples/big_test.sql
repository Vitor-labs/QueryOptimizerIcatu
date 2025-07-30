SELECT DISTINCT
    (SELECT COUNT(*) FROM orders o1 WHERE o1.customer_id = c.customer_id) as total_orders,
    (SELECT COUNT(*) FROM orders o2 WHERE o2.customer_id = c.customer_id AND o2.status = 'completed') as completed_orders,
    (SELECT COUNT(*) FROM orders o3 WHERE o3.customer_id = c.customer_id AND o3.status = 'pending') as pending_orders,
    (SELECT COUNT(*) FROM orders o4 WHERE o4.customer_id = c.customer_id AND o4.status = 'cancelled') as cancelled_orders,
    (SELECT AVG(o5.total_amount) FROM orders o5 WHERE o5.customer_id = c.customer_id) as avg_order_value,
    (SELECT MAX(o6.order_date) FROM orders o6 WHERE o6.customer_id = c.customer_id) as last_order_date,
    (SELECT MIN(o7.order_date) FROM orders o7 WHERE o7.customer_id = c.customer_id) as first_order_date,
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.phone,
    c.address_line1,
    c.address_line2,
    c.city,
    c.state,
    c.zip_code,
    c.country,
    c.registration_date,
    CASE 
        WHEN (SELECT COUNT(*) FROM orders o8 WHERE o8.customer_id = c.customer_id) > 50 THEN 'VIP'
        WHEN (SELECT COUNT(*) FROM orders o9 WHERE o9.customer_id = c.customer_id) > 20 THEN 'Premium'
        WHEN (SELECT COUNT(*) FROM orders o10 WHERE o10.customer_id = c.customer_id) > 5 THEN 'Regular'
        ELSE 'New'
    END as customer_tier,
    (SELECT p.product_name 
     FROM order_items oi 
     JOIN products p ON oi.product_id = p.product_id 
     JOIN orders o11 ON oi.order_id = o11.order_id 
     WHERE o11.customer_id = c.customer_id 
     GROUP BY p.product_id, p.product_name 
     ORDER BY SUM(oi.quantity) DESC 
     LIMIT 1) as most_purchased_product,
    (SELECT cat.category_name 
     FROM order_items oi2 
     JOIN products p2 ON oi2.product_id = p2.product_id 
     JOIN categories cat ON p2.category_id = cat.category_id
     JOIN orders o12 ON oi2.order_id = o12.order_id 
     WHERE o12.customer_id = c.customer_id 
     GROUP BY cat.category_id, cat.category_name 
     ORDER BY COUNT(*) DESC 
     LIMIT 1) as favorite_category,
    (SELECT SUM(o13.total_amount) FROM orders o13 WHERE o13.customer_id = c.customer_id AND YEAR(o13.order_date) = 2023) as total_2023_spending,
    (SELECT SUM(o14.total_amount) FROM orders o14 WHERE o14.customer_id = c.customer_id AND YEAR(o14.order_date) = 2022) as total_2022_spending,
    (SELECT COUNT(*) FROM orders o15 WHERE o15.customer_id = c.customer_id AND MONTH(o15.order_date) = MONTH(CURDATE()) AND YEAR(o15.order_date) = YEAR(CURDATE())) as orders_this_month,
    UPPER(CONCAT(c.first_name, ' ', c.last_name)) as full_name_upper,
    LOWER(CONCAT(c.first_name, ' ', c.last_name)) as full_name_lower,
    CONCAT(c.first_name, ' ', c.last_name) as full_name,
    DATEDIFF(CURDATE(), c.registration_date) as days_since_registration,
    DATEDIFF(CURDATE(), (SELECT MAX(o16.order_date) FROM orders o16 WHERE o16.customer_id = c.customer_id)) as days_since_last_order,
    (SELECT shipping_address FROM orders o17 WHERE o17.customer_id = c.customer_id ORDER BY o17.order_date DESC LIMIT 1) as last_shipping_address,
    (SELECT payment_method FROM orders o18 WHERE o18.customer_id = c.customer_id ORDER BY o18.order_date DESC LIMIT 1) as last_payment_method
FROM customers c
WHERE c.customer_id IN (
    SELECT DISTINCT o19.customer_id 
    FROM orders o19 
    WHERE o19.order_date >= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)
)
AND c.customer_id NOT IN (
    SELECT DISTINCT o20.customer_id 
    FROM orders o20 
    WHERE o20.status = 'fraud'
)
AND EXISTS (
    SELECT 1 FROM orders o21 WHERE o21.customer_id = c.customer_id
)
AND c.email LIKE '%@%'
AND LENGTH(c.phone) >= 10
AND c.registration_date IS NOT NULL
ORDER BY 
    (SELECT COUNT(*) FROM orders o22 WHERE o22.customer_id = c.customer_id) DESC,
    (SELECT SUM(o23.total_amount) FROM orders o23 WHERE o23.customer_id = c.customer_id) DESC,
    c.registration_date DESC,
    c.last_name ASC,
    c.first_name ASC;
