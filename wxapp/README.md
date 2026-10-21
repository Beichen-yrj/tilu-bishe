# wxapp · 微信小程序部分

本目录只放小程序相关内容，与 `web/`（网站）完全分离，互不引用。

```text
wxapp/
├── frontend/   小程序前端（微信开发者工具工程，当前为 Miniprogram-24blockchain1-Fianl）
└── backend/    小程序后端（尚未实现）
```

## 当前状态

- `frontend/`：期末作品工程骨架，尚无业务代码。
- `backend/`：只有说明文件，没有服务端代码。小程序的登录、隐患数据等接口目前可直接复用 `web/backend` 的 FastAPI 服务（`/api/*`，默认 `http://127.0.0.1:8000`）。

## 约定

- 小程序专属接口写在 `wxapp/backend/`，不要加进 `web/backend/`，避免两套客户端互相影响。
- 小程序默认请求地址放在 `frontend/**/config.js` 或 `app.js` 常量里，发布前改为 HTTPS 域名。
