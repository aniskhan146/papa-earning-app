@echo off
ECHO =======================================
ECHO  Starting GitHub Update Process...
ECHO =======================================

REM এটি আপনার কম্পিউটারে থাকা Git Bash এর লোকেশন।
REM সাধারণত এটি ঠিকই থাকে। যদি কাজ না করে, আপনার Git এর লোকেশন খুঁজে এখানে দিন।
SET GIT_BASH="C:\Program Files\Git\bin\bash.exe"

REM বর্তমান ডিরেক্টরি থেকে update.sh স্ক্রিপ্টটি চালানো হচ্ছে।
%GIT_BASH% -c "./update.sh"

ECHO.
ECHO =======================================
ECHO  Update process finished.
ECHO  Press any key to exit.
ECHO =======================================

REM ব্যবহারকারীকে আউটপুট দেখার সুযোগ দেওয়ার জন্য টার্মিনালটি খোলা রাখে।
pause >nul