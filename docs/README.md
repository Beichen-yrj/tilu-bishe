# 项目文档

文档独立于代码目录存放，按客户端分成两套，互不混放：

```text
docs/
├── web-docs/       网站（web/）的需求、设计、指南、参考资料与素材
└── wxapp-docs/     小程序（wxapp/）的文档
```

| 目录 | 对应代码 | 内容 |
| --- | --- | --- |
| `web-docs/` | `web/` | 系统需求说明书、架构设计、项目开发说明、操作文档、数据库初始化说明、参考资料、图片素材 |
| `wxapp-docs/` | `wxapp/` | 小程序需求与接口约定（当前只有占位说明） |

- web 文档索引：`docs/web-docs/README.md`
- 小程序文档索引：`docs/wxapp-docs/README.md`
- 代码结构说明：仓库根 `README.md`
