@echo off
REM ======================================================================
REM MCP Server Runner Script
REM This script runs the MCP server with a 30-second delay for debugging
REM ======================================================================

echo ===== STARTING MCP SERVER WITH 30 SECOND DELAY =====
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Write to startup log
echo Starting at %date% %time% > logs\mcp_startup.log
echo Computer: %COMPUTERNAME% >> logs\mcp_startup.log
echo Working directory: %CD% >> logs\mcp_startup.log

echo Waiting 30 seconds before launching server...
echo Press Ctrl+C to cancel if needed
echo.
timeout /t 30 /nobreak

echo.
echo Startup time after delay: %time% >> logs\mcp_startup.log
echo Setting environment variables... >> logs\mcp_startup.log

REM Set Python environment variables
set "PYTHONPATH=%CD%"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUNBUFFERED=1"
set "PATH=%PATH%;%CD%\.venv\Scripts"
set "VIRTUAL_ENV=%CD%\.venv"

REM Set MCP specific variables
set "MCP_SERVER_ROOT=%CD%"
set "MCP_TRANSPORT=stdio"
set "MCP_LOG_LEVEL=DEBUG"
set "MCP_LOGGING__FORMAT=text"
set "MCP_LOGGING__ENABLE_STDOUT=true"
set "MCP_LOGS_PATH=%CD%\logs"

REM Log environment variables
echo Environment variables set: >> logs\mcp_startup.log
set | findstr "PYTHON MCP_" >> logs\mcp_startup.log

REM Check Python executable
echo.
echo Checking Python executable... >> logs\mcp_startup.log
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Python executable not found at %CD%\.venv\Scripts\python.exe
    echo ERROR: Python executable not found >> logs\mcp_startup.log
    exit /b 1
)
echo Python executable found >> logs\mcp_startup.log

REM Print Python version
echo.
echo Running Python version test... >> logs\mcp_startup.log
.venv\Scripts\python.exe -c "import sys; print(f'Python {sys.version} on {sys.platform}')" > logs\mcp_stdout.log

REM Start the server
echo Starting server at %time% >> logs\mcp_startup.log
echo ===== LAUNCHING MCP SERVER =====
echo.

REM Run the server
.venv\Scripts\python.exe -m src.chemist_server 2> logs\mcp_stderr.log

REM Check exit code
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Server exited with code %ERRORLEVEL% at %time% >> logs\mcp_startup.log
    echo.
    echo ===== SERVER CRASHED WITH ERROR CODE %ERRORLEVEL% =====
    echo Check logs\mcp_stderr.log for details
    pause
    exit /b %ERRORLEVEL%
)

echo Server process ended at %time% >> logs\mcp_startup.log
echo.
echo ===== SERVER SHUT DOWN NORMALLY =====
pause