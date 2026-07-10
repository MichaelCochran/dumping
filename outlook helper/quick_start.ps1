# Quick Start Script for Outlook Email Task Generator
Write-Host "Outlook Email Task Generator - Quick Start" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Choose mode:
1 - Kanban Board (visual task management)
2 - Monitor (real-time task generation)
3 - Process recent emails (on-demand)
4 - List generated tasks
Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`nLaunching Qt Kanban Board..." -ForegroundColor Green
        python kanban_board_qt.py
    }
    "2" {
        Write-Host "`nStarting monitor mode... Press Ctrl+C to stop" -ForegroundColor Green
        python email_task_generator.py monitor
    }
    "3" {
        $limit = Read-Host "How many recent emails to process? (default: 10)"
        if ([string]::IsNullOrWhiteSpace($limit)) { $limit = 10 }
        Write-Host "`nProcessing $limit recent emails..." -ForegroundColor Green
        python email_task_generator.py process --limit $limit
    }
    "4" {
        Write-Host "`nListing generated tasks..." -ForegroundColor Green
        python email_task_generator.py list
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
    }
}
