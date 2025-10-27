@echo off
setlocal enabledelayedexpansion

echo Telegram Gift Price Bot - Windows Setup
echo.

set SCRIPT_DIR=%~dp0
cd "%SCRIPT_DIR%"

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating new virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt

:: Install Tonnel Marketplace API
echo Installing Tonnel Marketplace API...
pip install tonnelmp

:: Check if we need to download images
if not exist "downloaded_images" (
    echo Downloading gift images...
    python main.py
) else (
    echo Gift images already downloaded
)

:: Pregenerate backgrounds if they don't exist
if not exist "pregenerated_backgrounds" (
    echo Generating background images...
    python pregenerate_backgrounds.py
) else (
    echo Backgrounds already generated
)

:: Run the card pre-generation script first to ensure we have all cards
echo Pre-generating gift cards...
python pregenerate_gift_cards.py

:: Store the pid file for the background process
set "PID_FILE=%SCRIPT_DIR%.pregeneration_pid"

:: Start the card pre-generation scheduler in the background
echo Starting card pre-generation scheduler...
start /b "" python run_card_pregeneration.py > pregeneration_scheduler.log 2>&1
set PREGENERATION_PID=%ERRORLEVEL%
echo !PREGENERATION_PID! > "%PID_FILE%"

:: Run the bot
echo Starting Telegram bot...
python telegram_bot.py

:: Script will continue after the bot stops or is interrupted
echo Bot has stopped.

:: Cleanup before exit
echo Cleaning up processes...

:: Check if pid file exists and kill the process
if exist "%PID_FILE%" (
    set /p PREGENERATION_PID=<"%PID_FILE%"
    taskkill /PID !PREGENERATION_PID! /F > nul 2>&1
    del "%PID_FILE%"
)

:: Deactivate virtual environment
deactivate

echo Cleanup complete 