# Hinemos MCP Server - Windows セットアップガイド

## 前提条件

1. **Python 3.8以上** がインストールされていること
2. **pip** が利用可能であること
3. **Hinemos サーバ** へのネットワーク接続

## セットアップ手順

### 1. 依存関係のインストール

```cmd
pip install -r requirements.txt
```

### 2. 環境変数の設定

以下の環境変数を設定するか、`start_fastmcp_server.bat` を編集してください：

```cmd
set HINEMOS_BASE_URL=http://3.113.245.85:8080/HinemosWeb/api
set HINEMOS_USERNAME=hinemos
set HINEMOS_PASSWORD=hinemos
set HINEMOS_VERIFY_SSL=false
```

### 3. サーバの起動

#### 方法1: バッチファイルを使用
```cmd
start_fastmcp_server.bat
```

#### 方法2: 直接Python実行
```cmd
python hinemos_fastmcp_server.py
```

## 利用可能なMCPツール

### リポジトリ管理
- `hinemos_get_facility_tree` - 完全なファシリティツリーを取得
- `hinemos_get_repository_node` - 特定のノード情報を取得
- `hinemos_create_repository_node` - 新しいノードを作成
- `hinemos_update_repository_node` - 既存ノードを更新

### 監視設定管理
- `hinemos_get_monitor` - 特定の監視設定を取得
- `hinemos_create_monitor` - **統合監視作成ツール** (全11種類対応)

### スコープ管理
- `hinemos_create_scope` - 新しいスコープを作成
- `hinemos_assign_nodes_to_scope` - ノードをスコープに割り当て
- `hinemos_remove_nodes_from_scope` - スコープからノードを削除

## 統合監視作成ツール

`hinemos_create_monitor` では以下の監視タイプをサポート：

1. **ping** - PING監視
2. **http_numeric** - HTTP数値監視
3. **http_string** - HTTP文字列監視
4. **snmp** - SNMP監視
5. **logfile** - ログファイル監視
6. **sql** - SQL監視
7. **jmx** - JMX監視
8. **process** - プロセス監視
9. **port** - ポート監視
10. **winevent** - Windowsイベント監視
11. **custom** - カスタム監視

### 使用例

```json
{
  "monitor_type": "ping",
  "monitor_id": "ping_monitor_01",
  "facility_id": "target_node_01",
  "description": "サーバ死活監視",
  "run_interval": "MIN_05",
  "run_count": 3,
  "timeout": 5000
}
```

## トラブルシューティング

### 接続エラー
- Hinemos サーバのURL、ユーザ名、パスワードを確認
- ネットワーク接続を確認
- SSL証明書の問題がある場合は `HINEMOS_VERIFY_SSL=false` を設定

###依存関係エラー
```cmd
pip install --upgrade -r requirements.txt
```

### ポートエラー
- 他のMCPサーバが起動していないか確認
- 管理者権限で実行

## ログとデバッグ

サーバ起動時にコンソールにログが出力されます。エラーが発生した場合は、ログの内容を確認してください。

## 参考資料

- `docs/mcp-server.md` - MCP サーバの詳細ドキュメント
- `examples/` - 使用例
- `integration/` - 統合テスト例