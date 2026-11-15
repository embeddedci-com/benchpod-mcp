@echo off
rem Windows twin of bin/benchpod-mcp, found through PATHEXT when the plugin's command
rem (${CLAUDE_PLUGIN_ROOT}/bin/benchpod-mcp in Claude Code, ./bin/benchpod-mcp in Codex) is started
rem on Windows. Starts the BenchPod MCP server
rem with uvx. Without uv on PATH it installs a private copy into the plugin's data folder first
rem (no admin rights, PATH untouched); uv then fetches its own Python.
rem stdout is the MCP stream: everything else goes to stderr.
rem SPEC is one exact embeddedci-mcp release per plugin release (bumped with bin/benchpod-mcp and
rem mcpb/pyproject.toml). The private uv is one pinned uv release, checked against its SHA-256.
setlocal
set "SPEC=embeddedci-mcp==2.13.18"
set "UV_VERSION=0.13.6"

rem The uv installer's folder may be missing from the PATH of an app started before uv was installed.
set "PATH=%PATH%;%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin"
where uvx >nul 2>nul
if errorlevel 1 goto private
uvx --from "%SPEC%" embeddedci-mcp
exit /b %errorlevel%

:private
set "DATA=%CLAUDE_PLUGIN_DATA%"
if not defined DATA set "DATA=%LOCALAPPDATA%\benchpod-mcp"
set "UV_DIR=%DATA%\uv"
if exist "%UV_DIR%\uvx.exe" goto run

rem The uv release archive for this machine and its SHA-256 (from the release's .sha256 files).
rem A 32-bit cmd on 64-bit Windows reports x86 and keeps the real one in PROCESSOR_ARCHITEW6432.
set "ARCH=%PROCESSOR_ARCHITEW6432%"
if not defined ARCH set "ARCH=%PROCESSOR_ARCHITECTURE%"
if /i "%ARCH%"=="AMD64" (
  set "UV_TARGET=x86_64-pc-windows-msvc"
  set "UV_SHA256=a2a8820d5eea32f08ef467ef3b7f66883a9b076d5737a2fc2fbb5f458d1bb50f"
) else if /i "%ARCH%"=="ARM64" (
  set "UV_TARGET=aarch64-pc-windows-msvc"
  set "UV_SHA256=c2426c0c8e28b53d8c440e47a18d96ad4db51e159866c0e81435b196d7f0081c"
) else (
  >&2 echo benchpod: uv not found on PATH and no private copy for %ARCH% Windows.
  goto failed
)
set "UV_URL=https://github.com/astral-sh/uv/releases/download/%UV_VERSION%/uv-%UV_TARGET%.zip"

>&2 echo benchpod: uv not found on PATH, installing uv %UV_VERSION% in "%UV_DIR%"
set "TMP_DIR=%UV_DIR%.tmp.%RANDOM%"
if exist "%TMP_DIR%" rmdir /s /q "%TMP_DIR%"
mkdir "%TMP_DIR%" || exit /b 1
rem Started from PowerShell 7, PSModulePath points at its modules, which Windows PowerShell cannot
rem load (Expand-Archive then fails). Unset, it rebuilds its own default.
set "PSModulePath="
rem Download, check the SHA-256 and only then unpack; a mismatch leaves nothing behind.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $zip = Join-Path $env:TMP_DIR 'uv.zip'; Invoke-WebRequest -UseBasicParsing -Uri $env:UV_URL -OutFile $zip; $got = (Get-FileHash -Algorithm SHA256 -LiteralPath $zip).Hash.ToLower(); if ($got -ne $env:UV_SHA256) { [Console]::Error.WriteLine('benchpod: ' + $env:UV_URL + ' has SHA-256 ' + $got + ', expected ' + $env:UV_SHA256 + '; not installing it'); exit 1 }; Expand-Archive -LiteralPath $zip -DestinationPath $env:TMP_DIR -Force; Remove-Item -LiteralPath $zip" 1>&2
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
