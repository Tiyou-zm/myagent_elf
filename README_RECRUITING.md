# MyAgent Elf

一个面向个人知识管理与本地检索场景的 AI 应用实验项目。

这个仓库目前聚焦三件事：

- 本地文件检索后端
- 搜索 / 对话入口能力
- Agent 能力实验与应用验证

## 项目定位

MyAgent Elf 不是单纯的聊天壳子，而是一个偏 **本地知识检索 + 应用编排** 的 AI 应用项目。核心目标是：

- 让用户为本地文件夹建立索引
- 通过自然语言检索文件与内容
- 返回命中片段、来源路径与说明
- 在检索基础上继续衔接对话与后续操作

这个项目更偏“能落地的个人知识工具”，而不是纯演示型 Demo。

## 亮点能力

- 基于 **SQLite + FTS5** 构建全文检索能力
- 提供 **FastAPI** 服务接口，便于前端、桌面端或脚本接入
- 支持索引、搜索、文件级搜索、对话搜索与文件打开等最小闭环
- 适合作为个人知识库、资料检索助手、轻量本地 RAG / Search 应用的基础骨架

## 当前最小 API

- `GET /healthz`
- `GET /api/v1/roots`
- `POST /api/v1/index`
- `POST /api/v1/search`
- `POST /api/v1/search/files`
- `POST /api/v1/chat`
- `POST /api/v1/open`

## 技术栈

- Python
- FastAPI
- SQLite
- FTS5
- PowerShell（本地脚本）

## 代码结构

- `src/index_service`
  - 索引服务主包
- `src/index_service/api.py`
  - FastAPI 路由
- `src/index_service/storage.py`
  - SQLite + FTS5 存储层
- `src/index_service/indexing.py`
  - 目录扫描与切块建索引
- `src/index_service/search.py`
  - 检索服务
- `tests/test_indexing.py`
  - 核心链路测试

## 本地运行

安装依赖：

```bash
python -m pip install -r requirements.txt
```

启动服务：

```bash
python -m uvicorn index_service.main:app --app-dir src --reload
```

或使用脚本：

```powershell
.\scripts\start_index_service.ps1 -Reload
```

执行最小验收：

```powershell
.\scripts\smoke_test_index_service.ps1
```

如需接入本地私有 LLM，可在仓库根目录配置 `.env.local`。

## 适合展示给招聘方的点

- 不是只调用模型 API，而是实际做了 **检索链路、数据存储与服务接口**
- 理解 **全文索引、查询匹配、检索流程** 等底层逻辑
- 能把 AI 应用需求拆成可运行的后端模块与最小产品闭环
- 具备把检索系统继续扩展到桌面端、前端或 Agent 工作流中的能力

## 适合的岗位方向

- AI 应用开发工程师
- Python 应用开发工程师
- 检索 / 知识库应用开发
- 工具型全栈工程师
- 实施开发 / 平台型研发

## 后续可扩展方向

- 更完整的前端 / 桌面端检索入口
- 多数据源索引与增量更新
- 更强的召回排序与结果解释
- 知识库问答与工作流编排

---

这个文件是面向招聘展示整理的说明；原 `README.md` 仍保留项目的学习推进上下文。