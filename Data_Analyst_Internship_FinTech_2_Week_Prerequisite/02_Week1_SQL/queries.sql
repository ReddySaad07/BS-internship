-- Data Analyst Internship – SQL Practice
-- Database: sales_analysis.db
-- Main table: orders

-- 1. SELECT
SELECT * FROM orders LIMIT 10;

-- 2. WHERE
SELECT order_id, customer_id, product, sales_amount
FROM orders
WHERE sales_amount > 50000
ORDER BY sales_amount DESC;

-- 3. ORDER BY
SELECT product, sales_amount
FROM orders
ORDER BY sales_amount DESC;

-- 4. GROUP BY – revenue by product
SELECT product, ROUND(SUM(sales_amount),2) AS revenue
FROM orders
GROUP BY product
ORDER BY revenue DESC;

-- 5. HAVING – products above a revenue threshold
SELECT product, ROUND(SUM(sales_amount),2) AS revenue
FROM orders
GROUP BY product
HAVING SUM(sales_amount) > 1000000
ORDER BY revenue DESC;

-- 6. JOIN example using a derived customer summary
WITH customer_summary AS (
    SELECT customer_id, SUM(sales_amount) AS revenue
    FROM orders
    GROUP BY customer_id
)
SELECT o.order_id, o.customer_id, o.product, o.sales_amount, c.revenue AS customer_total_revenue
FROM orders o
JOIN customer_summary c ON o.customer_id = c.customer_id
LIMIT 20;

-- 7. Aggregate functions
SELECT
    COUNT(*) AS orders,
    COUNT(DISTINCT customer_id) AS customers,
    ROUND(SUM(sales_amount),2) AS revenue,
    ROUND(AVG(sales_amount),2) AS avg_order_value,
    ROUND(MAX(sales_amount),2) AS max_order_value
FROM orders;

-- 8. Subquery – orders above average order value
SELECT order_id, product, sales_amount
FROM orders
WHERE sales_amount > (SELECT AVG(sales_amount) FROM orders)
ORDER BY sales_amount DESC;

-- 9. Basic window function – customer revenue rank
SELECT
    customer_id,
    ROUND(SUM(sales_amount),2) AS revenue,
    RANK() OVER (ORDER BY SUM(sales_amount) DESC) AS revenue_rank
FROM orders
GROUP BY customer_id;

-- 10. Monthly trend
SELECT month, ROUND(SUM(sales_amount),2) AS revenue
FROM orders
GROUP BY month
ORDER BY month;

-- 11. Product performance
SELECT product,
       SUM(quantity) AS units_sold,
       ROUND(SUM(sales_amount),2) AS revenue,
       ROUND(SUM(profit),2) AS profit,
       ROUND(100.0*SUM(profit)/SUM(sales_amount),2) AS profit_margin_pct
FROM orders
GROUP BY product
ORDER BY revenue DESC;
