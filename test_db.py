import psycopg2

# Database configuration (Replace with real credentials)
DB_CONFIG = {
    'dbname': 'click_logger',
    'user': 'click',
    'password': 'lol007',
    'host': '34.93.76.26',
    'port': '5432'
}


def main():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        # cur.execute("SELECT * FROM clicks;")
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'clicks';")
        rows = cur.fetchall()
        for row in rows:
            print(row)
    except Exception as e:
        print("error")


if __name__ == '__main__':
    main()
