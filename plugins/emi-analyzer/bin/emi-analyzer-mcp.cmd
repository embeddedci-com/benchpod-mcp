@echo off
rem Windows twin of bin/emi-analyzer-mcp, found through PATHEXT when the plugin's command is
rem started on Windows. Runs `emi-local mcp` from the installed EMI Analyzer app.
rem stdout is the MCP stream: everything else goes to stderr.
setlocal
set "MIN_VERSION=0.4.0"

if defined EMI_LOCAL call :try "%EMI_LOCAL%"
for /f "delims=" %%p in ('where emi-local 2^>nul') do call :try "%%p"
call :try "%LOCALAPPDATA%\Programs\EMI Analyzer\emi-local.exe"
call :try "%ProgramFiles%\EMI Analyzer\emi-local.exe"

>&2 echo emi-analyzer: the EMI Analyzer app was not found. Install EMI Analyzer %MIN_VERSION% or newer ^(it needs Docker^): https://github.com/embeddedci-com/emi-analyzer#readme. Installed somewhere else? Set the plugin's emi_local option to its emi-local.exe.
exit /b 1

:try
if not exist "%~1" exit /b 1
set "VERSION="
for /f "delims=" %%v in ('"%~1" -version 2^>nul') do if not defined VERSION set "VERSION=%%v"
if "%VERSION%"=="dev" goto run
powershell -NoProfile -Command "if ([version]'%VERSION%' -ge [version]'%MIN_VERSION%') { exit 0 } else { exit 1 }" >nul 2>nul
if errorlevel 1 (
  >&2 echo emi-analyzer: %~1 is version %VERSION%; the MCP server needs %MIN_VERSION% or newer.
  exit /b 1
)
:run
"%~1" mcp
exit %errorlevel%
