# wxapp/backend · 小程序后端（占位）

当前没有实现代码。小程序现阶段直接调用 `web/backend`（FastAPI，`/api/*`）的接口。

需要独立后端时，在此目录按 `web/backend` 的结构新建：

```text
wxapp/backend/
├── app/             FastAPI 应用（main.py、models.py、schemas.py、auth.py…）
├── tests/
├── requirements.txt
└── .env.example
```

要求：

- 独立虚拟环境 `wxapp/backend/.venv`，不复用 `web/backend/.venv`；
- 独立数据库或独立 schema，避免与网站业务数据互相覆盖；
- 小程序侧只通过 HTTPS 域名访问，不在客户端写死数据库口令。
