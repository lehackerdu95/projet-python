@echo off
REM Setup script for Windows

echo 🚀 Setting up Collections Manager...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed
    exit /b 1
)

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo ✅ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Copy .env file
if not exist .env (
    echo 📝 Creating .env file...
    copy .env.example .env
    echo ⚠️  Don't forget to update SECRET_KEY in .env!
)

echo.
echo ✨ Setup complete!
echo.
echo Next steps:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Update SECRET_KEY in .env
echo 3. Run migrations: python manage.py migrate
echo 4. Create admin: python manage.py createsuperuser
echo 5. Run server: python manage.py runserver
