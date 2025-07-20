# Hinemos MCP Client

Hinemos MCP (Model Context Protocol) Client は、Hinemos REST API を Python から簡単に操作できるクライアントライブラリです。また、Claude AI と統合するための MCP サーバーも提供します。

Project status: Under working

## 2025/07/20

現在再実装中で動作が不完全です。確認できた機能は以下です
- リポジトリ管理
  - ファシリティツリーの取得(OK)
  - ノードツリーの取得(OK)
  - スコープの取得(OK)
  - ノードの追加(OK)
  - ノードに対するスコープの割り当て(NG)
  - スコープの作成(Not Yet)
- 監視設定(Not yet)
- 収集(Not yet)
- ジョブ管理(Not yet)
- エージェント管理(Not yet)
- ログ管理(Not yet)
****

## 🚀 主な機能

### 🔧 Hinemos REST Client
- **リポジトリ管理**: ノード・スコープの作成、更新、削除、検索
- **監視設定**: 各種監視（Ping、HTTP、SNMP、ログファイル等）の作成・管理
- **認証**: ユーザー名・パスワード認証、セッション管理
- **エラーハンドリング**: 詳細なエラー情報とリトライ機能

### 🤖 MCP Server（Claude AI 統合）
- **自然言語操作**: Claude AI から自然言語でHinemosを操作
- **統一インターフェース**: 複数の監視タイプを一つのツールで作成
- **リソース提供**: ノード、スコープ、監視設定の一覧表示
- **セキュアな設定**: 環境変数による認証情報管理

## 📦 システム要件

- Python 3.8+
- Hinemos 7.0+
- mcp パッケージ（MCP Server使用時）

## 🔧 インストール

```bash
# リポジトリのクローン
git clone https://github.com/your-username/hinemos-mcp-claude.git
cd hinemos-mcp-claude

# 基本ライブラリのインストール
pip install httpx pydantic

# MCP Server使用時（Claude AI統合）
pip install mcp
```

## 🚀 クイックスタート

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
    print(f"ノード数: {len(nodes)}")
    
    # 監視設定操作
    monitor = MonitorAPI(client)
    monitors = monitor.list_monitors()
    print(f"監視設定数: {len(monitors)}")
```

### 2. MCP Server の起動（Claude AI統合）

```bash
# 環境変数設定
export HINEMOS_BASE_URL="http://hinemos-server:8080/HinemosWeb/api"
export HINEMOS_USERNAME="hinemos"
export HINEMOS_PASSWORD="hinemos"

# サーバー起動
python3 hinemos_mcp_server.py
```

### 3. Claude での使用例

```
Hinemosのノード一覧を表示してください

新しいWebサーバー（192.168.1.100）をリポジトリに追加してください

WEB1サーバーにPing監視を設定してください
```

## 📂 プロジェクト構成

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
├── examples/                  # サンプルコード（テンプレート）
├── tests/                     # テストコード
├── hinemos_mcp_server.py      # MCP サーバー起動スクリプト
└── mcp_config_template.json   # MCP 設定ファイルテンプレート
```

## ✅ 対応機能

### リポジトリ管理
- [x] ノードの作成・更新・削除・一覧取得
- [x] スコープの作成・更新・削除・一覧取得  
- [x] ファシリティツリーの取得
- [x] エージェント状態の確認

### 監視設定
- [x] Ping監視
- [x] HTTP監視（数値・文字列）
- [x] SNMP監視
- [x] ログファイル監視
- [x] 監視の有効化・無効化
- [x] コレクター制御

### MCP Server
- [x] Claude AI との統合
- [x] リソース提供（ノード、監視設定等）
- [x] 統一された操作インターフェース
- [x] 環境変数による設定管理

## 📖 ドキュメント

詳細なドキュメントは `docs/` ディレクトリにあります：

- **[メインドキュメント](./docs/README.md)** - プロジェクト全体の概要
- **[Hinemos REST Client API](./docs/hinemos-rest-client.md)** - Python クライアントライブラリの完全リファレンス
- **[MCP Server ドキュメント](./docs/mcp-server.md)** - Claude AI との統合方法
- **[MCP Server 使用例](./docs/mcp-server-examples.md)** - Claude で使用できる具体的なコマンド例
- **[API リファレンス](./docs/api-reference.md)** - 詳細なAPIドキュメント
- **[使用例](./docs/examples.md)** - 基本的な使用方法とサンプルコード

## 🔧 設定方法

### 1. 基本設定

`examples/` ディレクトリのテンプレートファイルをコピーして設定：

```bash
# リポジトリ操作の例
cp examples/repository_example_template.py examples/repository_example.py
# ファイルを編集してあなたのHinemosサーバー情報を設定

# 監視設定の例  
cp examples/monitor_example_template.py examples/monitor_example.py
# ファイルを編集してあなたのHinemosサーバー情報を設定
```

### 2. MCP Server設定

```bash
# MCP設定ファイルの作成
cp mcp_config_template.json mcp_config.json
# ファイルを編集してあなたのHinemosサーバー情報を設定
```

## 🧪 テスト

```bash
# 基本動作テスト（設定後）
python3 examples/repository_example.py
python3 examples/monitor_example.py

# MCP Server テスト
python3 hinemos_mcp_server.py
```

## 🤝 貢献

プロジェクトへの貢献を歓迎します：

1. Issue の報告
2. 機能要求の提案
3. プルリクエストの送信
4. ドキュメントの改善

## 📄 ライセンス

このプロジェクトは Hinemos と同じライセンスの下で提供されています。

## 🔗 関連リンク

- [Hinemos公式サイト](https://www.hinemos.info/)
- [Model Context Protocol (MCP)](https://spec.modelcontextprotocol.io/)
- [Claude AI](https://claude.ai/)

## 💡 使用例

### Pythonクライアント
```python
# ノード作成
with HinemosClient(**config) as client:
    repo = RepositoryAPI(client)
    node = repo.create_node(
        facility_id="WEB01",
        facility_name="Web Server 01", 
        ip_address="192.168.1.100"
    )

# Ping監視作成
    monitor = MonitorAPI(client)
    ping_monitor = monitor.create_ping_monitor(
        monitor_id="PING_WEB01",
        facility_id="WEB01",
        description="Web server ping check"
    )
```

### Claude AI（MCP Server経由）
```
新しいWebサーバー「WEB02」（IP: 192.168.1.101）をリポジトリに追加して、
Ping監視とHTTP監視を設定してください。
```

---

**注意**: テンプレートファイルを使用して、実際のサーバー情報で設定してからご利用ください。
