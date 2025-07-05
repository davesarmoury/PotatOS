@echo off
echo 🤖 Starting PotatOS Ollama Server...

REM Get IP address
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%i
    goto :found
)
:found
set IP=%IP:~1%

echo 📡 Server IP address: %IP%

REM Check port
set PORT=11434
netstat -an | findstr ":%PORT% " >nul
if %errorlevel% equ 0 (
    echo ⚠️  Port %PORT% already in use!
    echo Stopping existing Ollama process...
    taskkill /f /im ollama.exe 2>nul
    timeout /t 2 >nul
)

REM Check model
set MODEL=llama3.2:3b
echo 🔍 Model check: %MODEL%
ollama list | findstr "%MODEL%" >nul
if %errorlevel% neq 0 (
    echo 📥 Downloading model: %MODEL%
    ollama pull "%MODEL%"
) else (
    echo ✅ Model available: %MODEL%
)

REM Set environment variable for network access
set OLLAMA_HOST=0.0.0.0

echo 🚀 Starting Ollama server...
echo 📍 Access URL: http://%IP%:%PORT%
echo ⏹️  Use Ctrl+C to stop
echo.

REM Start server
ollama serve

pause
