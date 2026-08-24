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

    def update_player_username(self, old_username, new_username):
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE players SET username = %s WHERE username = %s", (new_username, old_username))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error updating player username: {e}")
            return False
        finally:
            self.close()

    def get_player_profile(self, username):
        if not self.connect():
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM players WHERE username = %s", (username,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error retrieving player profile: {e}")
            return None
        finally:
            self.close()

    def update_player_profile(self, username, ship_color=None, player_title=None, control_scheme=None, difficulty=None):
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            
            updates = []
            params = []
            
            if ship_color:
                updates.append("ship_color = %s")
                params.append(ship_color)
            if player_title:
                updates.append("player_title = %s")
                params.append(player_title)
            if control_scheme:
                updates.append("control_scheme = %s")
                params.append(control_scheme)
            if difficulty:
                updates.append("difficulty = %s")
                params.append(difficulty)
                
            if not updates:
                return True
                
            params.append(username)
            query = f"UPDATE players SET {', '.join(updates)} WHERE username = %s"
            
            cursor.execute(query, tuple(params))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error updating player profile: {e}")
            return False
        finally:
            self.close()

    def delete_player(self, username):
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM players WHERE username = %s", (username,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting player: {e}")
            return False
        finally:
            self.close()

if __name__ == "__main__":
    def run_tests():
        print("Testing DB CRUD operations...")
        db = DBManager(user="root", password="")
        
        # 1. Create / Read (get_or_create_player)
        print("1. Creating test player 'test_user_123'...")
        player_id = db.get_or_create_player("test_user_123")
        print(f"   -> Player ID: {player_id}")
        assert player_id is not None, "Failed to create player"

        # 2. Create Score
        print("2. Saving score (100) for 'test_user_123'...")
        success = db.save_score("test_user_123", 100)
        print(f"   -> Success: {success}")
        assert success, "Failed to save score"

        # 3. Read Leaderboard
        print("3. Reading top scores...")
        scores = db.get_top_scores(limit=10)
        print(f"   -> Top Scores: {scores}")
        assert len(scores) > 0, "No scores found"

        # 4. Update
        print("4. Updating username from 'test_user_123' to 'test_user_456'...")
        update_success = db.update_player_username("test_user_123", "test_user_456")
        print(f"   -> Success: {update_success}")
        assert update_success, "Failed to update username"

        # 4b. Update Profile
        print("4b. Updating profile for 'test_user_456'...")
        profile_success = db.update_player_profile(
            "test_user_456", 
            ship_color="blue", 
            player_title="Galactic Hero",
            control_scheme="wasd",
            difficulty="hard"
        )
        print(f"   -> Success: {profile_success}")
        assert profile_success, "Failed to update profile data"
        
        # 4c. Verify Profile Update
        print("4c. Reading profile for 'test_user_456'...")
        profile = db.get_player_profile("test_user_456")
        print(f"   -> Profile Data: {profile}")
        assert profile['ship_color'] == 'blue', "Ship color didn't update"
        assert profile['difficulty'] == 'hard', "Difficulty didn't update"

        # 5. Delete
        print("5. Deleting test player 'test_user_456'...")
        delete_success = db.delete_player("test_user_456")
        print(f"   -> Success: {delete_success}")
        assert delete_success, "Failed to delete player"

        print("\nAll DB CRUD tests passed successfully!")

    run_tests()
