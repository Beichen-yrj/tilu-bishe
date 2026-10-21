# 铁路危险货物运输“双重预防机制”追责一体化信息平台

仓库按“站点”分包，代码与文档分开存放：

```text
.
├── web/          网站（前端 + 后端 + 脚本）
├── wxapp/        微信小程序（前端 + 后端占位）
├── docs/         文档：web-docs/ 与 wxapp-docs/
├── README.md
└── .gitignore / .gitattributes / .vscode / AGENTS.md
```

## web/（网站）

```text
web/
├── frontend/           React 19 + TS + Vite（src、public、tests、vite.config.ts、tsconfig*.json）
├── backend/            FastAPI + SQLAlchemy（app、tests、requirements.txt、.env、docker-compose.yml）
├── scripts/            本地一键启动（启动项目.py / .bat）与数据库初始化包/
├── package.json        统一构建入口：dev / build / lint / typecheck / test / test:backend
├── pyrightconfig.json  后端类型检查配置（指向 backend/）
└── 启动项目.bat        双击启动前后端
```

```bash
cd web
npm run dev            # 只起前端（Vite 5173，/api 代理到 8000）
npm run build          # 前端构建，产物 web/frontend/dist
npm test               # 前端领域逻辑测试
npm run test:backend   # 后端 pytest
npm run typecheck      # tsc -b
```

后端单独启动：`cd web/backend && .venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000`。

## wxapp/（小程序）

```text
wxapp/
├── frontend/           小程序源码（微信开发者工具工程）
├── backend/            小程序后端（占位，暂复用 web/backend 的 /api/* 接口）
└── README.md
```

小程序专属接口写在 `wxapp/backend/`，不要加进 `web/backend/`。

## docs/（文档）

```text
docs/
├── web-docs/           网站设计、指南、参考资料、图片素材
└── wxapp-docs/         小程序文档
```

- web 文档索引：`docs/web-docs/README.md`
- 小程序文档索引：`docs/wxapp-docs/README.md`
