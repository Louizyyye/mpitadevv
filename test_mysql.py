import pymysql

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="YourPasswordHere",
        database="YourDatabaseName"  # replace with actual
    )
    print("✅ Connected successfully!")
except Exception as e:
    print("❌ Error:", e)
