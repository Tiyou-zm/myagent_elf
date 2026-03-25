# agent_study

这是我们一起搭建个人桌面宠物 Agent 的主学习仓库。

当前这个仓库只继续负责三件事：

- 本地文件检索后端
- 搜索窗口
- Agent 能力实验

## 已独立出去的项目

### 绯铃桌宠本体

独立目录：

- `C:\Users\Administrator\Desktop\feiling`

从当前版本开始，绯铃桌宠的这些内容都不再继续记在主仓库里：

- 桌宠本体交互
- WPF 桌宠壳
- 素材整理
- 待机精灵帧
- 移动行为

直接看：

- `C:\Users\Administrator\Desktop\feiling\README.md`
- `C:\Users\Administrator\Desktop\feiling\run_feiling.bat`
- `C:\Users\Administrator\Desktop\feiling\stop_feiling.bat`

### EasyVtuber 导帧实验

独立目录：

- `C:\Users\Administrator\Desktop\EasyVtuber_inspect`

从当前版本开始，`EasyVtuber` 的这些内容也不再继续细记在主仓库里：

- 模型与环境补齐
- 待机导帧实验
- sprite sheet 预览
- 性能与导出验证

直接看：

- `C:\Users\Administrator\Desktop\EasyVtuber_inspect\README_LOCAL.md`
- `C:\Users\Administrator\Desktop\EasyVtuber_inspect\PERF_OPT_PROGRESS.md`
- `C:\Users\Administrator\Desktop\EasyVtuber_inspect\export_feiling_idle_frames.ps1`

## 主仓库当前目标

以“本地文件检索助理”为 `v1`：

- 用户指定若干本地文件夹
- 系统建立索引
- 用户用自然语言查找文件和内容
- 结果返回路径、命中片段、相关说明
- 支持一键打开文件或所在目录

## 当前代码范围

- `src/index_service`
  - Python 索引服务主包
- `src/index_service/api.py`
  - FastAPI 路由
- `src/index_service/storage.py`
  - SQLite + FTS5 存储层
- `src/index_service/indexing.py`
  - 目录扫描与切块建索引
- `src/index_service/search.py`
  - 最小检索服务
- `tests/test_indexing.py`
  - 核心链路测试

## 当前最小 API

- `GET /healthz`
- `GET /api/v1/roots`
- `POST /api/v1/index`
- `POST /api/v1/search`
- `POST /api/v1/search/files`
- `POST /api/v1/chat`
- `POST /api/v1/open`

## 本地运行

安装依赖：

```bash
python -m pip install -r requirements.txt
```

启动服务：

```bash
python -m uvicorn index_service.main:app --app-dir src --reload
```

或者直接用脚本：

```powershell
.\scripts\start_index_service.ps1 -Reload
```

跑一遍最小验收：

```powershell
.\scripts\smoke_test_index_service.ps1
```

如果要接本地私有 LLM 配置，可以在仓库根目录放不会进 Git 的 `.env.local`：

```text
FEILING_LLM_BASE_URL=...
FEILING_LLM_API_KEY=...
FEILING_LLM_MODEL=...
```

## 仓库约定

- `PROJECT_CONTEXT.md`
  - 记录当前项目边界、架构和关键决定
- `LEARNING_JOURNAL.md`
  - 记录按时间推进的学习日志
- 默认边做边学
- 每完成一步有效推进，默认直接 `commit + push`
- 提交信息默认写成十几到二十字的浓缩简介
- 换电脑继续时，先读 `NEW_MACHINE_SETUP.md`

## 当前说明

主仓库现在只保留：

- 检索与搜索主线
- 必要的分线索引
- 不再承载绯铃桌宠和 `EasyVtuber` 实验的详细过程日志
