# Hinemos REST Client Examples

## 基本的な使用例

### 1. 基本的な接続とファシリティ情報取得

```python
from hinemos_mcp import HinemosClient, RepositoryAPI

# Hinemosサーバー設定
config = {
    "base_url": "http://hinemos-server:8080/HinemosWeb/api",
    "username": "hinemos",
    "password": "hinemos",
    "verify_ssl": False,  # 開発環境用
    "timeout": 30.0
}

# 接続テストと基本操作
with HinemosClient(**config) as client:
    repo = RepositoryAPI(client)
    
    # ファシリティツリー取得
    facility_tree = repo.get_facility_tree()
    print(f"Root facility: {facility_tree.facility_name} ({facility_tree.facility_id})")
    
    # 全ノード一覧取得
    nodes = repo.list_nodes()
    print(f"Total nodes: {len(nodes)}")
    
    # ノード情報の表示
    for node in nodes[:5]:
        ip = node.ip_address_v4 or node.ip_address_v6 or "No IP"
        status = "有効" if node.valid else "無効"
        print(f"  - {node.facility_id}: {node.facility_name} ({ip}) - {status}")
    
    # エージェント状態確認
    agent_status = repo.get_agent_status()
    print(f"Active agents: {len(agent_status['agents'])}")
```

### 2. ノード作成と設定

```python
def create_linux_server():
    """Linuxサーバーノードを作成する例"""
    with HinemosClient(**config) as client:
        repo = RepositoryAPI(client)
        
        # Linuxサーバーノード作成
        node = repo.create_node(
            facility_id="LINUX_WEB01",
            facility_name="Linux Web Server 01",
            ip_address="192.168.1.100",
            description="Apache Web Server on CentOS 8",
            platform_family="LINUX",
            
            # SNMP設定
            snmp_community="public",
            snmp_port=161,
            snmp_version=SnmpVersion.V2,
            
            # 追加設定
            administrator="webadmin@company.com",
            contact="IT Support Team"
        )
        
        print(f"Created Linux node: {node.facility_id}")
        return node

def create_windows_server():
    """Windowsサーバーノードを作成する例"""
    with HinemosClient(**config) as client:
        repo = RepositoryAPI(client)
        
        # Windowsサーバーノード作成
        node = repo.create_node(
            facility_id="WIN_DB01",
            facility_name="Windows Database Server 01",
            ip_address="192.168.1.200",
            description="SQL Server 2019 on Windows Server 2019",
            platform_family="WINDOWS",
            
            # SNMP設定
            snmp_community="private",
            snmp_port=161,
            snmp_version=SnmpVersion.V2,
            
            # WinRM設定（追加パラメータとして）
            winrm_port=5985,
            winrm_user="Administrator",
            winrm_protocol="HTTP"
        )
        
        print(f"Created Windows node: {node.facility_id}")
        return node
```

### 3. スコープ管理とノードの整理

```python
def setup_environment_scopes():
    """環境別のスコープを作成してノードを整理する例"""
    with HinemosClient(**config) as client:
        repo = RepositoryAPI(client)
        
        # 環境別スコープ作成
        scopes = [
            ("PRODUCTION", "本番環境", "Production environment servers"),
            ("STAGING", "ステージング環境", "Staging environment servers"),
            ("DEVELOPMENT", "開発環境", "Development environment servers")
        ]
        
        created_scopes = []
        for scope_id, scope_name, description in scopes:
            scope = repo.create_scope(
                facility_id=scope_id,
                facility_name=scope_name,
                description=description,
                owner_role_id="ADMINISTRATORS"
            )
            created_scopes.append(scope)
            print(f"Created scope: {scope.facility_id}")
        
        # 既存ノードを環境別に分類
        all_nodes = repo.list_nodes()
        
        # ノード名のパターンでスコープに振り分け
        for node in all_nodes:
            if "prod" in node.facility_name.lower():
                repo.assign_nodes_to_scope("PRODUCTION", [node.facility_id])
                print(f"Assigned {node.facility_id} to PRODUCTION")
            elif "stg" in node.facility_name.lower():
                repo.assign_nodes_to_scope("STAGING", [node.facility_id])
                print(f"Assigned {node.facility_id} to STAGING")
            elif "dev" in node.facility_name.lower():
                repo.assign_nodes_to_scope("DEVELOPMENT", [node.facility_id])
                print(f"Assigned {node.facility_id} to DEVELOPMENT")
        
        return created_scopes
```

### 4. 一括ノード管理

```python
def bulk_node_operations():
    """複数ノードの一括操作例"""
    with HinemosClient(**config) as client:
        repo = RepositoryAPI(client)
        
        # 複数ノードを一括作成
        nodes_to_create = [
            {
                "facility_id": f"WEB{i:02d}",
                "facility_name": f"Web Server {i:02d}",
                "ip_address": f"192.168.1.{100 + i}",
                "platform_family": "LINUX"
            }
            for i in range(1, 6)
        ]
        
        created_nodes = []
        for node_spec in nodes_to_create:
            try:
                node = repo.create_node(**node_spec)
                created_nodes.append(node)
                print(f"Created: {node.facility_id}")
            except HinemosAPIError as e:
                print(f"Failed to create {node_spec['facility_id']}: {e}")
        
        # Webサーバースコープ作成
        web_scope = repo.create_scope(
            facility_id="WEB_SERVERS",
            facility_name="Web Servers",
            description="All web server nodes"
        )
        
        # 作成したノードをWebサーバースコープに一括割り当て
        node_ids = [node.facility_id for node in created_nodes]
        repo.assign_nodes_to_scope("WEB_SERVERS", node_ids)
        print(f"Assigned {len(node_ids)} nodes to WEB_SERVERS scope")
        
        return created_nodes

def bulk_node_update():
    """複数ノードの一括更新例"""
    with HinemosClient(**config) as client:
        repo = RepositoryAPI(client)
        
        # 特定パターンのノードを検索
        all_nodes = repo.list_nodes()
        web_nodes = [node for node in all_nodes if "WEB" in node.facility_id]
        
        # SNMPコミュニティを一括更新
        for node in web_nodes:
            try:
                repo.update_node(
                    facility_id=node.facility_id,
                    snmp_community="web_servers_community",
                    description=f"Updated: {node.description or 'Web server node'}"
                )
                print(f"Updated: {node.facility_id}")
            except HinemosAPIError as e:
                print(f"Failed to update {node.facility_id}: {e}")
```

### 5. 監視とヘルスチェック

```python
def health_check_nodes():
    """ノードのヘルスチェック例"""
    with HinemosClient(**config) as client:
        repo = RepositoryAPI(client)
        
        # エージェント状態チェック
        agent_status = repo.get_agent_status()
        print(f"Total agents: {len(agent_status['agents'])}")
        
        # 各エージェントの状態確認
        for agent in agent_status['agents']:
            facility_id = agent['facility_id']
            last_login = agent['last_login']
            startup_time = agent['startup_time']
            
            print(f"\nAgent: {facility_id}")
            print(f"  Last Login: {last_login}")
            print(f"  Startup Time: {startup_time}")
            
            # ノードへのPing実行
            try:
                ping_result = repo.ping_node(facility_id, count=3)
                print(f"  Ping: SUCCESS")
            except HinemosAPIError as e:
                print(f"  Ping: FAILED - {e}")

def monitor_node_connectivity():
    """ノード接続性の定期監視例"""
    import time
    
    with HinemosClient(**config) as client:
        repo = RepositoryAPI(client)
        
        # 監視対象ノード一覧
        nodes = repo.list_nodes()
        critical_nodes = [node for node in nodes if "PROD" in node.facility_id]
        
        print(f"Monitoring {len(critical_nodes)} critical nodes...")
        
        while True:
            for node in critical_nodes:
                try:
                    ping_result = repo.ping_node(node.facility_id, count=1)
                    print(f"✅ {node.facility_id}: OK")
                except HinemosAPIError as e:
                    print(f"❌ {node.facility_id}: FAILED - {e}")
            
            time.sleep(60)  # 1分間隔
```

### 6. データエクスポート

```python
def export_inventory():
    """ノードインベントリをCSVエクスポートする例"""
    import csv
    from datetime import datetime
    
    with HinemosClient(**config) as client:
        repo = RepositoryAPI(client)
        
        # 全ノード情報取得
        nodes = repo.list_nodes()
        
        # CSVファイル作成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hinemos_inventory_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'facility_id', 'facility_name', 'ip_address', 'platform_family',
                'description', 'owner_role_id', 'valid', 'create_datetime'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for node in nodes:
                writer.writerow({
                    'facility_id': node.facility_id,
                    'facility_name': node.facility_name,
                    'ip_address': node.ip_address_v4 or node.ip_address_v6 or '',
                    'platform_family': node.platform_family or '',
                    'description': node.description or '',
                    'owner_role_id': node.owner_role_id or '',
                    'valid': node.valid,
                    'create_datetime': node.create_datetime or ''
                })
        
        print(f"Exported {len(nodes)} nodes to {filename}")
        return filename

def generate_topology_report():
    """ネットワークトポロジーレポート生成例"""
    with HinemosClient(**config) as client:
        repo = RepositoryAPI(client)
        
        # ファシリティツリー取得
        facility_tree = repo.get_facility_tree()
        all_facilities = repo.get_all_facilities()
        
        # スコープ別ノード集計
        scopes = [f for f in all_facilities if f.facility_type == FacilityType.SCOPE]
        nodes = [f for f in all_facilities if f.facility_type == FacilityType.NODE]
        
        print("=== Hinemos Topology Report ===")
        print(f"Total Scopes: {len(scopes)}")
        print(f"Total Nodes: {len(nodes)}")
        print()
        
        # スコープ別詳細
        for scope in scopes:
            scope_nodes = repo.list_nodes(parent_scope_id=scope.facility_id)
            print(f"Scope: {scope.facility_name} ({scope.facility_id})")
            print(f"  Nodes: {len(scope_nodes)}")
            
            # プラットフォーム別集計
            platforms = {}
            for node in scope_nodes:
                platform = node.platform_family or "Unknown"
                platforms[platform] = platforms.get(platform, 0) + 1
            
            for platform, count in platforms.items():
                print(f"    {platform}: {count}")
            print()
```

### 7. エラーハンドリングと再試行

```python
def robust_node_operations():
    """エラーハンドリングと再試行を含む堅牢な操作例"""
    import time
    from hinemos_mcp import HinemosAPIError
    
    def retry_operation(operation, max_retries=3, delay=1):
        """操作の再試行ラッパー"""
        for attempt in range(max_retries):
            try:
                return operation()
            except HinemosAPIError as e:
                if e.status_code == 401:
                    # 認証エラーは再試行しない
                    raise
                elif attempt == max_retries - 1:
                    # 最後の試行でも失敗
                    raise
                else:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # exponential backoff
    
    with HinemosClient(**config) as client:
        repo = RepositoryAPI(client)
        
        # 堅牢なノード作成
        def create_node_operation():
            return repo.create_node(
                facility_id="ROBUST_NODE01",
                facility_name="Robust Node 01",
                ip_address="192.168.1.150"
            )
        
        try:
            node = retry_operation(create_node_operation)
            print(f"Successfully created node: {node.facility_id}")
        except HinemosAPIError as e:
            print(f"Failed to create node after retries: {e}")
        
        # 堅牢なノード更新
        def update_node_operation():
            return repo.update_node(
                facility_id="ROBUST_NODE01",
                description="Updated with retry logic"
            )
        
        try:
            updated_node = retry_operation(update_node_operation)
            print(f"Successfully updated node: {updated_node.facility_id}")
        except HinemosAPIError as e:
            print(f"Failed to update node after retries: {e}")

def batch_operations_with_progress():
    """進捗表示付きバッチ操作例"""
    from tqdm import tqdm  # pip install tqdm
    
    with HinemosClient(**config) as client:
        repo = RepositoryAPI(client)
        
        # 大量ノード作成（進捗表示付き）
        nodes_to_create = [
            {
                "facility_id": f"BATCH{i:03d}",
                "facility_name": f"Batch Node {i:03d}",
                "ip_address": f"10.0.1.{i}"
            }
            for i in range(1, 101)  # 100ノード
        ]
        
        success_count = 0
        failed_count = 0
        
        with tqdm(total=len(nodes_to_create), desc="Creating nodes") as pbar:
            for node_spec in nodes_to_create:
                try:
                    repo.create_node(**node_spec)
                    success_count += 1
                except HinemosAPIError as e:
                    failed_count += 1
                    tqdm.write(f"Failed: {node_spec['facility_id']} - {e}")
                
                pbar.update(1)
                pbar.set_postfix({
                    'Success': success_count,
                    'Failed': failed_count
                })
        
        print(f"\nBatch operation completed:")
        print(f"  Success: {success_count}")
        print(f"  Failed: {failed_count}")
```

### 8. 設定管理

```python
def manage_configurations():
    """設定管理の例"""
    import json
    import os
    
    # 設定ファイルから読み込み
    def load_config():
        config_file = os.getenv("HINEMOS_CONFIG", "hinemos_config.json")
        with open(config_file, 'r') as f:
            return json.load(f)
    
    # 環境変数からの設定
    def config_from_env():
        return {
            "base_url": os.getenv("HINEMOS_URL", "http://localhost:8080/HinemosWeb/api"),
            "username": os.getenv("HINEMOS_USERNAME", "hinemos"),
            "password": os.getenv("HINEMOS_PASSWORD", "hinemos"),
            "verify_ssl": os.getenv("HINEMOS_VERIFY_SSL", "false").lower() == "true",
            "timeout": float(os.getenv("HINEMOS_TIMEOUT", "30.0"))
        }
    
    # 設定の検証
    def validate_config(config):
        required_fields = ["base_url", "username", "password"]
        for field in required_fields:
            if not config.get(field):
                raise ValueError(f"Missing required config: {field}")
        return config
    
    # 設定読み込みと使用
    try:
        config = load_config()
    except FileNotFoundError:
        config = config_from_env()
    
    config = validate_config(config)
    
    with HinemosClient(**config) as client:
        repo = RepositoryAPI(client)
        
        # 設定確認のための簡単なテスト
        facility_tree = repo.get_facility_tree()
        print(f"Connected to Hinemos: {facility_tree.facility_name}")
```

これらの例を参考に、具体的な運用要件に合わせてHinemos REST Clientを活用してください。