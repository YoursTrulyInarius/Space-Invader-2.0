# Space Invaders
This is a **weekly commit project** where features and improvements are added incrementally each week.
aaaaa
## Latest Update — Arcade Combat & Wave Tuning

### 🎮 Classic Enemy Formation Movement
- Enemies now drift in a slower, more deliberate side-to-side sweep instead of feeling overly aggressive.
- The formation turns around with a cleaner rhythm at the screen edges, creating a more classic arcade flow.
- Enemy ships stay inside a controlled upper-middle play area and do not drop below the intended battle zone.
- Enemy spacing and staggered wave layout now read more like a traditional Space Invaders formation.

### 🔫 Hold-to-Fire Combat
- Holding the fire key now continuously shoots with a controlled cooldown instead of requiring repeated taps.
- Player bullets have been slowed down slightly for more readable, arcade-style pacing.
- Enemy bullets fire in a straight vertical line and remain within the intended playfield behavior.

### ❤️ Three-Heart Life System
- The player now starts with **3 hearts**.
- Each hit removes one heart, and the ship briefly blinks while invulnerable after damage.
- Once all hearts are lost, the game ends and the score flow continues into the leaderboard/database save flow.

### 🎨 HUD & Visual Polish
- The heart icon has been replaced with a cleaner custom-drawn shape instead of a red box/generic placeholder.
- Enemy ships are slightly smaller to improve readability and fit the arcade formation better.
<<<<<<< HEAD
- The background now uses a galaxy-inspired scene with soft nebula glow, cooler cosmic colors, and a subtle drifting space feel.
=======
- The background now uses a moving, glowing space scene with a starfield and soft nebula-like atmosphere.
>>>>>>> f1cd83b785ac44e46aabccd14d74ffcc5ec5258e
- The overall combat feel is smoother and more faithful to classic Space Invaders pacing.

### 🏆 Existing Systems Still Included
- Secure login and registration flow with password hashing.
- High-score leaderboard filtered to the best score per player.
- Persistent database-backed score saving and personal best tracking.
<<<<<<< HEAD
- Retro UI styling, glowing panels, and an animated galaxy backdrop.
=======
- Retro UI styling, glowing panels, and an animated space backdrop.
>>>>>>> f1cd83b785ac44e46aabccd14d74ffcc5ec5258e

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
