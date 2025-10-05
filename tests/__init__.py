import psycopg
conn = psycopg.connect(
    dbname="your_db_name",
    user="postgres",
    password="cassanovaFry1!",
    host="127.0.0.1",
    port=5432
)
print("Connected successfully!")
