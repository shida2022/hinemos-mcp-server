@echo off
REM Hinemos HTTP MCP Server Startup Script for Windows
REM 
REM このスクリプトを実行する前に以下を確認してください:
REM 1. Python 3.8+ がインストールされている
REM 2. pip install -r requirements.txt を実行済み
REM 3. 環境変数が設定されている (または下記で設定)

echo Starting Hinemos HTTP MCP Server...
echo.

REM 環境変数の設定 (必要に応じて変更)
set HINEMOS_BASE_URL=http://3.113.245.85:8080/HinemosWeb/api
set HINEMOS_USERNAME=hinemos
set HINEMOS_PASSWORD=hinemos
set HINEMOS_VERIFY_SSL=false

REM HTTP サーバ設定
set MCP_HTTP_HOST=127.0.0.1
set MCP_HTTP_PORT=8000

echo Configuration:
echo - Hinemos URL: %HINEMOS_BASE_URL%
echo - Username: %HINEMOS_USERNAME%
echo - SSL Verification: %HINEMOS_VERIFY_SSL%
echo - HTTP Server: http://%MCP_HTTP_HOST%:%MCP_HTTP_PORT%
echo.

echo Available endpoints after startup:
echo - Health Check: http://%MCP_HTTP_HOST%:%MCP_HTTP_PORT%/health
echo - Tools List:   http://%MCP_HTTP_HOST%:%MCP_HTTP_PORT%/tools
echo - Resources:    http://%MCP_HTTP_HOST%:%MCP_HTTP_PORT%/resources
echo.

REM HTTP MCPサーバを起動
python hinemos_http_server.py

pause