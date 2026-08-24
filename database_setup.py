import mysql.connector
from mysql.connector import Error

def setup_database():
    try:
        # Prompt for credentials to create the database (requires root or admin access)
        host = input("Enter MySQL Host [localhost]: ") or "localhost"
        user = input("Enter MySQL Username [root]: ") or "root"
        password = input("Enter MySQL Password: ")

        print("\nConnecting to MySQL server...")
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Creating database 'space_invader_db' if it doesn't exist...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS space_invader_db")
            
            print("Using 'space_invader_db'...")
            cursor.execute("USE space_invader_db")
            
            print("Creating 'players' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    ship_color VARCHAR(20) DEFAULT 'green',
                    player_title VARCHAR(50) DEFAULT 'Space Cadet',
                    control_scheme VARCHAR(10) DEFAULT 'arrows',
                    difficulty VARCHAR(10) DEFAULT 'normal',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            print("Updating 'players' table schema if needed (adding new columns)...")
            alter_queries = [
                "ALTER TABLE players ADD COLUMN ship_color VARCHAR(20) DEFAULT 'green'",
                "ALTER TABLE players ADD COLUMN player_title VARCHAR(50) DEFAULT 'Space Cadet'",
                "ALTER TABLE players ADD COLUMN control_scheme VARCHAR(10) DEFAULT 'arrows'",
                "ALTER TABLE players ADD COLUMN difficulty VARCHAR(10) DEFAULT 'normal'"
            ]
            for query in alter_queries:
                try:
                    cursor.execute(query)
                except Error as e:
                    # Ignore duplicate column errors (Error 1060: Duplicate column name)
                    pass


            print("Creating 'scores' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_id INT,
                    score INT NOT NULL,
                    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
                )
            """)
            
            connection.commit()
            print("\nDatabase setup complete successfully!")
            
    except Error as e:
        print(f"\nError while connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")

if __name__ == "__main__":
    setup_database()
