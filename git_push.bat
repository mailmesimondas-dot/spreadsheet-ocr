@echo off
title Push to GitHub for Android APK Build
echo ========================================================
echo       SPREADSHEET OCR - GITHUB DEPLOYMENT HELPER
echo ========================================================
echo.
echo This script will initialize a Git repository and push
echo the project to GitHub, triggering the cloud builder for
echo your Android .apk file.
echo.

:: Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed on this system!
    echo Please install Git from https://git-scm.com/ and try again.
    echo.
    pause
    exit /b 1
)

:: Prompt user for repository URL
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/username/repo-name.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] Repository URL cannot be empty!
    echo.
    pause
    exit /b 1
)

echo.
echo [STATUS] Initializing Local Git Repository...
git init

echo [STATUS] Staging files...
:: Add all files, excluding build cache/venv/large executables
echo node_modules/ > .gitignore
echo .venv/ >> .gitignore
echo venv/ >> .gitignore
echo *.exe >> .gitignore
echo *.xlsx >> .gitignore
echo *.png >> .gitignore
echo build/ >> .gitignore
echo dist/ >> .gitignore
echo .buildozer/ >> .gitignore
echo bin/ >> .gitignore
git add .

echo [STATUS] Creating first commit...
git commit -m "Initialize Spreadsheet OCR application and Android workflow"

echo [STATUS] Configuring remote repository...
git remote remove origin >nul 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo [STATUS] Pushing project to GitHub...
echo.
echo Note: If prompted, please authenticate with your GitHub credentials.
echo.
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to push code to GitHub! 
    echo Please verify your credentials, repository URL, and internet connection.
    echo.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Code successfully pushed to GitHub!
echo.

:: Extract repository URL details to open actions page
set ACTIONS_URL=%REPO_URL%
:: Strip the .git extension if present
set ACTIONS_URL=%ACTIONS_URL:.git=%
set ACTIONS_URL=%ACTIONS_URL%/actions

echo [STATUS] Opening GitHub Actions cloud compiler in your browser...
echo URL: %ACTIONS_URL%
start "" "%ACTIONS_URL%"

echo.
echo ========================================================
echo  Your APK is now building in the cloud!
echo  Please wait ~10 minutes, click the workflow run, 
echo  and download the APK from the "Artifacts" section.
echo ========================================================
echo.
pause
