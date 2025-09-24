#The access/linker code for the application code and the database

import mysql.connector
from mysql.connector import Error

def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # I do not have password (for easier access)
            database="fletapp"
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        raise e