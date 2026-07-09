-- ============================================================
-- 1. Find the total revenue generated per store.
-- ============================================================

SELECT
    s.store_id,
    SUM(p.amount) AS total_revenue
FROM store s
JOIN staff st
    ON s.store_id = st.store_id
JOIN payment p
    ON st.staff_id = p.staff_id
GROUP BY s.store_id
ORDER BY total_revenue DESC;
-- ============================================================
-- 2. Find the average rental duration per film category.
-- ============================================================

SELECT
    c.name AS category,
    AVG(f.rental_duration) AS avg_rental_duration
FROM category c
JOIN film_category fc
    ON c.category_id = fc.category_id
JOIN film f
    ON fc.film_id = f.film_id
GROUP BY c.name
ORDER BY avg_rental_duration DESC;
-- ============================================================
-- 3. Find the number of rentals made each month.
-- ============================================================

SELECT
    DATE_TRUNC('month', rental_date) AS rental_month,
    COUNT(*) AS total_rentals
FROM rental
GROUP BY rental_month
ORDER BY rental_month;
-- ============================================================
-- 4. Find categories with more than 50 films (use HAVING).
-- ============================================================

SELECT
    c.name AS category,
    COUNT(fc.film_id) AS total_films
FROM category c
JOIN film_category fc
    ON c.category_id = fc.category_id
GROUP BY c.name
HAVING COUNT(fc.film_id) > 50
ORDER BY total_films DESC;
-- ============================================================
-- 5. Find customers who spent more than the average customer spend.
-- ============================================================

SELECT
    customer_id,
    SUM(amount) AS total_spent
FROM payment
GROUP BY customer_id
HAVING SUM(amount) >
(
    SELECT AVG(total_spent)
    FROM
    (
        SELECT
            customer_id,
            SUM(amount) AS total_spent
        FROM payment
        GROUP BY customer_id
    ) avg_customer
)
ORDER BY total_spent DESC;
-- ============================================================
-- 6. Find the film(s) with the highest rental rate in each category
--    (Correlated Subquery)
-- ============================================================

SELECT
    c.name AS category,
    f.title,
    f.rental_rate
FROM film f
JOIN film_category fc
    ON f.film_id = fc.film_id
JOIN category c
    ON fc.category_id = c.category_id
WHERE f.rental_rate =
(
    SELECT MAX(f2.rental_rate)
    FROM film f2
    JOIN film_category fc2
        ON f2.film_id = fc2.film_id
    WHERE fc2.category_id = fc.category_id
)
ORDER BY c.name, f.title;
-- ============================================================
-- 7. Find customers who have never rented a film
--    (Using NOT EXISTS)
-- ============================================================

SELECT
    c.customer_id,
    c.first_name,
    c.last_name
FROM customer c
WHERE NOT EXISTS
(
    SELECT 1
    FROM rental r
    WHERE r.customer_id = c.customer_id
);
-- ============================================================
-- 8. Find the store with the highest total revenue
--    (Subquery in WHERE clause)
-- ============================================================

SELECT
    revenue.store_id,
    revenue.total_revenue
FROM
(
    SELECT
        s.store_id,
        SUM(p.amount) AS total_revenue
    FROM store s
    JOIN staff st
        ON s.store_id = st.store_id
    JOIN payment p
        ON st.staff_id = p.staff_id
    GROUP BY s.store_id
) revenue
WHERE revenue.total_revenue =
(
    SELECT MAX(total_revenue)
    FROM
    (
        SELECT
            s.store_id,
            SUM(p.amount) AS total_revenue
        FROM store s
        JOIN staff st
            ON s.store_id = st.store_id
        JOIN payment p
            ON st.staff_id = p.staff_id
        GROUP BY s.store_id
    ) max_rev
);
-- ============================================================
-- 9. Using a CTE, rank customers by total spend within each city.
-- ============================================================

WITH customer_spending AS
(
    SELECT
        c.customer_id,
        c.first_name,
        c.last_name,
        ci.city,
        SUM(p.amount) AS total_spent
    FROM customer c
    JOIN address a
        ON c.address_id = a.address_id
    JOIN city ci
        ON a.city_id = ci.city_id
    JOIN payment p
        ON c.customer_id = p.customer_id
    GROUP BY
        c.customer_id,
        c.first_name,
        c.last_name,
        ci.city
)

SELECT *,
       RANK() OVER
       (
           PARTITION BY city
           ORDER BY total_spent DESC
       ) AS city_rank
FROM customer_spending
ORDER BY city, city_rank;
-- ============================================================
-- 10. Using ROW_NUMBER(), find the most recently rented film
--     for each customer.
-- ============================================================

SELECT *
FROM
(
    SELECT
        c.customer_id,
        c.first_name,
        c.last_name,
        f.title,
        r.rental_date,
        ROW_NUMBER() OVER
        (
            PARTITION BY c.customer_id
            ORDER BY r.rental_date DESC
        ) AS rn
    FROM customer c
    JOIN rental r
        ON c.customer_id = r.customer_id
    JOIN inventory i
        ON r.inventory_id = i.inventory_id
    JOIN film f
        ON i.film_id = f.film_id
) recent
WHERE rn = 1;
-- ============================================================
-- 11. Using a CTE, calculate month-over-month rental revenue growth.
-- ============================================================

WITH monthly_revenue AS
(
    SELECT
        DATE_TRUNC('month', payment_date) AS month,
        SUM(amount) AS revenue
    FROM payment
    GROUP BY month
)

SELECT
    month,
    revenue,
    LAG(revenue) OVER
    (
        ORDER BY month
    ) AS previous_month_revenue,
    revenue -
    LAG(revenue) OVER
    (
        ORDER BY month
    ) AS revenue_growth
FROM monthly_revenue
ORDER BY month;
-- ============================================================
-- 12. Find the top 3 highest-grossing films per category
--     using RANK() inside a CTE.
-- ============================================================

WITH film_revenue AS
(
    SELECT
        c.name AS category,
        f.title,
        SUM(p.amount) AS revenue
    FROM payment p
    JOIN rental r
        ON p.rental_id = r.rental_id
    JOIN inventory i
        ON r.inventory_id = i.inventory_id
    JOIN film f
        ON i.film_id = f.film_id
    JOIN film_category fc
        ON f.film_id = fc.film_id
    JOIN category c
        ON fc.category_id = c.category_id
    GROUP BY
        c.name,
        f.title
),

ranked_films AS
(
    SELECT *,
           RANK() OVER
           (
               PARTITION BY category
               ORDER BY revenue DESC
           ) AS film_rank
    FROM film_revenue
)

SELECT *
FROM ranked_films
WHERE film_rank <= 3
ORDER BY category, film_rank;