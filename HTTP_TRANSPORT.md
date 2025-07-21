# Hinemos MCP Server - HTTP Transport

## 概要

Hinemos MCP ServerはHTTP Transportをサポートしており、RESTful APIを通じてMCPツールにアクセスできます。

## 特徴

- **RESTful API**: 標準的なHTTP/JSONでMCPツールを呼び出し
- **FastAPI**: 高性能なPython Webフレームワークを使用
- **リアルタイム**: 同期的なHTTPリクエスト/レスポンス
- **ブラウザ対応**: Webブラウザから直接APIにアクセス可能
- **Swagger UI**: 自動生成されるAPI仕様書

## セットアップ

### 1. 依存関係のインストール

```bash
pip install fastapi uvicorn[standard]
# または
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
# Hinemos接続設定
export HINEMOS_BASE_URL=http://3.113.245.85:8080/HinemosWeb/api
export HINEMOS_USERNAME=hinemos
export HINEMOS_PASSWORD=hinemos
export HINEMOS_VERIFY_SSL=false

# HTTP サーバ設定 (オプション)
export MCP_HTTP_HOST=127.0.0.1
export MCP_HTTP_PORT=8000
```

### 3. サーバの起動

```bash
# 方法1: 専用スクリプト
python hinemos_http_server.py

# 方法2: バッチファイル (Windows)
start_http_server.bat

# 方法3: 直接起動
python -m src.hinemos_mcp.server.http_fastmcp_server
```

## API エンドポイント

### 基本情報

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/` | GET | サーバ情報 |
| `/health` | GET | ヘルスチェック |
| `/docs` | GET | Swagger UI (自動生成) |
| `/redoc` | GET | ReDoc API仕様書 |

### MCP Tools

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/tools` | GET | 利用可能なツール一覧 |
| `/tools/{tool_name}` | POST | 特定のツール実行 |

### MCP Resources

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/resources` | GET | 利用可能なリソース一覧 |
| `/resources/{resource_name}` | GET | 特定のリソース取得 |

## 使用例

### 1. ヘルスチェック

```bash
curl http://127.0.0.1:8000/health
```

```json
{
  "status": "healthy",
  "hinemos_connection": "ok",
  "timestamp": "2025-07-21T20:00:00"
}
```

### 2. ツール一覧の取得

```bash
curl http://127.0.0.1:8000/tools
```

```json
{
  "tools": [
    {
      "name": "hinemos_get_facility_tree",
      "description": "Get complete facility tree showing hierarchy and relationships.",
      "endpoint": "/tools/hinemos_get_facility_tree"
    },
    {
      "name": "hinemos_create_monitor",
      "description": "Create a new monitor configuration.",
      "endpoint": "/tools/hinemos_create_monitor"
    }
  ]
}
```

### 3. ポート監視の作成

```bash
curl -X POST http://127.0.0.1:8000/tools/hinemos_create_monitor \
  -H "Content-Type: application/json" \
  -d '{
    "monitor_type": "port",
    "monitor_id": "PORT_8080_AP1",
    "facility_id": "AP1",
    "description": "AP1ノードのポート8080監視",
    "port_no": 8080,
    "service_id": "TCP",
    "timeout": 5000,
    "run_interval": "MIN_05"
  }'
```

```json
{
  "tool": "hinemos_create_monitor",
  "status": "success",
  "result": "{\"status\": \"created\", \"monitor_id\": \"PORT_8080_AP1\", \"monitor_type\": \"port\", \"description\": \"AP1ノードのポート8080監視\"}"
}
```

### 4. ファシリティツリーの取得

```bash
curl http://127.0.0.1:8000/resources/hinemos___repository_facility_tree
```

### 5. ノード情報の取得

```bash
curl -X POST http://127.0.0.1:8000/tools/hinemos_get_repository_node \
  -H "Content-Type: application/json" \
  -d '{"facility_id": "AP1"}'
```

## 利用可能なMCPツール

### リポジトリ管理
- `hinemos_get_facility_tree` - ファシリティツリー取得
- `hinemos_get_repository_node` - ノード情報取得
- `hinemos_create_repository_node` - ノード作成
- `hinemos_update_repository_node` - ノード更新

### 監視設定
- `hinemos_get_monitor` - 監視設定取得
- `hinemos_create_monitor` - 統合監視作成 (11種類対応)

### スコープ管理
- `hinemos_create_scope` - スコープ作成
- `hinemos_assign_nodes_to_scope` - ノードをスコープに割り当て
- `hinemos_remove_nodes_from_scope` - スコープからノードを削除

## 設定オプション

### 環境変数

| 変数名 | デフォルト値 | 説明 |
|---|---|---|
| `HINEMOS_BASE_URL` | `http://localhost:8080/HinemosWeb/api` | Hinemos REST API URL |
| `HINEMOS_USERNAME` | `hinemos` | Hinemosユーザ名 |
| `HINEMOS_PASSWORD` | `hinemos` | Hinemosパスワード |
| `HINEMOS_VERIFY_SSL` | `true` | SSL証明書検証 |
| `MCP_HTTP_HOST` | `127.0.0.1` | HTTPサーバのホスト |
| `MCP_HTTP_PORT` | `8000` | HTTPサーバのポート |

## トラブルシューティング

### 1. サーバが起動しない

```bash
# ポートの使用状況を確認
netstat -an | grep :8000

# 別のポートを使用
export MCP_HTTP_PORT=8001
python hinemos_http_server.py
```

### 2. Hinemos接続エラー

```bash
# ヘルスチェックでエラー詳細を確認
curl http://127.0.0.1:8000/health
```

### 3. 依存関係エラー

```bash
# 依存関係を再インストール
pip install --upgrade -r requirements.txt
```

## 開発・テスト

### Swagger UI

サーバ起動後、ブラウザで以下にアクセス:
```
http://127.0.0.1:8000/docs
```

### API 仕様書 (ReDoc)

```
http://127.0.0.1:8000/redoc
```

### JSON Schema

```bash
curl http://127.0.0.1:8000/openapi.json
```

## パフォーマンス

- **並行処理**: FastAPIの非同期処理により高い並行性
- **レスポンス時間**: 通常10-100ms (Hinemos APIの応答時間に依存)
- **スループット**: 100-1000 requests/second (ハードウェアに依存)

## セキュリティ

- **認証**: 環境変数による基本認証
- **HTTPS**: 本番環境ではリバースプロキシ (nginx等) の使用を推奨
- **CORS**: 必要に応じてCORS設定を追加可能

## STDIOとHTTPの比較

| 項目 | STDIO Transport | HTTP Transport |
|---|---|---|
| **プロトコル** | 標準入出力 | HTTP/JSON |
| **用途** | CLI、エディタ統合 | Web API、ブラウザ |
| **パフォーマンス** | 高速 | 中程度 |
| **デバッグ** | 困難 | 容易 (ブラウザ、curl) |
| **スケーラビリティ** | 低 | 高 |
| **セットアップ** | 簡単 | 中程度 |