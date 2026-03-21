# Project Context

## 项目名称

个人桌面宠物 Agent

## 当前阶段

`v1` 骨架搭建阶段

## 当前工作目录

`C:\\Users\\Administrator\\Desktop\\agent_study`

## Git 仓库

- 本地仓库目录：`C:\\Users\\Administrator\\Desktop\\agent_study`
- 远程仓库：`https://github.com/Tiyou-zm/myagent_elf.git`
- 约定：后续开发默认都在这个目录内进行
- 当前 `origin` 实际推送地址：`git@github.com:Tiyou-zm/myagent_elf.git`

## 协作约定

- 默认工作方式是边做边学，而不是只闷头往前写功能
- 每推进一小步，都要把结果和关键认识同步到 `README.md`、`PROJECT_CONTEXT.md`、`LEARNING_JOURNAL.md`
- 以后所有 Git 提交信息默认写成对本次工作的浓缩简介，控制在十几到二十字左右，不需要用户重复提醒
- 以后每完成一步有效推进，默认直接执行 `commit + push`
- 如果在新电脑上继续学习，优先按 `NEW_MACHINE_SETUP.md` 恢复环境和上下文

## 当前 Git 同步状态

- 远程默认分支：`main`
- 本地工作分支：`main`
- 本地保留一个历史备份分支：`codex/master-pre-main-sync`
- 当前机器已切到 `SSH over 443` 推送 GitHub
- 之前 smart-HTTP 不稳定时，远程内容曾通过 GitHub API 兜底同步
- 这意味着：
  - 远程文件内容已经同步
  - 本地开发统一在 `main` 上继续
  - 历史整理时保留备份分支，避免丢失此前本地提交

## 当前 Git 连接方案

- fetch / push 默认走 SSH，而不是 HTTPS
- SSH 主机配置写在 `C:\\Users\\Administrator\\.ssh\\config`
- GitHub 主机名仍写作 `github.com`，但通过 `ssh.github.com:443` 建立连接
- 这样做是为了绕开本机对 HTTPS push 的偶发连接重置

## v1 核心目标

把项目做成一个“本地文件检索助理”：

- 帮用户从指定目录中找文件
- 帮用户从文件内容中找信息
- 帮用户总结某个文件
- 支持打开文件或打开所在目录

## 为什么先这样做

- 这是最实用、最容易验证价值的 Agent 能力
- 真正的桌面宠物可以先作为交互外壳，核心难点是“找得准”
- 这个方向后续可以自然扩展到提醒、记忆、工作流、密码管理器接入

## 技术方向

- 桌面端：Electron
- Agent 服务：Python + FastAPI
- 存储：SQLite
- 全文检索：SQLite FTS5
- 后续可扩展语义检索：embedding + 向量存储

## 分层思路

1. 表现层：桌面宠物、聊天框、结果卡片
2. 应用层：窗口控制、消息转发、打开文件
3. Agent 层：意图识别与流程编排
4. 检索层：扫描、解析、切块、索引、搜索、排序
5. 存储层：文件元数据、文本块、会话和偏好

## 重要边界

- 只索引用户明确授权的目录
- 回答必须附带来源文件路径
- 不把密码当普通记忆来保存
- 密码管理后续只考虑接入专业密码管理器，不自造明文存储

## 当前下一步

已进入 `Python` 索引服务骨架实现，当前先把“扫描目录 -> 建索引 -> 查询”这条链路立起来。

## 当前服务骨架

- 包目录：`src/index_service`
- API：FastAPI
- 存储：SQLite + FTS5
- 当前最小接口：
  - `GET /healthz`
  - `GET /api/v1/roots`
  - `POST /api/v1/index`
  - `POST /api/v1/search`
  - `POST /api/v1/search/files`

## 当前实现范围

- 扫描用户显式传入的目录
- 仅处理一批常见文本文件扩展名
- 把文本切块后写入 SQLite FTS5
- 支持基于 FTS 的最小内容检索
- 支持基于路径/文件名的最小文件检索
- 支持基于文件大小和修改时间的简单增量跳过
- 支持查询当前登记过的索引根目录

## 今天补上的学习共识

- 增量索引当前只做到文件级，不做到块级
- 文件名检索和内容检索虽然都叫搜索，但底层搜索对象不同
- 文本切块的主要价值是让结果更可定位、更可展示
- `storage.py` 属于存储层，负责屏蔽 SQLite 细节
- `build_index()` 是索引总调度：校验目录、遍历文件、判断变化、读取、切块、入库
- 切块采用“按字符数控制块大小、按行保留自然边界”的策略
- 相邻块之间保留少量重叠内容，用来维持上下文连续性
- 内容搜索从 `document_chunks_fts` 出发，而不是从 `files` 表出发
- 当前搜索结果同时包含展示字段和定位字段：
  - 展示字段：`snippet`
  - 定位字段：`chunk_index`、`start_line`、`end_line`
- 当前 `v1` 的整机闭环已经明确：
  - 用户授权目录
  - Python 建索引
  - 用户搜索
  - Python 返回结构化命中结果
  - Electron 展示与执行打开动作
- 当前更像是“后端检索发动机已成形”，而不是“桌面产品已完成”

## 下一步

- 先补齐 `v1` 整机图认知：用户目录授权、索引服务、搜索结果、桌面端展示如何串成闭环
- 讲清 Electron 和 Python 服务为什么分层，以及两者怎么通信
- 把 Python 服务真正启动并测通，跨过“代码存在”到“软件可用”的那一步
- 补更稳妥的文件解析策略
- 优化文件检索与内容检索的排序
- 增加文件摘要/结果重排
- 再接 Electron 侧调用链路

## 2026-03-21 进展补充

当前 Python 服务已经完成一次真实启动与接口实测，说明后端状态已经从“只写出了代码”推进到“本地可运行”。

本次固定下来的运行入口：

- `scripts/start_index_service.ps1`
- `scripts/smoke_test_index_service.ps1`

本次已经实测通过的接口：

- `GET /healthz`
- `POST /api/v1/index`
- `POST /api/v1/search`
- `POST /api/v1/search/files`
- `GET /api/v1/roots`

因此，下一步不再是“先证明服务能不能跑”，而是“基于稳定启动/验收入口继续推进后端体验或接 Electron”。
