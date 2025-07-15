import pymysql

# MySQL ulanish parametrlari
host = "109.73.201.204"
user = "premium_bot"
password = "Shohzod1009"
database = "premium_bot"

try:
    # Ulanishni amalga oshirish
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    print("✅ Muvaffaqiyatli ulandi!")

    with connection.cursor() as cursor:
        # SQL so‘rov
        cursor.execute("SELECT * FROM usersold  LIMIT 10;")
        rows = cursor.fetchall()

        # Natijalarni chiqarish
        for row in rows:
            print(row)

except Exception as e:
    print("❌ Xatolik yuz berdi:", e)

finally:
    if 'connection' in locals():
        connection.close()
