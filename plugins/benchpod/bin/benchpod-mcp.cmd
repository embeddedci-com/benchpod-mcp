@echo off
rem Windows twin of bin/benchpod-mcp, found through PATHEXT when the plugin's command
rem ${CLAUDE_PLUGIN_ROOT}/bin/benchpod-mcp is started on Windows. Starts the BenchPod MCP server
rem with uvx. Without uv on PATH it installs a private copy into the plugin's data folder first
rem (no admin rights, PATH untouched); uv then fetches its own Python.
rem stdout is the MCP stream: everything else goes to stderr.
setlocal
set "SPEC=embeddedci-mcp>=2.2,<3"

where uvx >nul 2>nul
if errorlevel 1 goto private
uvx --from "%SPEC%" embeddedci-mcp
exit /b %errorlevel%

:private
set "DATA=%CLAUDE_PLUGIN_DATA%"
if not defined DATA set "DATA=%LOCALAPPDATA%\benchpod-mcp"
set "UV_DIR=%DATA%\uv"
if exist "%UV_DIR%\uvx.exe" goto run

>&2 echo benchpod: uv not found on PATH, installing a private copy in "%UV_DIR%"
set "TMP_DIR=%UV_DIR%.tmp.%RANDOM%"
if exist "%TMP_DIR%" rmdir /s /q "%TMP_DIR%"
mkdir "%TMP_DIR%" || exit /b 1
powershell -NoProfile -ExecutionPolicy Bypass -Command "$env:UV_UNMANAGED_INSTALL = $env:TMP_DIR; irm https://astral.sh/uv/install.ps1 | iex" 1>&2
if not exist "%TMP_DIR%\uvx.exe" goto failed
rem Another session may have finished first; either copy works.
if exist "%UV_DIR%\uvx.exe" (rmdir /s /q "%TMP_DIR%") else (move "%TMP_DIR%" "%UV_DIR%" >nul)
goto run

:failed
if exist "%TMP_DIR%" rmdir /s /q "%TMP_DIR%"
>&2 echo benchpod: could not install uv. Install it yourself: https://docs.astral.sh/uv/getting-started/installation/
exit /b 1

:run
"%UV_DIR%\uvx.exe" --from "%SPEC%" embeddedci-mcp
exit /b %errorlevel%
