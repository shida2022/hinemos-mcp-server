# Tests

このディレクトリには、Hinemos MCP Claudeプロジェクトのテストファイルが含まれています。

## テストファイル

### 包括的テスト

- **`../comprehensive_test.py`** - 全機能の包括的テスト
  - 24のメソッドをテスト
  - 自動リソースクリーンアップ
  - 詳細なテスト結果レポート

### 今後のテスト

このディレクトリには将来的に以下のテストが追加される予定です：

- **単体テスト** - 各コンポーネントの詳細テスト
- **統合テスト** - API連携テスト
- **パフォーマンステスト** - 性能測定
- **MCPテスト** - MCP統合後のテスト

## テスト実行

### 包括的テスト実行

```bash
# メインディレクトリから実行
python3 comprehensive_test.py
```

### 今後のpytestサポート

```bash
# pytest環境のセットアップ (将来実装予定)
pip install pytest pytest-asyncio

# テスト実行 (将来実装予定)
python3 -m pytest tests/ -v
```

## テスト環境

### 必要な環境

- Python 3.7+
- httpx, pydantic
- 動作中のHinemosサーバー

### 設定

テスト実行前に、`comprehensive_test.py`の`CONFIG`セクションでHinemosサーバーの接続情報を設定してください：

```python
CONFIG = {
    "base_url": "http://your-hinemos:8080/HinemosWeb/api",
    "username": "your-username",
    "password": "your-password",
    "verify_ssl": False
}
```

## 注意事項

- テストは実際のHinemosサーバーに対して実行されます
- テスト用リソース（`TEST_NODE_*`, `TEST_SCOPE_*`）は自動的にクリーンアップされます
- テスト実行には適切な権限を持つHinemosユーザーが必要です