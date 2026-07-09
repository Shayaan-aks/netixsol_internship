# Week-3 Day-4

## Segmentation Logic and Justification

The customer segmentation was based on multiple customer behavior metrics instead of only total spending. The metrics used were:

- `total_spent`
- `total_invoices`
- `unique_genres_purchased`

The segmentation logic was:

- **Platinum:** customers with high spending, high invoice count, and strong genre diversity.
- **Gold:** customers with strong spending and regular purchase frequency.
- **Silver:** customers with moderate spending or some genre diversity.
- **Bronze:** customers below the Silver threshold.

This logic is useful because a valuable customer is not only someone who spends more money. A strong customer may also buy frequently and explore multiple genres, which makes them easier to target with different campaigns.

In the results, most customers were classified as **Silver**, while smaller groups were classified as **Gold** and **Platinum**. No customers fell into Bronze using this dataset and threshold logic.

## Country Ranking Methodology

The country expansion score was calculated using multiple business metrics:

- Total revenue
- Total customers
- Average revenue per customer
- Average invoice value
- Number of genres purchased
- Customer diversity by city

The scoring formula gave the highest weight to total revenue, but also included customer quality and diversity. The formula used was:

```sql
(total_revenue * 0.35)
+ (avg_revenue_per_customer * 0.25)
+ (avg_invoice_value * 0.15)
+ (genres_purchased * 2.00)
+ (customer_diversity * 1.50)
```

This means countries were not ranked only by revenue. A country with strong average customer value, genre diversity, and customers spread across multiple cities could also rank well.

The top three countries from the ranking were:

1. USA
2. Canada
3. France

These countries are the strongest candidates for future expansion because they combine strong revenue with healthy customer and genre activity.

## Marketing Recommendation Strategy

The marketing recommendation strategy used customer segments and each customer's favorite genre.

First, each customer's favorite genre was calculated by counting how many tracks they purchased in each genre. Then `ROW_NUMBER()` was used to rank genres per customer and select the top genre.

Campaigns were assigned by segment:

- **Platinum:** early access to new releases in their favorite genre
- **Gold:** discounted album bundles
- **Silver:** genre-based discount campaigns
- **Bronze:** first upgrade coupon for next purchase

This strategy makes the campaign more personalized because it does not only depend on customer value. It also uses the customer's actual listening and purchase behavior.

## Key Results

- The largest segment was **Silver**, with 45 customers and total revenue of 1713.92.
- **Gold** had 9 customers and total revenue of 379.58.
- **Platinum** had 5 customers and total revenue of 235.10.
- The best country for expansion was **USA**, followed by **Canada** and **France**.
- The top employee by revenue was **Jane Peacock**, with 833.04 in sales.
- The top artist by revenue was **Iron Maiden**, with 138.60 in revenue.
- The top album by revenue was **Battlestar Galactica (Classic), Season 1**, with 35.82 in revenue.
- The highest-selling genre was **Rock**, followed by **Latin**, **Metal**, **Alternative & Punk**, and **Jazz**.

## Actionable Recommendations

1. **Prioritize expansion in the USA, Canada, and France.**  
   These countries ranked highest in the country performance score and should be the first targets for future growth campaigns.

2. **Use Rock as the main promotional genre.**  
   Rock had the highest track sales and revenue, so it should be featured in homepage promotions, email campaigns, and bundle offers.

3. **Create genre-based campaigns for Silver customers.**  
   Silver customers are the largest segment, so even small improvements in conversion from this group could create meaningful revenue growth.

4. **Offer early access campaigns to Platinum customers.**  
   Platinum customers are few but high value. They should receive exclusive offers, early releases, and personalized recommendations.

5. **Use album bundles for Gold customers.**  
   Gold customers already show strong purchase behavior, so discounted album bundles can encourage them to increase average invoice value.

6. **Study Jane Peacock's customer base and sales approach.**  
   Jane Peacock generated the highest employee-linked revenue, so her customer portfolio may contain useful patterns for sales strategy.

7. **Promote Iron Maiden and similar artists.**  
   Iron Maiden was the top artist by revenue, so similar artists or genre-adjacent recommendations may perform well with existing customers.

## Challenges Faced and How They Were Solved

One challenge was avoiding repeated calculations across tasks. This was solved by creating reusable CTEs such as `customer_profile`, `customer_segments`, `favorite_genres`, and `country_ranking`.

Another challenge was separating invoice-level calculations from track-level calculations. Invoice totals were calculated from the `invoice` table, while genre, artist, and album revenue were calculated from `invoice_line`. This avoided duplicated revenue caused by joining invoice rows to multiple invoice lines.

A third challenge was building a final executive report from many different metrics. This was solved by creating smaller CTEs for each business area, then combining their outputs into one final report using `UNION ALL`.

## Deliverables

- `business_intelligence_pipeline.sql` contains the full SQL pipeline.
- Screenshots include customer segmentation results, country ranking results, final executive report, and successful query execution.
