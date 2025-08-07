@echo off
CHCP 65001 >nul
ECHO =====================================
ECHO  GitHub Professional Update Helper
ECHO =====================================
ECHO.

REM ব্যবহারকারীর কাছ থেকে কমিট বার্তা নেওয়া হচ্ছে
SET /p commit_message="Enter your commit message: "

REM যদি ব্যবহারকারী কোনো বার্তা না দেয়
IF "%commit_message%"=="" (
    ECHO.
    ECHO ❌ Error: Commit message cannot be empty.
    ECHO Update Canceled.
    pause
    exit
)

ECHO.
ECHO 🔄 Updating with message: "%commit_message%"
ECHO.

SET GIT_BASH="C:\Program Files\Git\bin\bash.exe"

REM update-pro.sh কে বার্তা সহ চালানো হচ্ছে
%GIT_BASH% -c "./update-pro.sh '%commit_message%'"

ECHO.
ECHO =====================================
ECHO  Update finished. Press key to exit.
ECHO =====================================
pause >nul