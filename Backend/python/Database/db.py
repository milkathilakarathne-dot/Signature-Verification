import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

user = os.getenv("POSTGRE_USER")
password = os.getenv("POSTGRE_PASSWORD")
database = os.getenv("POSTGRE_DATABASE")
host = os.getenv("POSTGRE_HOST")
port = os.getenv("POSTGRE_PORT")

schema = os.getenv("SCHEMA")
user_table = os.getenv("USER_TABLE")


def create_schema_tables_if_not_exist(connection):
    
    cursor = connection.cursor()
    
    cursor.execute("""
        CREATE SCHEMA IF NOT EXISTS signature;

        CREATE TABLE IF NOT EXISTS signature.alluser_login (
            id SERIAL PRIMARY KEY,
            nic VARCHAR(100),
            username VARCHAR(100),
            password VARCHAR(20),
            role VARCHAR(20)
        );
    """)
    
    connection.commit()
    
    
def create_connection():
    connection = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port
    )
    
    create_schema_tables_if_not_exist(connection)
    
    return connection


def authenticate_userlogin(username, password):
    
    connection = create_connection()
    
    query = f"""
    select role FROM signature.alluser_login
    where username = '{username}' and password = '{password}'
    """
    
    cursor = connection.cursor()
    cursor.execute(query)
    record = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if record:
        return record[0]



def add_new_user_signature(username, password):
    
    connection = create_connection()
    
    try:
        query = """
        INSERT INTO signature.alluser_login (nic, username, password, role)
        VALUES (%s, %s, %s, %s);
        """
        cursor = connection.cursor()
        cursor.execute(query, (username, username, password, "USER"))
        connection.commit()

        print("User added successfully")
        return True

    except Exception as e:
        connection.rollback()
        print("New user adding failed! because", e)
        return False

    finally:
        cursor.close()
        connection.close()