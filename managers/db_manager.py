import mysql.connector
from mysql.connector import Error

class DBManager:
    def __init__(self, host="localhost", user="root", password="", database="space_invader_db"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return False
        return False

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def get_or_create_player(self, username):
        if not self.connect():
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Check if player exists
            cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
            player = cursor.fetchone()
            
            if player:
                return player['id']
            
            # Create player if not exists
            cursor.execute("INSERT INTO players (username) VALUES (%s)", (username,))
            self.connection.commit()
            return cursor.lastrowid
            
        except Error as e:
            print(f"Error getting/creating player: {e}")
            return None
        finally:
            self.close()

    def save_score(self, username, score):
        player_id = self.get_or_create_player(username)
        if not player_id:
            return False

        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO scores (player_id, score) VALUES (%s, %s)", (player_id, score))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error saving score: {e}")
            return False
        finally:
            self.close()

    def get_top_scores(self, limit=5):
        if not self.connect():
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT p.username, s.score, s.achieved_at 
                FROM scores s
                JOIN players p ON s.player_id = p.id
                ORDER BY s.score DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error retrieving top scores: {e}")
            return []
        finally:
            self.close()
