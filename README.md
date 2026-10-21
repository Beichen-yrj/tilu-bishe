# 铁路危险货物运输“双重预防机制”追责一体化信息平台

仓库按“站点”分包，两个子项目各自独立，互不交叉引用：

| 目录 | 内容 | 入口 |
| --- | --- | --- |
| `web/` | 网站部分：React + TypeScript + Vite 前端、FastAPI 后端、运维脚本、文档 | `web/启动项目.bat`（或 `cd web && npm run dev`） |
| `wxapp/` | 微信小程序部分：小程序前端 `frontend/`，后端 `backend/`（待接入） | 微信开发者工具打开 `wxapp/frontend/` |

## web/（网站）

```text
web/
├── frontend/           React 19 + TS + Vite（src、public、tests、vite.config.ts、tsconfig*.json）
├── backend/            FastAPI + SQLAlchemy（app、tests、requirements.txt、.env、docker-compose.yml）
├── deploy/             服务器运维：backup.sh、update.sh，测试脚手架在 deploy/tests/
├── scripts/            本地一键启动（启动项目.py / .bat）与数据库初始化包/
├── docs/               设计、指南、参考资料、图片素材
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
├── backend/            小程序后端（尚未实现，目录内 README 说明接入方式）
└── README.md
```

小程序后端目前为空，业务接口暂由 `web/backend` 提供；新增小程序专属接口时放在 `wxapp/backend/`，不要写进 `web/backend`。

## 更多文档

全部文档索引见 `web/docs/README.md`（设计、部署指南、数据库初始化、项目开发说明）。
