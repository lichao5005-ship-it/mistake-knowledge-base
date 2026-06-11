# 孩子错题本 — 项目上下文

## 项目概述
面向小学家庭的错题本 Web 应用。家长手机拍照录入错题，AI 自动识别判错分类，孩子 PC 端复习练习。支持语文、数学、英语三科。

## 技术栈
- 后端：Python FastAPI + SQLAlchemy + SQLite (WAL)
- 前端：Vue 3 + Vite + TypeScript SPA
- AI：通义千问 Qwen3.7-Plus（阿里云百炼平台，多模态）
- 认证：扫码登录（PC生成二维码，手机扫码确认）

## 架构原则
- 模块化：每个业务模块独立（router + service + models）
- 数据库模块独立，模块间通过 ID 松耦合
- AI 适配层统一（ai_client.py），换模型只改配置
- 可演进：第一版本地运行，后续可拆微服务

## 项目结构（当前阶段创建）
```
D:\mistake-knowledge-base\
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py
│   │   ├── shared/          # 共享基础设施
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── ai_client.py
│   │   └── modules/         # 业务模块
│   │       ├── knowledge/   # 知识点模块
│   │       ├── auth/        # 认证模块
│   │       ├── upload/      # 上传模块
│   │       ├── ocr/         # OCR识别模块
│   │       ├── question/    # 题库模块
│   │       ├── generate/    # 出题模块
│   │       └── analysis/    # 分析模块
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── views/
│       └── components/
└── docs/
```

## 运行方式
```
# 后端
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端（开发模式）
cd frontend && npm run dev
```

## AI 配置
- API: https://dashscope.aliyuncs.com/compatible-mode/v1
- 模型: qwen3.7-plus
- 适配层: app/shared/ai_client.py（统一接口，所有模块通过此接口调用AI）

## 权限与规则
- 我是 Hermes 军师调度下的云长（Claude Code），只管编码实现
- 所有改动按 Task 计划执行，无需额外询问
- 完成后运行 pytest 验证
- 代码写完后汇报用了哪些技能、发现了什么

## 实施计划
详见 docs/superpowers/plans/2026-06-11-mistake-notebook-implementation.md

## 12 Task 清单
| # | Task | Phase |
|---|------|-------|
| 1 | 项目脚手架搭建 | Phase 1 |
| 2 | 知识点模块 + 数据库模型 | Phase 1 |
| 3 | 认证模块 — QR 扫码登录 | Phase 1 |
| 4 | 上传模块 — 文件存储 + 二维码 | Phase 2 |
| 5 | OCR + AI 识别模块 | Phase 2 |
| 6 | 题库模块 — 错题入库与查询 | Phase 2 |
| 7 | Vue 3 前端搭建 + 基础页面 | Phase 3 |
| 8 | 前端录入与确认页面 | Phase 3 |
| 9 | 出题模块 — 相似题 + 模拟卷 | Phase 4 |
| 10 | 分析模块 — 统计 API | Phase 4 |
| 11 | 前端孩子端 — 复习模式 | Phase 4 |
| 12 | 集成测试与启动脚本 | Phase 5 |
