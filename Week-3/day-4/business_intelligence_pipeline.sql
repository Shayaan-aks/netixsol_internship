WITH invoice_metrics AS (
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.country,
    c.city,
    c.support_rep_id,
    ROUND(SUM(i.total), 2) AS total_spent,
    COUNT(DISTINCT i.invoice_id) AS total_invoices,
    COUNT(DISTINCT DATE_TRUNC('month', i.invoice_date)) AS purchase_months,
    ROUND(AVG(i.total), 2) AS avg_invoice_value
FROM customer c
JOIN invoice i ON c.customer_id = i.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.country, c.city, c.support_rep_id
),

track_metrics AS (
SELECT
    c.customer_id,
    SUM(il.quantity) AS total_tracks_purchased,
    COUNT(DISTINCT g.genre_id) AS unique_genres_purchased,
    COUNT(DISTINCT ar.artist_id) AS unique_artists_purchased
FROM customer c
JOIN invoice i ON c.customer_id = i.customer_id
JOIN invoice_line il ON i.invoice_id = il.invoice_id
JOIN track t ON il.track_id = t.track_id
JOIN genre g ON t.genre_id = g.genre_id
JOIN album al ON t.album_id = al.album_id
JOIN artist ar ON al.artist_id = ar.artist_id
GROUP BY c.customer_id
),

customer_profile AS (
SELECT
    im.customer_id,
    im.first_name,
    im.last_name,
    im.country,
    im.city,
    im.support_rep_id,
    im.total_spent,
    im.total_invoices,
    tm.total_tracks_purchased,
    tm.unique_genres_purchased,
    tm.unique_artists_purchased,
    im.purchase_months,
    im.avg_invoice_value
FROM invoice_metrics im
JOIN track_metrics tm ON im.customer_id = tm.customer_id
),

customer_segments AS (
SELECT
    *,
    CASE
        WHEN total_spent >= 45 AND total_invoices >= 7 AND unique_genres_purchased >= 4 THEN 'Platinum'
        WHEN total_spent >= 40 AND total_invoices >= 6 THEN 'Gold'
        WHEN total_spent >= 35 OR unique_genres_purchased >= 3 THEN 'Silver'
        ELSE 'Bronze'
    END AS customer_segment
FROM customer_profile
),

customer_genre_sales AS (
SELECT
    c.customer_id,
    g.name AS genre,
    SUM(il.quantity) AS tracks_bought,
    ROUND(SUM(il.unit_price * il.quantity), 2) AS genre_revenue
FROM customer c
JOIN invoice i ON c.customer_id = i.customer_id
JOIN invoice_line il ON i.invoice_id = il.invoice_id
JOIN track t ON il.track_id = t.track_id
JOIN genre g ON t.genre_id = g.genre_id
GROUP BY c.customer_id, g.name
),

favorite_genres_ranked AS (
SELECT
    customer_id,
    genre,
    tracks_bought,
    genre_revenue,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY tracks_bought DESC, genre_revenue DESC, genre
    ) AS genre_rank
FROM customer_genre_sales
),

favorite_genres AS (
SELECT
    customer_id,
    genre AS favorite_genre,
    tracks_bought AS favorite_genre_tracks,
    genre_revenue AS favorite_genre_revenue
FROM favorite_genres_ranked
WHERE genre_rank = 1
),

marketing_recommendations AS (
SELECT
    cs.customer_id,
    cs.first_name,
    cs.last_name,
    cs.country,
    cs.customer_segment,
    fg.favorite_genre,
    fg.favorite_genre_tracks,
    CASE
        WHEN cs.customer_segment = 'Platinum' THEN 'Early access to new releases in favorite genre'
        WHEN cs.customer_segment = 'Gold' THEN 'Discounted album bundles'
        WHEN cs.customer_segment = 'Silver' THEN 'Genre-based discount campaign'
        ELSE 'First upgrade coupon for next purchase'
    END AS recommended_campaign
FROM customer_segments cs
JOIN favorite_genres fg ON cs.customer_id = fg.customer_id
),

country_invoice_metrics AS (
SELECT
    c.country,
    ROUND(SUM(i.total), 2) AS total_revenue,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    COUNT(DISTINCT i.invoice_id) AS total_invoices,
    ROUND(SUM(i.total) / COUNT(DISTINCT c.customer_id), 2) AS avg_revenue_per_customer,
    ROUND(AVG(i.total), 2) AS avg_invoice_value,
    COUNT(DISTINCT c.city) AS customer_diversity
FROM customer c
JOIN invoice i ON c.customer_id = i.customer_id
GROUP BY c.country
),

country_track_metrics AS (
SELECT
    c.country,
    COUNT(DISTINCT g.genre_id) AS genres_purchased
FROM customer c
JOIN invoice i ON c.customer_id = i.customer_id
JOIN invoice_line il ON i.invoice_id = il.invoice_id
JOIN track t ON il.track_id = t.track_id
JOIN genre g ON t.genre_id = g.genre_id
GROUP BY c.country
),

country_metrics AS (
SELECT
    cim.country,
    cim.total_revenue,
    cim.total_customers,
    cim.avg_revenue_per_customer,
    cim.avg_invoice_value,
    ctm.genres_purchased,
    cim.customer_diversity,
    ROUND(
        (cim.total_revenue * 0.35) +
        (cim.avg_revenue_per_customer * 0.25) +
        (cim.avg_invoice_value * 0.15) +
        (ctm.genres_purchased * 2.00) +
        (cim.customer_diversity * 1.50),
        2
    ) AS country_performance_score
FROM country_invoice_metrics cim
JOIN country_track_metrics ctm ON cim.country = ctm.country
),

country_ranking AS (
SELECT
    *,
    RANK() OVER (ORDER BY country_performance_score DESC) AS country_rank,
    ROUND(total_revenue / SUM(total_revenue) OVER () * 100, 2) AS revenue_contribution_percentage
FROM country_metrics
),

segment_summary AS (
SELECT
    customer_segment,
    COUNT(*) AS total_customers,
    ROUND(SUM(total_spent), 2) AS segment_revenue,
    ROUND(AVG(total_spent), 2) AS avg_customer_spend,
    ROUND(AVG(total_invoices), 2) AS avg_invoices,
    ROUND(AVG(unique_genres_purchased), 2) AS avg_genres
FROM customer_segments
GROUP BY customer_segment
),

top_customers_by_segment AS (
SELECT
    customer_segment,
    customer_id,
    first_name,
    last_name,
    country,
    total_spent,
    RANK() OVER (
        PARTITION BY customer_segment
        ORDER BY total_spent DESC
    ) AS segment_customer_rank
FROM customer_segments
),

segment_genre_revenue AS (
SELECT
    cs.customer_segment,
    g.name AS genre,
    ROUND(SUM(il.unit_price * il.quantity), 2) AS genre_revenue,
    SUM(il.quantity) AS tracks_sold
FROM customer_segments cs
JOIN invoice i ON cs.customer_id = i.customer_id
JOIN invoice_line il ON i.invoice_id = il.invoice_id
JOIN track t ON il.track_id = t.track_id
JOIN genre g ON t.genre_id = g.genre_id
GROUP BY cs.customer_segment, g.name
),

top_genres_by_segment AS (
SELECT
    customer_segment,
    genre,
    genre_revenue,
    tracks_sold,
    RANK() OVER (
        PARTITION BY customer_segment
        ORDER BY genre_revenue DESC
    ) AS segment_genre_rank
FROM segment_genre_revenue
),

employee_revenue AS (
SELECT
    e.employee_id,
    e.first_name,
    e.last_name,
    e.title,
    ROUND(SUM(i.total), 2) AS total_revenue,
    RANK() OVER (ORDER BY SUM(i.total) DESC) AS employee_rank
FROM employee e
JOIN customer c ON e.employee_id = c.support_rep_id
JOIN invoice i ON c.customer_id = i.customer_id
GROUP BY e.employee_id, e.first_name, e.last_name, e.title
),

artist_revenue AS (
SELECT
    ar.artist_id,
    ar.name AS artist,
    ROUND(SUM(il.unit_price * il.quantity), 2) AS total_revenue,
    RANK() OVER (ORDER BY SUM(il.unit_price * il.quantity) DESC) AS artist_rank
FROM artist ar
JOIN album al ON ar.artist_id = al.artist_id
JOIN track t ON al.album_id = t.album_id
JOIN invoice_line il ON t.track_id = il.track_id
GROUP BY ar.artist_id, ar.name
),

album_revenue AS (
SELECT
    al.album_id,
    al.title AS album,
    ar.name AS artist,
    ROUND(SUM(il.unit_price * il.quantity), 2) AS total_revenue,
    RANK() OVER (ORDER BY SUM(il.unit_price * il.quantity) DESC) AS album_rank
FROM album al
JOIN artist ar ON al.artist_id = ar.artist_id
JOIN track t ON al.album_id = t.album_id
JOIN invoice_line il ON t.track_id = il.track_id
GROUP BY al.album_id, al.title, ar.name
),

executive_report AS (
SELECT
    'Customer Segment Summary' AS report_section,
    customer_segment AS metric_name,
    total_customers::text AS value_1,
    segment_revenue::text AS value_2,
    avg_customer_spend::text AS value_3
FROM segment_summary

UNION ALL

SELECT
    'Top Customer In Each Segment',
    customer_segment,
    first_name || ' ' || last_name,
    country,
    total_spent::text
FROM top_customers_by_segment
WHERE segment_customer_rank = 1

UNION ALL

SELECT
    'Top Genre In Each Segment',
    customer_segment,
    genre,
    genre_revenue::text,
    tracks_sold::text
FROM top_genres_by_segment
WHERE segment_genre_rank = 1

UNION ALL

SELECT
    'Best Performing Country',
    country,
    country_performance_score::text,
    total_revenue::text,
    revenue_contribution_percentage::text || '%'
FROM country_ranking
WHERE country_rank = 1

UNION ALL

SELECT
    'Revenue Contribution By Country',
    country,
    total_revenue::text,
    revenue_contribution_percentage::text || '%',
    country_rank::text
FROM country_ranking

UNION ALL

SELECT
    'Top Employee By Revenue',
    first_name || ' ' || last_name,
    title,
    total_revenue::text,
    employee_rank::text
FROM employee_revenue
WHERE employee_rank = 1

UNION ALL

SELECT
    'Top Artist By Revenue',
    artist,
    total_revenue::text,
    artist_rank::text,
    NULL
FROM artist_revenue
WHERE artist_rank = 1

UNION ALL

SELECT
    'Top Album By Revenue',
    album,
    artist,
    total_revenue::text,
    album_rank::text
FROM album_revenue
WHERE album_rank = 1
)

------------------------------------------------------------------------
------------------------------------------------------------------------
------------------------------------------------------------------------

-- TASK 1: customer spending profiles

-- SELECT *
-- FROM customer_profile
-- ORDER BY total_spent DESC;

------------------------------------------------------------------------
------------------------------------------------------------------------
------------------------------------------------------------------------

-- TASK 2: customer segmentation

-- SELECT *
-- FROM customer_segments
-- ORDER BY
-- CASE
--     WHEN customer_segment = 'Platinum' THEN 1
--     WHEN customer_segment = 'Gold' THEN 2
--     WHEN customer_segment = 'Silver' THEN 3
--     ELSE 4
-- END,
-- total_spent DESC;

------------------------------------------------------------------------
------------------------------------------------------------------------
------------------------------------------------------------------------

-- TASK 3: personalized marketing recommendation

-- SELECT *
-- FROM marketing_recommendations
-- ORDER BY
-- CASE
--     WHEN customer_segment = 'Platinum' THEN 1
--     WHEN customer_segment = 'Gold' THEN 2
--     WHEN customer_segment = 'Silver' THEN 3
--     ELSE 4
-- END,
-- customer_id;

------------------------------------------------------------------------
------------------------------------------------------------------------
------------------------------------------------------------------------

-- TASK 4: country expansion strategy

-- SELECT
--     country,
--     total_revenue,
--     total_customers,
--     avg_revenue_per_customer,
--     avg_invoice_value,
--     genres_purchased,
--     customer_diversity,
--     country_performance_score,
--     country_rank,
--     revenue_contribution_percentage
-- FROM country_ranking
-- ORDER BY country_rank;

------------------------------------------------------------------------
------------------------------------------------------------------------
------------------------------------------------------------------------

-- TASK 5: executive SQL report

SELECT *
FROM executive_report
ORDER BY report_section, metric_name;

------------------------------------------------------------------------
------------------------------------------------------------------------
------------------------------------------------------------------------
