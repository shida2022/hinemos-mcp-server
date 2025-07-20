# MCPサーバー再起動手順

## 問題の診断
- ツール `hinemos_create_scope` が見つからないエラーが発生
- 新しく追加したスコープ管理機能が認識されていない

## 解決手順

### 1. MCPサーバーを停止
現在実行中のMCPサーバーを停止してください。

### 2. キャッシュファイルの削除（既に完了）
```bash
# Pythonキャッシュファイルを削除（完了済み）
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### 3. MCPサーバーを再起動
```bash
# コマンドラインから直接実行する場合
python3 hinemos_mcp_server.py

# またはClaude Desktopを再起動
```

### 4. 利用可能なツールの確認
サーバー再起動後、以下のツールが利用可能になるはずです：

- `hinemos_create_scope` - 新しいスコープを作成
- `hinemos_assign_nodes_to_scope` - ノードをスコープに割り当て
- `hinemos_remove_nodes_from_scope` - スコープからノードを削除

### 5. 使用例

#### スコープ作成
```json
{
  "tool": "hinemos_create_scope",
  "arguments": {
    "facility_id": "SCOPE_001",
    "facility_name": "Production Servers",
    "description": "Production environment servers",
    "owner_role_id": "ADMINISTRATORS"
  }
}
```

#### ノード割り当て
```json
{
  "tool": "hinemos_assign_nodes_to_scope", 
  "arguments": {
    "scope_id": "SCOPE_001",
    "node_ids": ["NODE_001", "NODE_002", "NODE_003"]
  }
}
```

## トラブルシューティング

### Claude Desktopを使用している場合
1. Claude Desktopアプリケーションを完全に終了
2. アプリケーションを再起動
3. 新しいチャットセッションを開始

### 環境変数の確認
`mcp_config.json`で以下の環境変数が正しく設定されていることを確認：
- `HINEMOS_BASE_URL`
- `HINEMOS_USERNAME` 
- `HINEMOS_PASSWORD`
- `HINEMOS_VERIFY_SSL`

### ログの確認
サーバー起動時のログで以下を確認：
- エラーメッセージがないか
- 接続が成功しているか
- 新しいツールが読み込まれているか