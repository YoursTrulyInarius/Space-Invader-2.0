from managers.db_manager import DBManager

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

    # 5. Delete
    print("5. Deleting test player 'test_user_456'...")
    delete_success = db.delete_player("test_user_456")
    print(f"   -> Success: {delete_success}")
    assert delete_success, "Failed to delete player"

    print("\nAll DB CRUD tests passed successfully!")

if __name__ == "__main__":
    run_tests()
