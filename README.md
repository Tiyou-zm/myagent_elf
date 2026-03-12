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

今天的学习方式也定下来了：

- 先把功能做成最小可用版本
- 再用已经写出来的代码反过来教学
- 讲解时优先用人话和精确可点的文件链接

## Git 现状

这台机器当前 GitHub 推送已切到 `SSH over 443`：

- 仓库远程地址使用 `git@github.com:Tiyou-zm/myagent_elf.git`
- `C:\Users\Administrator\.ssh\config` 已配置走 `ssh.github.com:443`
- 后续优先用 SSH 推送，不再默认依赖 HTTPS push
