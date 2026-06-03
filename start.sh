#!/bin/bash
cd "$(dirname "$0")"

echo "========================================"
echo " PollPoint - Start Script (macOS/Linux)"
echo "========================================"
echo ""

# 1. Check Python
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "ERROR: Python is not installed."
    exit 1
fi

# 2. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[1/5] Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment."
        exit 1
    fi
else
    echo "[1/5] Virtual environment found."
fi

# Activate venv
source .venv/bin/activate

# 3. Install Dependencies
if ! python -c "import flask, flask_sqlalchemy" &>/dev/null; then
    echo "[2/5] Installing dependencies..."
    python -m pip install --upgrade pip >/dev/null
    python -m pip install -r server/requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies."
        exit 1
    fi
else
    echo "[2/5] Dependencies are already installed."
fi

# 4. Check PostgreSQL and create database
echo "[3/6] Checking PostgreSQL..."

# Check if psql exists
if ! command -v psql &>/dev/null; then
    echo "========================================================"
    echo " ERROR: PostgreSQL is not installed."
    echo ""
    echo " Please install PostgreSQL:"
    echo "  macOS:   brew install postgresql && brew services start postgresql"
    echo "  Ubuntu:  sudo apt update && sudo apt install postgresql"
    echo "  Then run this script again."
    echo "========================================================"
    exit 1
fi

# Check if database exists, create if not
echo "Checking database 'pollpoint'..."
if ! psql -U $(whoami) -d postgres -c "SELECT 1 FROM pg_database WHERE datname='pollpoint';" &>/dev/null; then
    echo "Creating database 'pollpoint'..."
    createdb pollpoint || createdb -U postgres pollpoint
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create database."
        echo "Run: createdb pollpoint"
        exit 1
    fi
    echo "Database created."
else
    echo "Database already exists."
fi

# 5. Environment Variables
if [ ! -f "server/.env" ]; then
    echo "[4/6] Creating server/.env from example..."
    cp server/.env.example server/.env
    echo "========================================================"
    echo " WARNING: server/.env created."
    echo " Please open server/.env and set your PGPASSWORD."
    echo " Press [ENTER] when ready to continue..."
    echo "========================================================"
    read -r
else
    echo "[4/6] Environment file found."
fi

# 6. Database Setup
while true; do
    echo "[5/6] Checking database connection..."
    if python -m server.check_db; then
        break
    else
        echo "========================================================"
        echo " ERROR: Database connection failed."
        echo " 1. Make sure PostgreSQL is running."
        echo " 2. Check your PGPASSWORD in server/.env."
        echo " Press [ENTER] to try again, or Ctrl+C to exit."
        echo "========================================================"
        read -r
    fi
done

echo "Initializing database tables and test users..."
python -m server.init_db >/dev/null 2>&1
python -m server.seed >/dev/null 2>&1

# 7. Start Server
echo ""
echo "[6/6] Setup complete!"
echo "========================================"
echo " Starting PollPoint Server..."
echo " URL: http://localhost:5001"
echo " Stop with Ctrl+C"
echo "========================================"
python -m server.run
