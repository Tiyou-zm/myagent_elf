# Project Context

## 项目名称

个人桌面宠物 Agent

## 当前阶段

`v1` 主仓库收口阶段

## 当前工作目录

- `C:\Users\Administrator\Desktop\agent_study`

## 主仓库职责

`agent_study` 当前只继续负责：

- 本地文件检索后端
- 搜索窗口
- Agent 能力实验
- 主学习仓库与主 Git 仓库

## 已独立分离的项目

### 绯铃桌宠本体

独立目录：

- `C:\Users\Administrator\Desktop\feiling`

独立上下文文件：

- `C:\Users\Administrator\Desktop\feiling\PROJECT_CONTEXT.md`

### EasyVtuber 导帧实验

独立目录：

- `C:\Users\Administrator\Desktop\EasyVtuber_inspect`

独立上下文文件：

- `C:\Users\Administrator\Desktop\EasyVtuber_inspect\PROJECT_CONTEXT.md`

## Git 仓库

- 本地仓库目录：`C:\Users\Administrator\Desktop\agent_study`
- 远程仓库：`git@github.com:Tiyou-zm/myagent_elf.git`
- 当前开发分支：`main`

## Git 连接方案

- fetch / push 默认走 SSH
- 当前机器通过 `ssh.github.com:443` 建立连接
- 这样做是为了绕开 HTTPS push 的偶发连接重置

## 协作约定

- 默认边做边学，不只停留在分析
- 每推进一小步，都要同步：
  - `README.md`
  - `PROJECT_CONTEXT.md`
  - `LEARNING_JOURNAL.md`
- 每完成一步有效推进，默认直接 `commit + push`
- 提交信息默认使用十几到二十字的简短中文简介

## 当前核心目标

把主仓库继续做成一个“本地文件检索助理”的主能力仓库：

- 用户指定若干本地文件夹
- 系统建立索引
- 用户用自然语言查找文件和内容
- 结果返回路径、命中片段、相关说明
- 支持一键打开文件或所在目录

## 为什么主仓库只保留这条线

- 这是当前最实用、最容易验证价值的 Agent 能力
- 桌宠本体已经分线，不再需要继续混在主仓库里
- `EasyVtuber` 导帧实验也已经分线，不再需要继续混在主仓库里

## 技术方向

- 检索服务：Python + FastAPI
- 存储：SQLite
- 全文检索：SQLite FTS5
- 搜索窗口：Electron / 前端壳
- 后续可扩展：
  - embedding
  - 向量检索
  - 对话搜索
  - Agent 编排

## 当前分层思路

1. 表现层：搜索窗口、结果卡片
2. 应用层：窗口控制、消息转发、打开文件
3. Agent 层：意图识别与流程编排
4. 检索层：扫描、解析、切块、索引、搜索、排序
5. 存储层：文件元数据、文本块、会话和偏好

## 当前边界

- 只索引用户明确授权的目录
- 回答必须附带来源文件路径
- 不把密码当普通记忆保存
- 私有密钥只放本地私有配置，不进 Git

## 当前服务骨架

- 包目录：`src/index_service`
- 最小接口：
  - `GET /healthz`
  - `GET /api/v1/roots`
  - `POST /api/v1/index`
  - `POST /api/v1/search`
  - `POST /api/v1/search/files`
  - `POST /api/v1/chat`
  - `POST /api/v1/open`

## 当前实现范围

- 扫描用户显式传入的目录
- 仅处理常见文本文件扩展名
- 把文本切块后写入 SQLite FTS5
- 支持内容检索
- 支持文件名/路径检索
- 支持基于文件大小和修改时间的简单增量跳过
- 支持查询当前登记过的索引根目录

## 当前下一步

- 继续收口本地检索、对话搜索和 Agent 方向
- 不再把绯铃桌宠和 `EasyVtuber` 实验细节混回主仓库

## 备注

如果后续要继续：

- 桌宠本体，请直接进入 `C:\Users\Administrator\Desktop\feiling`
- 导帧实验，请直接进入 `C:\Users\Administrator\Desktop\EasyVtuber_inspect`
