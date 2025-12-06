import mysql.connector

# cursor.execute(sql_query, params) is used to execute a SQL query with parameters
# database connection


# please replace your own parameters for host, user, and password.
try:
    mydb = mysql.connector.connect(
        host="your_entry",
        user="your_user",
        password="your_password",
        database="atm"
    )
    cursor = mydb.cursor()
    print("Connected to the database.")
except mysql.connector.Error as err:
    print("Connection error:", err)
    exit()