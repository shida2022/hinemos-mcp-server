# Hinemos REST Client API Reference

## 目次

1. [エンドポイント一覧](#エンドポイント一覧)
2. [認証](#認証)
3. [リクエスト・レスポンス形式](#リクエストレスポンス形式)
4. [コード例](#コード例)

## エンドポイント一覧

### 認証関連

| エンドポイント | メソッド | 説明 |
|-------------|---------|------|
| `/AccessRestEndpoints/access/login` | POST | ログイン・トークン取得 |
| `/AccessRestEndpoints/access/logout` | GET | ログアウト |

### Repository API

| エンドポイント | メソッド | 説明 | 実装状況 | テスト結果 |
|-------------|---------|------|---------|----------|
| `/RepositoryRestEndpoints/repository/facility_tree` | GET | ファシリティツリー取得 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/facility_tree/{facilityId}` | GET | 指定ファシリティ配下のツリー取得 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/facility_nodeTree` | GET | ノードツリー取得 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/node_withoutNodeConfigInfo_search` | POST | ノード検索 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/node_withoutNodeConfigInfo/{facilityId}` | GET | ノード情報取得（構成情報なし） | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/node/{facilityId}` | GET | ノード情報取得（完全版） | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/node` | POST | ノード作成 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/node/{facilityId}` | PUT | ノード更新 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/node` | DELETE | ノード削除 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/scope/{facilityId}` | GET | スコープ情報取得 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/scope` | POST | スコープ作成 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/scope/{facilityId}` | PUT | スコープ更新 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/scope` | DELETE | スコープ削除 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/facilityRelation/{parentFacilityId}` | PUT | ノード・スコープ関連付け | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/facilityRelation_release/{parentFacilityId}` | PUT | ノード・スコープ関連解除 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/node_valid/{facilityId}` | PUT | ノード有効/無効設定 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/agentStatus` | GET | エージェント状態取得 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/facility_ping/{facilityId}` | POST | ノードPing実行 | ✅ | ✅ 100% |
| `/RepositoryRestEndpoints/repository/facility` | GET | 全ファシリティ情報取得 | ✅ | ✅ 100% |

**テスト結果サマリー**: 全24メソッド 100%成功（2025年7月19日時点）

## 認証

### ログインフロー

1. **ログインリクエスト**
   ```http
   POST /AccessRestEndpoints/access/login
   Content-Type: application/json
   
   {
     "userId": "username",
     "password": "password"
   }
   ```

2. **ログインレスポンス**
   ```json
   {
     "token": {
       "tokenId": "uuid-string",
       "expirationDate": "2025-07-20 09:07:54.151",
       "validTermMinites": 1440
     },
     "managerInfo": {
       "timeZoneOffset": 0,
       "timeOffsetMillis": 0,
       "options": []
     }
   }
   ```

3. **後続リクエスト**
   ```http
   GET /RepositoryRestEndpoints/repository/facility_tree
   Content-Type: application/json
   Authorization: Bearer {tokenId}
   ```

## リクエスト・レスポンス形式

### ノード作成

**リクエスト:**
```json
{
  "facilityId": "SERVER01",
  "facilityName": "Web Server 01",
  "description": "Production web server",
  "ownerRoleId": "ADMINISTRATORS",
  "ipAddressVersion": "IPV4",
  "ipAddressV4": "192.168.1.100",
  "platformFamily": "LINUX",
  "snmpCommunity": "public",
  "snmpPort": 161,
  "snmpVersion": "TYPE_V2",
  "valid": true
}
```

**レスポンス:**
```json
{
  "facilityId": "SERVER01",
  "facilityName": "Web Server 01",
  "description": "Production web server",
  "ownerRoleId": "ADMINISTRATORS",
  "ipAddressVersion": "IPV4",
  "ipAddressV4": "192.168.1.100",
  "ipAddressV6": "",
  "platformFamily": "LINUX",
  "snmpCommunity": "public",
  "snmpPort": 161,
  "snmpVersion": "TYPE_V2",
  "valid": true,
  "createUserId": "hinemos",
  "createDatetime": "2025-07-19 10:30:00.000",
  "modifyUserId": "hinemos",
  "modifyDatetime": "2025-07-19 10:30:00.000"
}
```

### ノード検索

**リクエスト:**
```json
{
  "parentFacilityId": "PRODUCTION",
  "nodeConfigFilterIsAnd": true,
  "nodeConfigTargetDatetime": "2025-07-19 10:00:00.000"
}
```

**レスポンス:**
```json
[
  {
    "facilityId": "WEB1",
    "facilityName": "静的Webサーバ",
    "ipAddressVersion": "IPV4",
    "ipAddressV4": "172.31.24.100",
    "ipAddressV6": "",
    "platformFamily": "LINUX",
    "description": "",
    "ownerRoleId": "ALL_USERS",
    "createDatetime": "2025-06-10 09:59:41.980",
    "modifyDatetime": "2025-06-10 09:59:41.980"
  }
]
```

### ファシリティツリー取得

**レスポンス:**
```json
{
  "data": {
    "facilityId": "_ROOT_",
    "facilityName": "ルート",
    "facilityType": "TYPE_COMPOSITE",
    "description": "",
    "displaySortOrder": 0,
    "iconImage": "",
    "valid": true,
    "createUserId": "",
    "createDatetime": "1970-01-01 09:00:00.000",
    "modifyUserId": "",
    "modifyDatetime": "1970-01-01 09:00:00.000",
    "builtInFlg": true,
    "notReferFlg": false,
    "ownerRoleId": "ADMINISTRATORS"
  }
}
```

### エラーレスポンス

```json
{
  "status": 404,
  "message": "Not Found",
  "exception": "com.clustercontrol.fault.UrlNotFound",
  "stack": [
    "com.clustercontrol.plugin.util.RestApiHttpServerFactory$1.generate(...)",
    "..."
  ]
}
```

## コード例

### 基本的なCRUD操作

```python
from hinemos_mcp import HinemosClient, RepositoryAPI

# 設定
config = {
    "base_url": "http://hinemos-server:8080/HinemosWeb/api",
    "username": "hinemos",
    "password": "hinemos",
    "verify_ssl": False
}

with HinemosClient(**config) as client:
    repo = RepositoryAPI(client)
    
    # ノード作成
    node = repo.create_node(
        facility_id="SERVER01",
        facility_name="Web Server 01",
        ip_address="192.168.1.100",
        platform_family="LINUX"
    )
    print(f"Created node: {node.facility_id}")
    
    # ノード一覧取得
    nodes = repo.list_nodes()
    print(f"Total nodes: {len(nodes)}")
    
    # ノード更新
    updated_node = repo.update_node(
        facility_id="SERVER01",
        description="Updated description"
    )
    
    # ノード削除
    repo.delete_node("SERVER01")
```

### スコープ管理

```python
# スコープ作成
scope = repo.create_scope(
    facility_id="PRODUCTION",
    facility_name="Production Environment"
)

# ノードをスコープに割り当て
repo.assign_nodes_to_scope("PRODUCTION", ["SERVER01", "SERVER02"])

# スコープからノードを削除
repo.remove_nodes_from_scope("PRODUCTION", ["SERVER01"])
```

### エラーハンドリング

```python
from hinemos_mcp import HinemosAPIError

try:
    node = repo.get_node("NONEXISTENT")
except HinemosAPIError as e:
    if e.status_code == 404:
        print("Node not found")
    elif e.status_code == 401:
        print("Authentication failed")
    else:
        print(f"API Error: {e}")
```

### 監視操作

```python
# エージェント状態確認
agent_status = repo.get_agent_status()
for agent in agent_status['agents']:
    print(f"Agent {agent['facility_id']}: startup={agent['startup_time']}")

# ノードのPing実行
ping_result = repo.ping_node("SERVER01", count=3)
print(f"Ping result: {ping_result}")

# ノードの有効/無効切り替え
repo.disable_node("SERVER01")
repo.enable_node("SERVER01")
```

## パフォーマンス考慮事項

1. **認証トークン**: 自動管理されるため、頻繁なログインは発生しません
2. **接続プール**: httpxのconnection poolingを活用
3. **タイムアウト**: 適切なタイムアウト設定で応答性を確保
4. **バッチ操作**: 複数ノードの削除は単一APIコールで実行

## セキュリティ考慮事項

1. **認証情報**: 環境変数での管理を推奨
2. **SSL/TLS**: 本番環境では `verify_ssl=True` を設定
3. **権限管理**: 最小権限の原則に従いユーザー権限を設定
4. **トークン管理**: トークンは自動的に期限管理されます