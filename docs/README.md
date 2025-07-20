# Hinemos MCP Client Documentation

Hinemos MCP (Model Context Protocol) Client は、Hinemos REST API を Python から簡単に操作できるクライアントライブラリです。また、Claude AI と統合するための MCP サーバーも提供します。

## ドキュメント一覧

### 📚 基本ドキュメント
- **[Hinemos REST Client API リファレンス](./hinemos-rest-client.md)** - Python クライアントライブラリの完全なAPIリファレンス
- **[API リファレンス](./api-reference.md)** - 各モジュールの詳細なAPIドキュメント
- **[使用例](./examples.md)** - 基本的な使用方法とサンプルコード

### 🤖 MCP Server（Claude AI 統合）
- **[MCP Server ドキュメント](./mcp-server.md)** - Claude AI との統合を可能にする MCP サーバーの設定と使用方法
- **[MCP Server 使用例](./mcp-server-examples.md)** - Claude で実際に使用できる具体的なコマンド例

## プロジェクト構成

```
hinemos-mcp-claude/
├── src/hinemos_mcp/           # メインライブラリ
│   ├── client.py              # Hinemos REST クライアント
│   ├── models.py              # データモデル定義
│   ├── repository.py          # リポジトリ API ラッパー
│   ├── monitor.py             # 監視 API ラッパー
│   ├── monitor_models.py      # 監視データモデル
│   └── server/                # MCP サーバー
│       └── server.py          # MCP サーバー実装
├── docs/                      # ドキュメント
├── examples/                  # サンプルコード
├── tests/                     # テストコード
├── hinemos_mcp_server.py      # MCP サーバー起動スクリプト
└── mcp_config.json           # MCP 設定ファイル
```

## 主な機能

### 🔧 Hinemos REST Client
- **リポジトリ管理**: ノード・スコープの作成、更新、削除、検索
- **監視設定**: 各種監視（Ping、HTTP、SNMP、ログファイル等）の作成・管理
- **認証**: ユーザー名・パスワード認証、セッション管理
- **エラーハンドリング**: 詳細なエラー情報とリトライ機能

### 🤖 MCP Server
- **Claude AI 統合**: 自然言語でHinemosを操作
- **統一インターフェース**: 複数の監視タイプを一つのツールで作成
- **リソース提供**: ノード、スコープ、監視設定の一覧表示
- **セキュアな設定**: 環境変数による認証情報管理

## クイックスタート

### 1. Python クライアントの使用

```python
from hinemos_mcp import HinemosClient, RepositoryAPI, MonitorAPI

# クライアント接続
with HinemosClient(
    base_url="http://hinemos-server:8080/HinemosWeb/api",
    username="hinemos",
    password="hinemos"
) as client:
    # リポジトリ操作
    repo = RepositoryAPI(client)
    nodes = repo.list_nodes()
    
    # 監視設定操作
    monitor = MonitorAPI(client)
    monitors = monitor.list_monitors()
```

### 2. MCP Server の起動

```bash
# 環境変数設定
export HINEMOS_BASE_URL="http://hinemos-server:8080/HinemosWeb/api"
export HINEMOS_USERNAME="hinemos"
export HINEMOS_PASSWORD="hinemos"

# サーバー起動
python3 hinemos_mcp_server.py
```

### 3. Claude での使用

```
Hinemosのノード一覧を表示してください

新しいWebサーバー（192.168.1.100）をリポジトリに追加してください

WEB1サーバーにPing監視を設定してください
```

## 対応機能

### ✅ リポジトリ管理
- [x] ノードの作成・更新・削除・一覧取得
- [x] スコープの作成・更新・削除・一覧取得  
- [x] ファシリティツリーの取得
- [x] エージェント状態の確認

### ✅ 監視設定
- [x] Ping監視
- [x] HTTP監視（数値・文字列）
- [x] SNMP監視
- [x] ログファイル監視
- [x] カスタム監視（拡張可能）
- [x] 監視の有効化・無効化
- [x] コレクター制御

### ✅ MCP Server
- [x] Claude AI との統合
- [x] リソース提供（ノード、監視設定等）
- [x] 統一された操作インターフェース
- [x] 環境変数による設定管理

## システム要件

- Python 3.8+
- Hinemos 7.0+
- mcp パッケージ（MCP Server使用時）

## インストール

```bash
# 基本ライブラリのインストール
pip install -r requirements.txt

# MCP Server使用時
pip install mcp
```

## 貢献

プロジェクトへの貢献を歓迎します：

1. Issue の報告
2. 機能要求の提案
3. プルリクエストの送信
4. ドキュメントの改善

## ライセンス

このプロジェクトは Hinemos と同じライセンスの下で提供されています。

## サポート

- **ドキュメント**: このディレクトリ内の各ドキュメントを参照
- **サンプル**: `examples/` ディレクトリのサンプルコード
- **テスト**: `tests/` ディレクトリのテストコード
- **統合テスト**: `monitor_comprehensive_test.py` で全機能のテスト

## 最新情報

このライブラリは継続的に開発されており、新機能の追加や改善が行われています。最新の変更については、プロジェクトのコミット履歴を確認してください。