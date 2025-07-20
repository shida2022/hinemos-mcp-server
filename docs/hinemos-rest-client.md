# Hinemos REST Client Documentation

## 概要

Hinemos REST Client は、HinemosのREST APIと統合するためのPythonクライアントライブラリです。
Repository APIを中心とした監視システムの操作を、型安全で使いやすいインターフェースで提供します。

## 特徴

- **型安全**: Pydanticを使用した完全な型定義
- **認証対応**: Bearer token認証の自動管理
- **高レベルAPI**: 使いやすいRepository APIラッパー
- **エラーハンドリング**: 詳細なエラー情報とトラブルシューティング

## インストール

```bash
pip install httpx pydantic
```

## 基本的な使用方法

### クライアントの初期化

```python
from hinemos_mcp import HinemosClient, RepositoryAPI

# クライアント設定
config = {
    "base_url": "http://your-hinemos-server:8080/HinemosWeb/api",
    "username": "hinemos",
    "password": "hinemos",
    "verify_ssl": False  # 開発環境用
}

# クライアント作成
with HinemosClient(**config) as client:
    repo = RepositoryAPI(client)
    
    # APIを使用
    facility_tree = repo.get_facility_tree()
    print(f"Root facility: {facility_tree.facility_name}")
```

### 自動認証

クライアントは最初のAPI呼び出し時に自動的にログインし、Bearer tokenを取得します。
トークンは内部で管理され、後続のリクエストで自動的に使用されます。

## API リファレンス

### HinemosClient（低レベルAPI）

基本的なHTTPクライアント機能を提供します。

#### コンストラクタ

```python
HinemosClient(
    base_url: str,
    username: str,
    password: str,
    timeout: float = 30.0,
    verify_ssl: bool = True
)
```

**パラメータ:**
- `base_url`: HinemosサーバーのベースURL（例: `http://server:8080/HinemosWeb/api`）
- `username`: ログイン用ユーザー名
- `password`: ログイン用パスワード
- `timeout`: リクエストタイムアウト（秒）
- `verify_ssl`: SSL証明書の検証を行うかどうか

#### 主要メソッド

##### `login() -> None`
Hinemosにログインしてトークンを取得します。通常は自動的に呼ばれます。

##### `get_facility_tree(target_facility_id: Optional[str] = None) -> FacilityInfo`
ファシリティツリーを取得します。

##### `get_node_list(request: Optional[GetNodeListRequest] = None) -> List[NodeInfo]`
ノード一覧を取得します。

##### `add_node(node: AddNodeRequest) -> NodeInfo`
新しいノードを追加します。

##### `modify_node(facility_id: str, node: ModifyNodeRequest) -> NodeInfo`
既存のノードを更新します。

##### `delete_nodes(facility_ids: List[str]) -> None`
指定されたノードを削除します。

### RepositoryAPI（高レベルAPI）

Repository操作のためのより使いやすいラッパーです。

#### コンストラクタ

```python
RepositoryAPI(client: HinemosClient)
```

#### ノード管理

##### `create_node(facility_id, facility_name, ip_address, **kwargs) -> NodeInfo`

新しいノードを作成します。

**パラメータ:**
- `facility_id`: ユニークなファシリティID
- `facility_name`: 表示名
- `ip_address`: IPアドレス
- `owner_role_id`: オーナーロールID（デフォルト: "ADMINISTRATORS"）
- `description`: 説明（オプション）
- `platform_family`: プラットフォームファミリ（オプション）
- `snmp_community`: SNMPコミュニティ（デフォルト: "public"）
- `snmp_port`: SNMPポート（デフォルト: 161）
- `snmp_version`: SNMPバージョン（デフォルト: V2）

**例:**
```python
node = repo.create_node(
    facility_id="SERVER01",
    facility_name="Web Server 01",
    ip_address="192.168.1.100",
    description="Production web server",
    platform_family="Linux"
)
```

##### `update_node(facility_id, **kwargs) -> NodeInfo`

既存のノードを更新します。

**例:**
```python
updated_node = repo.update_node(
    facility_id="SERVER01",
    description="Updated description",
    ip_address="192.168.1.101"
)
```

##### `get_node(facility_id, include_config=False) -> NodeInfo`

ノード情報を取得します。

**例:**
```python
node = repo.get_node("SERVER01", include_config=True)
print(f"Node: {node.facility_name} - {node.ip_address_v4}")
```

##### `list_nodes(parent_scope_id=None, target_datetime=None) -> List[NodeInfo]`

ノード一覧を取得します。

**例:**
```python
# 全ノードを取得
all_nodes = repo.list_nodes()

# 特定のスコープ配下のノードを取得
scope_nodes = repo.list_nodes(parent_scope_id="PRODUCTION")
```

##### `delete_node(facility_id) -> None`

ノードを削除します。

##### `enable_node(facility_id) -> None` / `disable_node(facility_id) -> None`

ノードを有効/無効にします。

##### `ping_node(facility_id, count=3) -> dict`

ノードの接続性をテストします。

#### スコープ管理

##### `create_scope(facility_id, facility_name, **kwargs) -> ScopeInfo`

新しいスコープを作成します。

**例:**
```python
scope = repo.create_scope(
    facility_id="PRODUCTION",
    facility_name="Production Environment",
    description="本番環境"
)
```

##### `update_scope(facility_id, **kwargs) -> ScopeInfo`

既存のスコープを更新します。

##### `get_scope(facility_id) -> ScopeInfo`

スコープ情報を取得します。

##### `delete_scope(facility_id) -> None`

スコープを削除します。

##### `assign_nodes_to_scope(scope_id, node_ids) -> None`

ノードをスコープに割り当てます。

**例:**
```python
repo.assign_nodes_to_scope("PRODUCTION", ["SERVER01", "SERVER02"])
```

##### `remove_nodes_from_scope(scope_id, node_ids) -> None`

ノードをスコープから削除します。

#### ファシリティツリー操作

##### `get_facility_tree(root_facility_id=None) -> FacilityInfo`

ファシリティツリー構造を取得します。

##### `get_all_facilities() -> List[FacilityInfo]`

すべてのファシリティ情報を取得します。

#### エージェント操作

##### `get_agent_status() -> dict`

エージェント状態を取得します。

**例:**
```python
status = repo.get_agent_status()
for agent in status['agents']:
    print(f"Agent {agent['facility_id']}: last_login={agent['last_login']}")
```

## データモデル

### NodeInfo

ノード情報を表すモデルです。

**主要フィールド:**
- `facility_id`: ファシリティID
- `facility_name`: ファシリティ名
- `description`: 説明
- `ip_address_v4` / `ip_address_v6`: IPアドレス
- `ip_address_version`: IPバージョン（IPV4/IPV6）
- `platform_family`: プラットフォームファミリ
- `snmp_*`: SNMP設定
- `ssh_*`: SSH設定
- `valid`: 有効フラグ
- `owner_role_id`: オーナーロールID

### ScopeInfo

スコープ情報を表すモデルです。

**主要フィールド:**
- `facility_id`: ファシリティID
- `facility_name`: ファシリティ名
- `description`: 説明
- `owner_role_id`: オーナーロールID

### FacilityInfo

ファシリティ情報を表すモデルです。

**主要フィールド:**
- `facility_id`: ファシリティID
- `facility_name`: ファシリティ名
- `facility_type`: ファシリティタイプ（TYPE_SCOPE/TYPE_NODE/TYPE_COMPOSITE/TYPE_MANAGER）
- `description`: 説明
- `valid`: 有効フラグ

### 列挙型

#### IpAddressVersion
- `IPV4`: IPv4
- `IPV6`: IPv6

#### FacilityType
- `TYPE_SCOPE`: スコープ
- `TYPE_NODE`: ノード
- `TYPE_COMPOSITE`: コンポジット
- `TYPE_MANAGER`: マネージャ

#### SnmpVersion
- `TYPE_V1`: SNMP v1
- `TYPE_V2`: SNMP v2c
- `TYPE_V3`: SNMP v3

## エラーハンドリング

### HinemosAPIError

すべてのHinemos API関連のエラーは `HinemosAPIError` として発生します。

**属性:**
- `message`: エラーメッセージ
- `status_code`: HTTPステータスコード（存在する場合）
- `response`: サーバーからのレスポンス（存在する場合）

**例:**
```python
try:
    node = repo.get_node("NONEXISTENT")
except HinemosAPIError as e:
    print(f"API Error: {e}")
    if e.status_code == 404:
        print("Node not found")
    elif e.status_code == 401:
        print("Authentication failed")
```

### 一般的なエラーケース

1. **401 Unauthorized**: 認証エラー
   - ユーザー名・パスワードを確認
   - ユーザーの権限を確認

2. **404 Not Found**: リソースが見つからない
   - ファシリティIDを確認
   - エンドポイントのURLを確認

3. **500 Internal Server Error**: サーバーエラー
   - Hinemosマネージャのログを確認
   - データベース接続を確認

## 設定例

### 開発環境

```python
config = {
    "base_url": "http://localhost:8080/HinemosWeb/api",
    "username": "hinemos",
    "password": "hinemos",
    "verify_ssl": False,
    "timeout": 10.0
}
```

### 本番環境

```python
config = {
    "base_url": "https://hinemos.company.com:8443/HinemosWeb/api",
    "username": "api_user",
    "password": os.getenv("HINEMOS_PASSWORD"),
    "verify_ssl": True,
    "timeout": 30.0
}
```

## 制限事項

1. **対応API**: 現在はRepository APIのみ対応
2. **認証方式**: Bearer token認証のみ対応
3. **Hinemosバージョン**: REST APIが有効なバージョンが必要

## テスト

### 動作確認例

```python
from hinemos_mcp import HinemosClient, RepositoryAPI

# 基本的な動作確認
with HinemosClient(**config) as client:
    repo = RepositoryAPI(client)
    
    # ファシリティツリーの取得
    tree = repo.get_facility_tree()
    print(f"Root: {tree.facility_name}")
    
    # ノード一覧の取得
    nodes = repo.list_nodes()
    print(f"Total nodes: {len(nodes)}")
    
    # テストノードの作成と削除
    test_node = repo.create_node(
        facility_id="TEST_NODE_001",
        facility_name="Test Node",
        ip_address="192.168.1.100"
    )
    print(f"Created: {test_node.facility_name}")
    
    # クリーンアップ
    repo.delete_node("TEST_NODE_001")
    print("Test node deleted")
```

## トラブルシューティング

### よくある問題

1. **404 エラー**: エンドポイントURLを確認
2. **認証エラー**: ユーザー名・パスワード・権限を確認
3. **タイムアウト**: ネットワーク接続とtimeout設定を確認

## ライセンス

このプロジェクトのライセンスについては、プロジェクトルートのLICENSEファイルを参照してください。