@echo off
set REQUESTS_CA_BUNDLE=%cd%\Combined_pem.pem

:runVelociraptor
IF NOT DEFINED JIRA_TOKEN (
    ECHO Please enter your Jira token:
    SET /p JIRA_TOKEN=
)

set "path=.\python;%path%"

echo.
python.exe -m velociraptor.compare_sheet %*
echo.

cmd /k
