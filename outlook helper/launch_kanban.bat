@echo off
title Outlook Email Task Kanban Board
color 0A

echo.
echo ========================================
echo   Outlook Email Task Kanban Board
echo ========================================
echo.
echo Starting Qt Kanban Board...
echo.

python kanban_board_qt.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to launch Kanban board
    echo.
    echo Make sure:
    echo - Python is installed
    echo - Dependencies are installed: pip install -r requirements.txt
    echo - Outlook is running
    echo.
    pause
)
