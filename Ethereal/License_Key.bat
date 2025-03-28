@echo off
setlocal enabledelayedexpansion
title License Key Generator (24-Hour Expiry)
color 0A && cls

:: Create License folder if it doesn't exist
if not exist "License" mkdir License

:: Check for existing valid license
if exist "License\expiration_time.txt" (
    for /f "tokens=*" %%t in (License\expiration_time.txt) do set "expiry_time=%%t"
    set "now=%date:~6,4%%date:~3,2%%date:~0,2%%time:~0,2%%time:~3,2%"
    set "now=!now: =0!"
    
    if "!expiry_time!" gtr "!now!" (
        echo.
        echo [ERROR] Valid license already exists
        echo Expires at: !expiry_time:~0,4!-!expiry_time:~4,2!-!expiry_time:~6,2! !expiry_time:~8,2!:!expiry_time:~10,2!
        echo.
        echo To generate new key:
        echo 1. Wait for current license to expire OR
        echo 2. Delete License\license_key.txt and License\expiration_time.txt
        echo.
        pause
        exit /b
    )
)

:: Character sets
set "letters=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
set "numbers=0123456789"
set "mix=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

:: Generate key (ET-XXXX-XXXX-XXXX format)
set "key=ET-"

:: Generate 4 random letters
for /L %%i in (1,1,4) do (
    set /a "rand=!random! %% 26"
    for %%j in (!rand!) do set "key=!key!!letters:~%%j,1!"
)

set "key=!key!-"

:: Generate 4 random digits
for /L %%i in (1,1,4) do (
    set /a "rand=!random! %% 10"
    for %%j in (!rand!) do set "key=!key!!numbers:~%%j,1!"
)

set "key=!key!-"

:: Generate 4 random alphanumeric
for /L %%i in (1,1,4) do (
    set /a "rand=!random! %% 36"
    for %%j in (!rand!) do set "key=!key!!mix:~%%j,1!"
)

:: Calculate expiry time (24 hours later - precise calculation)
for /f "tokens=2 delims==" %%A in ('wmic os get localdatetime /value ^| find "="') do set "datetime=%%A"
set "year=!datetime:~0,4!"
set "month=!datetime:~4,2!"
set "day=!datetime:~6,2!"
set "hour=!datetime:~8,2!"
set "minute=!datetime:~10,2!"

:: Create proper timestamp and add 24 hours
set "current_time=!year!-!month!-!day! !hour!:!minute!"
powershell -command "$date = [datetime]::ParseExact('!current_time!', 'yyyy-MM-dd HH:mm', $null); $expiry = $date.AddHours(24); $expiry.ToString('yyyyMMddHHmm')" > License\expiration_time.txt

:: Save key
echo !key!>License\license_key.txt

:: Display
echo.
echo [SUCCESS] Key generated:
echo !key!
echo Expires at: !year!-!month!-!day! !hour!:!minute! (24 hours from now)
echo Saved in License folder
echo.
pause