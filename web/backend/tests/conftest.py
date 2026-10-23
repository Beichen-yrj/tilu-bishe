"""pytest 夹具：切换到临时 SQLite、注入测试密钥并修正导入路径。"""

from __future__ import annotations

import os
import sys
from pathlib import Path


TEST_DB = Path(__file__).with_name("test.db")
sys.path.insert(0, str(Path(__file__).parents[1]))
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["JWT_SECRET"] = "test-secret-at-least-thirty-two-characters"
