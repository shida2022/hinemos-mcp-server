@echo off
REM Hinemos FastMCP Server Startup Script for Windows
REM 
REM このスクリプトを実行する前に以下を確認してください:
REM 1. Python 3.8+ がインストールされている
REM 2. pip install -r requirements.txt を実行済み
REM 3. 環境変数が設定されている (または下記で設定)

echo Starting Hinemos FastMCP Server...
echo.

REM 環境変数の設定 (必要に応じて変更)
set HINEMOS_BASE_URL=http://3.113.245.85:8080/HinemosWeb/api
set HINEMOS_USERNAME=hinemos
set HINEMOS_PASSWORD=hinemos
set HINEMOS_VERIFY_SSL=false

echo Configuration:
echo - Hinemos URL: %HINEMOS_BASE_URL%
echo - Username: %HINEMOS_USERNAME%
echo - SSL Verification: %HINEMOS_VERIFY_SSL%
echo.

REM FastMCPサーバを起動
python hinemos_fastmcp_server.py

pause