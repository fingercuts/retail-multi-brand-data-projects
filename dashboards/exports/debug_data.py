import duckdb
con = duckdb.connect('data/multibrand_retail.duckdb', read_only=True)

print("=== Jakarta cities in dim_customers ===")
print(con.execute("""
    SELECT city, region, COUNT(*) as cnt 
    FROM dim_customers 
    WHERE region = 'DKI Jakarta'
    GROUP BY 1, 2 ORDER BY 3 DESC
""").df().to_string())

print("\n=== Top 15 cities by customer revenue ===")
print(con.execute("""
    SELECT c.city, c.region, SUM(s.net_amount) as revenue, COUNT(DISTINCT c.customer_id) as customers
    FROM fct_sales s
    JOIN dim_customers c ON s.customer_id = c.customer_id
    GROUP BY 1, 2 ORDER BY 3 DESC LIMIT 15
""").df().to_string())

print("\n=== Channel mix for dashboard ===")
print(con.execute("""
    SELECT 
        COALESCE(ch.channel_name, 'In-Store') as channel,
        COUNT(*) as txns, SUM(s.net_amount) as rev
    FROM fct_sales s
    LEFT JOIN dim_channels ch ON s.channel_id = ch.channel_id
    GROUP BY 1 ORDER BY 3 DESC
""").df().to_string())

con.close()
