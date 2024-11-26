# db_config.py
import mysql.connector

def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',  # replace with your MySQL username
        password='Iu@09082004',  # replace with your MySQL password
        database='gym_management',
        auth_plugin='mysql_native_password'  # Add this line
    )

conn = create_connection()

if conn.is_connected():
    print("Connection Established")