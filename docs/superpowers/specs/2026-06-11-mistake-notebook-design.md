# 孩子错题本 — 设计规格文档

## 概述

一个面向小学家庭的错题本 Web 应用，支持语文、数学、英语三科错题管理。家长通过手机拍照/上传文件录入错题，AI 自动识别、判错、分类，孩子通过 PC 端复习和练习。

## 技术选型

| 项目 | 选择 |
|------|------|
| 后端框架 | Python FastAPI |
| 前端框架 | Vue 3（独立 SPA） |
| 数据库 | SQLite（WAL 模式，第一版）→ PostgreSQL（后续扩展） |
| ORM | SQLAlchemy |
| AI 模型 | 通义千问 Qwen3.7-Plus（阿里云百炼平台） |
| API Key | sk-fe3d16d1d5624772869d4669842f5cf6 |
| 运行环境 | Windows 11 本地网页服务，局域网内手机可访问 |

## 架构原则

- **模块化** — 每个业务模块独立（router + service + models），修改不影响其他模块
- **数据库模块独立** — 共享数据集中管理，各模块数据表自包含
- **ID 松耦合** — 模块间通过 ID 引用，不直接访问对方内部表
- **AI 适配层** — 统一 `ai_client.py`，换模型只改配置
- **可演进** — 第一版本地运行，后续可拆微服务

## 模块结构

```
mistake-book/
├── shared/                     # 共享基础设施
│   ├── database.py             # 数据库引擎（独立模块）
│   ├── config.py               # 全局配置
│   └── ai_client.py            # AI API 统一适配层
│
├── modules/
│   ├── auth/                   # 认证模块（扫码登录）
│   │   ├── router.py
│   │   ├── service.py
│   │   └── models.py
│   ├── upload/                 # 上传模块（图片/PDF/Word）
│   │   ├── router.py
│   │   ├── service.py
│   │   └── models.py
│   ├── ocr/                    # OCR 识别模块
│   │   ├── router.py
│   │   ├── service.py          # 调用 AI API
│   │   └── models.py
│   ├── question/               # 题库模块（错题管理）
│   │   ├── router.py
│   │   ├── service.py
│   │   └── models.py
│   ├── generate/               # 出题模块（相似题/模拟卷）
│   │   ├── router.py
│   │   ├── service.py
│   │   └── models.py
│   ├── analysis/               # 分析模块（统计+报告）
│   │   ├── router.py
│   │   ├── service.py
│   │   └── models.py
│   └── knowledge/              # 知识点模块（共享）
│       ├── router.py
│       ├── service.py
│       └── models.py
│
└── frontend/                   # Vue 3 前端（独立）
    └── src/
```

## 数据库设计

### 共享数据层（shared/models.py）

- **subjects** — 科目表（语文/数学/英语）：id, name, icon, created_at
- **knowledge_points** — 知识点树（树形结构）：id, subject_id, name, parent_id, level, sort_order
- **users** — 用户表：id, role(家长/孩子), nickname, avatar
- **class_schedule** — 年级/学期配置：id, grade, semester, is_current

### 录入模块（upload + ocr）

- **upload_sessions** — 录入会话：id, user_id, subject_id, source_type, status, created_at
- **source_files** — 原始文件：id, session_id, file_name, file_path, file_type, page_count
- **ocr_results** — OCR 识别结果：id, source_file_id, page_number, raw_text, structured_data, status, confidence, processing_time
- **ai_corrections** — AI 判错结果：id, ocr_result_id, question_number, student_answer, is_correct, correct_answer, error_type, ai_analysis

### 题库模块（question）

- **questions** — 题目主表（核心）：id, subject_id, knowledge_point_id, question_type, content(JSON), answer, difficulty, source_file_id, source_page, tags, status, created_at
- **mistake_records** — 错题记录（核心）：id, question_id, student_answer, is_correct, error_type, ai_error_analysis(JSON), corrected_count, last_wrong_at
- **question_images** — 题目图片资源：id, question_id, image_type, image_path

### 出题模块（generate）

- **similar_questions** — 相似题：id, original_question_id, similar_question_id, similarity_type, ai_generated, created_at
- **exam_papers** — 模拟试卷：id, user_id, subject_id, title, question_ids(JSON), total_score, difficulty, duration_minutes, status, created_at
- **practice_results** — 做题记录：id, question_id, student_answer, is_correct, source, time_spent, created_at

### 分析模块（analysis）

- **error_analysis** — 出错点分析报告：id, user_id, subject_id, report_date, weak_knowledge_points(JSON), error_distribution(JSON), trend_data(JSON), suggestions(JSON)
- **study_reports** — 学习周报/月报：id, user_id, report_type, summary(JSON), generated_at

## 核心流程：手机拍照录入

1. **PC 端** → 打开录入页 → 生成二维码（含 session ID）
2. **手机端** → 扫码 → 选科目（语文/数学/英语）→ 拍照/从相册选图
3. **裁剪** → 拖拽框选有效题目区域（支持多次裁剪，一张图切多题）
4. **AI 处理** → 发送到 Qwen3.7-Plus → 分三步完成：
   - Step 1: OCR 识别（图片 → 结构化 JSON，含题号、内容、空白位置）
   - Step 2: AI 判错 + 分类（判断对错、标注错误类型、关联知识点）
   - Step 3: 正解分析（正确答案 + 小学生能懂的解题思路）
5. **PC 端确认** → 家长审核 AI 结果（可编辑修正）→ 一键入库（存入 questions + mistake_records）

## AI 模块设计

### 统一适配层（ai_client.py）

- 通用接口：`call_ai(model, prompt, image) → JSON`
- 支持 retry / fallback / token 统计
- 所有模块通过此接口调用 AI，换模型只改配置

### OCR 识别策略

- 直接发送裁剪图片给多模态模型，一次性完成"看到→理解→结构化"
- 数学公式用 LaTeX 格式输出
- 手写中文字优先识别

### 判错策略

- 逐题判断：学生答案 vs 标准答案
- 错误类型分类：粗心 / 概念不清 / 审题错误 / 计算错误 / 未作答
- 返回结构化 JSON，前端直接渲染

### 出题策略

- **相似题**：基于原题知识点+难度，AI 生成同类题（3 道/次）
- **模拟卷**：选择科目+知识点+题量，AI 组卷
- **错题重做卷**：将某段时间内错题打包重做

## 前端页面

### PC 端（家长管理）

| 路由 | 页面 | 功能 |
|------|------|------|
| / | 首页 | 三科概览、快捷入口 |
| /upload | 录入页 | 二维码 + 文件列表 |
| /confirm/:id | 确认入库 | AI 结果审核 + 编辑 + 入库 |
| /questions | 错题集 | 筛选/查看/管理错题 |
| /generate | 出题页 | 相似题 + 模拟卷 + 错题重做 |
| /analysis | 统计页 | 趋势/知识点/错误类型/学习日历 |
| /settings | 设置 | 用户/年级/API Key 配置 |

### 手机端（拍照录入）

- /scan — 扫码页
- /upload — 选科→拍照→裁剪→提交
- /processing — 处理中（显示进度，可后台）
- /done — 完成页（提示去 PC 端确认）

### 孩子端

- 切换角色进入"孩子模式"：大字号、色彩丰富、操作简单
- 三科入口 → 选择要复习的科目
- 两种复习模式：逐题复习 / 做题模式
- 完成复习后：显示激励反馈（星星、进度条）

## 统计功能

第一版优先实现的三个核心视图：

1. **三科正确率趋势（折线图）** — 近30天每日正确率变化
2. **薄弱知识点排行（柱状图）** — 按科目显示出错最多的知识点 TOP 5
3. **错误类型分布（饼图）** — 粗心/概念不清/审题错误/计算错误 占比

后续迭代：
4. 学习日历（热力图）
5. 错题复做正确率
6. AI 学习周报/月报

## 学习激励（游戏化）

- 连续打卡得星星
- 错题清零进度条
- 知识点掌握等级（待加强 → 已掌握 → 小达人）

## 扩展性设计

### 单用户 → 多用户并发

- 数据库：SQLite WAL → PostgreSQL（只改 database.py 连接串，模块代码不动）
- 图片存储：本地磁盘 → 按用户分目录 / 对象存储
- 服务器：单进程 → gunicorn + uvicorn workers
- AI 调用：同步 → Celery 任务队列
- 认证：简易 token → JWT + Redis 会话

### 模块 → 微服务

每个模块是独立 package（router + service + models），将来拎出去变成独立服务只需改路由注册。
