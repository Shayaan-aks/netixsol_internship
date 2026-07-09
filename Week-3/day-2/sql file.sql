-- SELECT c.first_name,c.last_name,c.email,city,country
-- FROM customer AS c
-- JOIN address on c.address_id =address.address_id
-- JOIN city on address.city_id = city.city_id
-- JOIN country on city.country_id=country.country_id

-- select first_name,last_name,p.amount,title
-- FROM payment AS p
-- JOIN customer on p.customer_id=customer.customer_id
-- JOIN rental on p.rental_id=rental.rental_id
-- JOIN inventory on rental.inventory_id =inventory.inventory_id
-- JOIN film on inventory.film_id=film.film_id

-- select c.first_name,SUM(amount) as total_spent
-- FROM customer AS c
-- JOIN payment on c.customer_id=payment.customer_id
-- GROUP BY c.first_name 
-- ORDER BY total_spent DESC
-- LIMIT 10

-- SELECT
--     f.title AS film_title,
--     c.name AS category,
--     f.rental_rate
-- FROM film f
-- JOIN film_category fc
--     ON f.film_id = fc.film_id
-- JOIN category c
--     ON fc.category_id = c.category_id
-- ORDER BY f.title;

-- SELECT
--     f.title AS film_title,
--     a.first_name,
--     a.last_name
-- FROM film f
-- JOIN film_actor fa
--     ON f.film_id = fa.film_id
-- JOIN actor a
--     ON fa.actor_id = a.actor_id
-- ORDER BY f.title, a.last_name, a.first_name;

-- select count(film_id) as total_films,c.name as category
-- from category as c
-- JOIN film_category on c.category_id=film_category.category_id
-- GROUP BY c.name
-- ORDER BY total_films DESC

-- select sum(p.amount) as total_revenue,name
-- from payment as p
-- join rental on p.rental_id=rental.rental_id
-- join inventory on rental.inventory_id=inventory.inventory_id
-- join film_category on inventory.film_id=film_category.film_id
-- join category on film_category.category_id=category.category_id
-- GROUP BY name
-- ORDER BY total_revenue DESC
-- LIMIT 1
-- having max(total_revenue)

-- select c.first_name,count(rental_id)
-- from customer as c
-- join rental on c.customer_id=rental.customer_id
-- group by first_name
-- having count(rental_id)>10

-- select c.city,sum(amount) as total_revenue
-- from city as c
-- join address on c.city_id=address.city_id
-- join staff on address.address_id=staff.address_id
-- join payment on staff.staff_id=payment.staff_id
-- group by city
-- order by total_revenue desc
-- limit 1

select ,sum(amount) as total_revenue
from city as c
join address on c.city_id=address.city_id
join staff on address.address_id=staff.address_id
join payment on staff.staff_id=payment.staff_id
group by city
order by total_revenue desc
limit 1


