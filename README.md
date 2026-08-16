# Space Invaders

This is a **weekly commit project** where features and improvements are added incrementally each week.

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
.venv\scripts\activate
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
