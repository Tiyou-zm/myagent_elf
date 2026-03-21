# agent_study

这是我们一起搭建个人桌面宠物 Agent 的学习仓库。

当前目标：

- 以“本地文件检索助理”为 `v1`
- 一边学习 Agent 设计，一边把能运行的项目做出来
- 每推进一步，都留下简洁但可回忆的共同笔记

仓库约定：

- `PROJECT_CONTEXT.md`：记录当前项目边界、架构和关键决定
- `LEARNING_JOURNAL.md`：按时间记录我们的学习日记
- 后续代码会按模块逐步加入，不一开始堆满
- 默认边做边学，每推进一小步都要把关键结论同步回文档
- 以后所有 Git 提交信息默认写成对本次工作的浓缩简介，控制在十几到二十字左右，不再每次单独提醒
- 以后每完成一步有效推进，默认直接 `commit + push`
- 如果换电脑继续学习，先读 `NEW_MACHINE_SETUP.md`

当前 `v1` 方向：

- 用户指定若干本地文件夹
- 系统建立索引
- 用户用自然语言查找文件和内容
- 结果返回文件路径、命中片段、相关说明
- 支持一键打开文件或所在目录

当前不做：

- 扫描整个电脑
- 自己保存密码
- 全自动执行复杂任务

下一步建议：

- 先搭 `Python` 索引服务骨架
- 再补最小检索 API
- 最后接桌面宠物界面

## 当前代码状态

已经补上第一版 `Python` 索引服务骨架：

- `src/index_service`：服务主包
- `src/index_service/api.py`：FastAPI 路由
- `src/index_service/storage.py`：SQLite + FTS5 存储层
- `src/index_service/indexing.py`：目录扫描与切块建索引
- `src/index_service/search.py`：最小检索服务
- `tests/test_indexing.py`：核心链路测试

当前已经补上的 `v1` 实用能力：

- 内容检索：按文本内容查命中片段
- 文件检索：按文件名/路径模糊匹配查文件
- 增量索引：未变化文件会跳过重建
- 根目录查询：可查看当前登记过的索引目录

## 计划中的最小 API

- `GET /healthz`
- `GET /api/v1/roots`
- `POST /api/v1/index`
- `POST /api/v1/search`
- `POST /api/v1/search/files`

## 本地运行

先安装依赖：

```bash
python -m pip install -r requirements.txt
```

启动服务：

```bash
python -m uvicorn index_service.main:app --app-dir src --reload
```

## 当前接口说明

`POST /api/v1/index`

- 输入：用户授权的目录列表
- 输出：扫描文件数、实际重建数、未变化跳过数、跳过文件数、删除文件数

`POST /api/v1/search`

- 作用：按文件内容搜索

`POST /api/v1/search/files`

- 作用：按文件名或路径搜索

`GET /api/v1/roots`

- 作用：查看当前已经登记过的索引根目录

## 今日学习结论

今天围绕索引服务把几个最关键的底层概念讲通了：

- 增量索引：文件没变就跳过重建
- 文件名检索和内容检索要分两条路
- 内容检索不是直接搜整篇文件，而是搜切块后的文本
- `storage.py` 的职责是把所有直接碰 SQLite 的事情收口起来
- `build_index()` 的骨架是：没变就跳过，变了就读取、切块、入库
- 切块主规则是按字符数控制大小，但按行组织内容
- 文件一旦被判定为有变化，当前策略是整文件替换文本块，而不是块级增量更新
- 内容搜索先从 FTS 文本块索引开始查，再回头拼接文件信息
- `snippet` 负责展示命中片段，`bm25` 负责给结果打分排序
- 搜索结果既要让人看懂，也要能定位，所以同时返回片段和位置信息
- 当前最缺的不是单个函数细节，而是整机图、前后端衔接和从“代码存在”到“软件可用”的落地感
- 下一阶段应减少逐行细讲，转向整体闭环理解，并把 Python 服务真正跑起来
- 当前 `v1` 闭环可以概括成：
  - 用户授权目录
  - Python 服务建索引
  - 用户发起搜索
  - Python 返回结构化结果
  - Electron 展示结果
  - 用户执行打开文件或目录
- 现阶段核心仍然是先把本地文件检索这个“发动机”做稳，Electron 属于后续交互外壳

今天的学习方式也定下来了：

- 先把功能做成最小可用版本
- 再用已经写出来的代码反过来教学
- 讲解时优先用人话和精确可点的文件链接

## Git 现状

这台机器当前 GitHub 推送已切到 `SSH over 443`：

- 仓库远程地址使用 `git@github.com:Tiyou-zm/myagent_elf.git`
- `C:\Users\Administrator\.ssh\config` 已配置走 `ssh.github.com:443`
- 后续优先用 SSH 推送，不再默认依赖 HTTPS push

## 固定启动与验收

今天已经把 Python 服务的启动和最小验收固定成脚本：

- `scripts/start_index_service.ps1`
- `scripts/smoke_test_index_service.ps1`

常用方式：

```powershell
.\scripts\start_index_service.ps1 -Reload
```

服务启动后，跑一遍最小闭环验证：

```powershell
.\scripts\smoke_test_index_service.ps1
```

这会依次验证：

- `/healthz`
- `/api/v1/index`
- `/api/v1/search`
- `/api/v1/search/files`
- `/api/v1/roots`

这一步的意义是把项目从“代码存在”进一步固定到“服务可启动、接口可重复验证”。
