@echo off
set REQUESTS_CA_BUNDLE=Combined_pem.pem
goto:runVelociraptor

:runVelociraptor
ECHO Please enter your Jira token:
SET /p JIRA_TOKEN=
python\python.exe -m velociraptor.compare_sheet %*

cmd /k

