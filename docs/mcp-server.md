# Hinemos MCP Server Documentation

## 概要

Hinemos MCP Server は、[Model Context Protocol (MCP)](https://spec.modelcontextprotocol.io/) を実装したサーバーです。Claude などの AI アシスタントから Hinemos の機能にアクセスできるようになります。

## 特徴

- **統一されたインターface**: リポジトリ管理と監視設定を一つのサーバーで提供
- **リソース**: Hinemos の各種データをリソースとして公開
- **ツール**: 各種操作をツールとして提供
- **環境変数による設定**: セキュアな認証情報の管理

## アーキテクチャ

```
Claude AI Assistant
       ↓ (MCP Protocol)
   MCP Server
       ↓ (REST API)
   Hinemos Manager
```

## インストールと設定

### 1. 必要な依存関係のインストール

```bash
pip install mcp
```

### 2. 環境変数の設定

```bash
export HINEMOS_BASE_URL="http://your-hinemos-server:8080/HinemosWeb/api"
export HINEMOS_USERNAME="your-username" 
export HINEMOS_PASSWORD="your-password"
export HINEMOS_VERIFY_SSL="false"  # 必要に応じて
```

### 3. MCP設定ファイル（Claude用）

`mcp_config.json`:
```json
{
  "mcpServers": {
    "hinemos": {
      "command": "python3",
      "args": ["hinemos_mcp_server.py"],
      "env": {
        "HINEMOS_BASE_URL": "http://your-hinemos-server:8080/HinemosWeb/api",
        "HINEMOS_USERNAME": "your-username",
        "HINEMOS_PASSWORD": "your-password", 
        "HINEMOS_VERIFY_SSL": "false"
      }
    }
  }
}
```

## サーバーの起動

```bash
python3 hinemos_mcp_server.py
```

## 提供されるリソース

### 1. `hinemos://repository/nodes`
- **説明**: リポジトリ内の全ノード一覧
- **形式**: JSON配列
- **内容**: facility_id, facility_name, description, ip_address, platform_family等

### 2. `hinemos://repository/scopes` 
- **説明**: リポジトリ内の全スコープ一覧
- **形式**: JSON配列
- **内容**: facility_id, facility_name, description, facility_type等

### 3. `hinemos://monitor/settings`
- **説明**: 全監視設定一覧
- **形式**: JSON配列
- **内容**: monitor_id, monitor_type, description, facility_id等

## 提供されるツール

### リポジトリ管理ツール

#### `hinemos_get_repository_node`
**説明**: 指定されたノードの詳細情報を取得

**パラメータ**:
- `facility_id` (必須): 取得するノードのファシリティID

**使用例**:
```json
{
  "facility_id": "WEB1"
}
```

#### `hinemos_create_repository_node`
**説明**: 新しいノードを作成

**パラメータ**:
- `facility_id` (必須): 新しいノードのファシリティID
- `facility_name` (必須): ノードの表示名
- `ip_address` (必須): ノードのIPアドレス
- `description` (オプション): ノードの説明
- `platform_family` (オプション): プラットフォームファミリー
- `sub_platform_family` (オプション): サブプラットフォームファミリー

**使用例**:
```json
{
  "facility_id": "WEB_SERVER_01",
  "facility_name": "Web Server 01",
  "ip_address": "192.168.1.100",
  "description": "Production web server",
  "platform_family": "LINUX"
}
```

#### `hinemos_update_repository_node`
**説明**: 既存ノードの情報を更新

**パラメータ**:
- `facility_id` (必須): 更新するノードのファシリティID
- `facility_name` (オプション): 新しい表示名
- `description` (オプション): 新しい説明
- `ip_address` (オプション): 新しいIPアドレス

**使用例**:
```json
{
  "facility_id": "WEB_SERVER_01",
  "description": "Updated production web server",
  "ip_address": "192.168.1.101"
}
```

### 監視管理ツール

#### `hinemos_get_monitor`
**説明**: 指定された監視設定の詳細情報を取得

**パラメータ**:
- `monitor_id` (必須): 取得する監視設定のID

**使用例**:
```json
{
  "monitor_id": "PING_MONITOR_01"
}
```

#### `hinemos_create_monitor`
**説明**: 新しい監視設定を作成（統一インターフェース）

**パラメータ**:
- `monitor_type` (必須): 監視タイプ (`ping`, `http_numeric`, `http_string`, `snmp`, `logfile`)
- `monitor_id` (必須): 監視設定ID
- `facility_id` (必須): 監視対象のファシリティID
- `description` (オプション): 監視設定の説明
- `run_interval` (オプション): 監視間隔 (デフォルト: `MIN_05`)

**監視タイプ別パラメータ**:

##### Ping監視 (`monitor_type: "ping"`)
- `run_count` (オプション): ping実行回数 (デフォルト: 3)
- `timeout` (オプション): タイムアウト時間(ms) (デフォルト: 5000)

**使用例**:
```json
{
  "monitor_type": "ping",
  "monitor_id": "PING_WEB01",
  "facility_id": "WEB1",
  "description": "Web server ping monitoring",
  "run_count": 5,
  "timeout": 3000
}
```

##### HTTP数値監視 (`monitor_type: "http_numeric"`)
- `url` (必須): 監視対象URL
- `timeout` (オプション): タイムアウト時間(ms) (デフォルト: 10000)

**使用例**:
```json
{
  "monitor_type": "http_numeric",
  "monitor_id": "HTTP_RESPONSE_TIME",
  "facility_id": "WEB1", 
  "url": "http://web1.example.com/health",
  "description": "Web server response time monitoring"
}
```

##### HTTP文字列監視 (`monitor_type: "http_string"`)
- `url` (必須): 監視対象URL
- `patterns` (オプション): 検索パターンの配列
- `timeout` (オプション): タイムアウト時間(ms) (デフォルト: 10000)

**使用例**:
```json
{
  "monitor_type": "http_string",
  "monitor_id": "HTTP_STRING_CHECK",
  "facility_id": "WEB1",
  "url": "http://web1.example.com/status",
  "patterns": [
    {
      "pattern": ".*OK.*",
      "priority": "INFO",
      "message": "Service is OK"
    },
    {
      "pattern": ".*ERROR.*", 
      "priority": "CRITICAL",
      "message": "Service error detected"
    }
  ]
}
```

##### SNMP監視 (`monitor_type: "snmp"`)
- `oid` (必須): 監視対象のOID
- `convert_flg` (オプション): 変換フラグ (`NONE`, `DELTA`) (デフォルト: `NONE`)

**使用例**:
```json
{
  "monitor_type": "snmp",
  "monitor_id": "SNMP_CPU_USAGE",
  "facility_id": "SERVER01",
  "oid": "1.3.6.1.2.1.25.3.3.1.2.1",
  "description": "CPU usage monitoring"
}
```

##### ログファイル監視 (`monitor_type: "logfile"`)
- `directory` (必須): ログファイルディレクトリ
- `filename` (必須): ログファイル名パターン
- `patterns` (オプション): 検索パターンの配列
- `encoding` (オプション): ファイルエンコーディング (デフォルト: `UTF-8`)

**使用例**:
```json
{
  "monitor_type": "logfile",
  "monitor_id": "LOG_ERROR_CHECK",
  "facility_id": "APP01",
  "directory": "/var/log/application",
  "filename": "app.log",
  "patterns": [
    {
      "pattern": ".*ERROR.*",
      "priority": "CRITICAL", 
      "message": "Application error detected"
    }
  ]
}
```

## Claude での使用例

### 1. リソースの参照
```
Hinemosのノード一覧を見せてください
```

### 2. ノードの作成
```
新しいWebサーバー（192.168.1.200）をリポジトリに追加してください
```

### 3. 監視設定の作成
```
WEB1サーバーに対してpingの監視を設定してください
```

### 4. 既存設定の確認
```
現在設定されている監視項目を一覧表示してください
```

## トラブルシューティング

### よくある問題

#### 1. 接続エラー
```
Error: HTTP 401: Unauthorized
```
**解決方法**: 環境変数のユーザー名・パスワードを確認してください。

#### 2. SSL証明書エラー
```
SSL Certificate verification failed
```
**解決方法**: `HINEMOS_VERIFY_SSL=false` を設定してください。

#### 3. Hinemosサーバーに接続できない
```
Connection refused
```
**解決方法**: 
- Hinemosサーバーが起動していることを確認
- ネットワーク接続を確認
- ファイアウォール設定を確認

### デバッグ方法

#### ログの確認
サーバー起動時に詳細なログが出力されます：
```bash
python3 hinemos_mcp_server.py
```

#### 手動テスト
統合テストスクリプトで基本機能を確認：
```bash
python3 test_mcp_integration.py
```

## セキュリティ考慮事項

1. **認証情報の管理**: 環境変数を使用して認証情報を管理
2. **SSL/TLS**: 本番環境では SSL 証明書の検証を有効にする
3. **アクセス制御**: Hinemos側で適切なユーザー権限を設定
4. **ネットワーク**: MCPサーバーとHinemosサーバー間の通信を保護

## 開発・拡張

### 新しいツールの追加
`src/hinemos_mcp/server/server.py` の `list_tools()` および `call_tool()` メソッドを拡張してください。

### 新しいリソースの追加  
`src/hinemos_mcp/server/server.py` の `list_resources()` および `read_resource()` メソッドを拡張してください。

## ライセンス

このプロジェクトは Hinemos と同じライセンスの下で提供されています。