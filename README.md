# Space Invaders
This is a **weekly commit project** where features and improvements are added incrementally each week.

## Latest Update — Week 4

### 🔐 Secure Login & Registration Flow
- Added proper **Login** and **Registration** screens to authenticate players.
- Implemented secure password storage using SHA-256 hashing (built-in `hashlib` library).
- Enforced validation rules (username 3+ chars, password 4+ chars, and matching password confirmations).
- Supported auto-login directly after successful registration.

### 🏆 Interactive Leaderboard Screen
- Created a dedicated **Leaderboard Screen** displaying the top 10 all-time high scores.
- Renders a clean table with ranks, player names, scores, and dates.
- Features special gold, silver, and bronze highlights for top 3 positions.
- Highlights the currently logged-in user's entry in a green indicator strip.

### 💾 Live Database Score Saving
- Game scores are captured and written to the database **live** as soon as the blinking game-over sequence completes.
- Keeps track of and displays your **Personal Best** high score on the menu screen and during gameplay.

### 🎨 Visual Redesign & UI Polish
- **Twinkling Star-Field**: A moving background added to all menu screens for a space vibe.
- **Glassmorphic Glows**: Main headings now feature a soft, neon glow underneath the title text.
- **Focused States**: Input fields glow when active, and passwords display masked with circular `●` characters.
- **Floating Labels**: All-caps badges (e.g. `USERNAME`, `PASSWORD`, `DISPLAY NAME`) float cleanly above their respective inputs.
- **HUD Chips**: In-game HUD now encloses the current Score and personal Best inside distinct container boxes rather than floating raw text.

---

## Previous Updates

### Week 3 — Bug Fixes & Refinement
- **Ship Color Tinting**: Converted base image to grayscale at load time to allow correct color multiplication for all choices (Green, Blue, Red, Yellow, Purple).
- **Enemy Movement**: Enemies dive to player's current position instead of their position 60 frames ago.
- **Profile Screen Clean Up**: Hid unfinished difficulty selector and matched color swatches with actual ship colors.
- **Name Input Box**: Handled select-all (Ctrl+A), Ctrl+Backspace, and Ctrl+V copy-paste.

### Week 2 — Player Profiles & Leaderboards
- **Database Integration**: Saves your Space Invaders score to a local MySQL database!
- **Player Profiles**: Enter your username on the new start screen to track your scores. You can also rename your profile directly from the start screen!
- **In-Game Leaderboards**: At the end of every game, the top 5 highest scores are displayed on the Game Over screen.

## Database Schema

The game uses a local MySQL database named `space_invader_db` with the following schema:

```sql
CREATE TABLE IF NOT EXISTS players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(64) DEFAULT NULL,
    ship_color VARCHAR(20) DEFAULT 'green',
    player_title VARCHAR(50) DEFAULT 'Space Cadet',
    control_scheme VARCHAR(10) DEFAULT 'arrows',
    difficulty VARCHAR(10) DEFAULT 'normal',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT,
    score INT NOT NULL,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);
```

## Setup Instructions

Follow these step-by-step instructions to set up and run the game locally on your machine.

### 1. Create a Virtual Environment

It is recommended to use a virtual environment to manage dependencies. Open your terminal in the project root directory and run:

```bash
python -m venv .venv
```

### 2. Activate the Virtual Environment

Activate the newly created virtual environment. Since you are on Windows, use the following command in PowerShell or Command Prompt:

```bash
.\.venv\Scripts\activate
```

*(If you are using bash/Git Bash, use `source .venv/Scripts/activate`)*

### 3. Install Dependencies

With the virtual environment active, install the required packages using `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Setup the Database

Initialize and set up the local database by running the `database_setup.py` script:

```bash
python database_setup.py
```

### 5. Run the Game

Once everything is set up, you can start the game by executing the main script:

```bash
python main.py
```

Enjoy playing!
