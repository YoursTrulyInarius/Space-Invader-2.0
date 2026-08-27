# Space Invaders
aa
This is a **weekly commit project** where features and improvements are added incrementally each week.

## Latest Update — Week 3

### 🎨 Ship Color Tinting (Fixed)
- Ship colors (Green, Blue, Red, Yellow, Purple) now display correctly for all choices.
- **Root cause:** The original `myship.png` asset is red-tinted, so multiplying by non-red colors zeroed out those channels and produced a dark/invisible ship.
- **Fix:** The base image is now converted to luminance-correct **grayscale** once at load time, then `BLEND_RGB_MULT` is applied with the chosen color. Grayscale × any color = correct hue at full brightness, with the original alpha/transparency preserved perfectly.
- Grayscale brightness is boosted by ×1.9 before tinting so all color swatches appear vivid and clear.

### 🚀 Enemy Movement (Fixed)
- Enemies now correctly dive toward the **player's current position** instead of their position from 60 frames ago.
- Enemy off-screen detection now uses actual screen dimensions instead of hardcoded pixel values, preventing enemies from lingering outside the visible area.

### 🧩 Player Profile Screen (Cleaned Up)
- The **Difficulty row** has been temporarily removed from the Profile screen until difficulty logic is fully implemented.
- Color swatches in the profile UI now match the actual in-game ship tint colors exactly.

### ⌨️ Name Bar Input Fixes
- **Ctrl+A** now acts as "select all" — the next key typed replaces the entire name instantly.
- **Ctrl+A → Backspace** correctly clears the entire name field (previously only worked with a second Ctrl press).
- **Ctrl+Backspace** clears the full name in one keystroke.
- **Ctrl+V** pastes text from the clipboard directly into the name field.

---

## Previous Updates

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
