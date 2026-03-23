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
  - `POST /api/v1/open`

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

## 2026-03-21 接口体验补充

当前 API 已经开始从“纯后端返回结构”往“更适合前端直接消费”推进：

- 健康检查补了 `message`
- 索引接口补了摘要式 `message`
- 搜索接口补了 `message` 和 `total_results`
- `400 Bad Request` 改成统一结构化错误体

为了给这一步兜底，测试层也补上了 API 级用例，而不再只停留在服务层测试。

## 2026-03-21 最小前端壳补充

在正式开始 Electron 之前，先补了一个非常薄的前端调用壳，用来验证前后端衔接方式：

- 静态页：`playground/index.html`
- 启动脚本：`scripts/start_frontend_shell.ps1`

后端同时补了本地开发用 CORS，仅放行：

- `http://127.0.0.1:4173`
- `http://localhost:4173`

这样当前已经可以先用网页壳把“索引 -> 搜索 -> 查看结果”整条调用链点通，再进入正式 Electron。

## 2026-03-21 本地动作链补充

当前最小前端壳已经不只是“查到结果”，还可以通过后端动作接口触发：

- 打开文件
- 打开所在目录

因此当前闭环已经从“能调用搜索”推进到“能从结果触发本地动作”。

## 2026-03-21 最小 Electron 壳补充

当前已经补上一个最小 Electron 工程，用来把现有前端壳正式放进桌面窗口：

- `package.json`
- `electron/main.js`
- `scripts/start_electron_shell.ps1`

当前策略很克制：

- 先不引 React / Vite
- Electron 先只负责窗口宿主
- 前端壳继续沿用现有 `playground/index.html`
- 后端仍然独立运行

因为 Electron 通过 `file://` 加载页面，后端 CORS 也同步补了 `Origin: null` 的放行。

## 2026-03-21 统一启动编排补充

当前已经补上最小桌面栈的统一启动与停止脚本：

- `scripts/start_desktop_stack.ps1`
- `scripts/stop_desktop_stack.ps1`

这套脚本当前负责：

- 拉起 Python 后端
- 等待健康检查通过
- 拉起 Electron 壳
- 记录运行状态
- 统一停止整套栈

这意味着当前桌面端开发入口已经从“记多条命令”推进到“一条启动，一条停止”。

## 2026-03-23 窗口角色补充

当前 Electron 不再只是一整个搜索窗口，而是已经开始按产品形态拆角色：

- 桌宠入口壳：
  - `electron/pet.html`
  - 小型、常驻、负责唤起搜索
- 搜索结果窗口：
  - 继续沿用 `playground/index.html`
  - 负责完整搜索交互

这个拆分的意义是避免后面把“桌宠”和“功能窗口”混成一个形态。

## 2026-03-23 桌宠主次补充

当前产品权重明确调整为：

- 主体：桌宠常驻形态
- 功能：搜索只是桌宠的一项能力
- 底座：Python 检索服务继续作为能力引擎

对应到当前实现：

- Electron 启动时先只创建桌宠窗口
- 搜索窗口由桌宠主动唤起时再创建和展示
- 桌宠窗口负责表达状态、保留入口，而不承担完整搜索面板职责

## 2026-03-23 桌面栈稳定性补充

统一停机脚本本轮额外补了两点：

- 停止目标进程后显式等待退出
- 重试检查后端端口是否仍在监听

目标是保证 `scripts/stop_desktop_stack.ps1` 真正对应“整套桌面栈已停干净”。

## 2026-03-23 桌宠 OC 补充

当前桌宠角色已开始从“功能入口壳”进入“有明确人格的 OC”阶段。

角色方向：

- 名字：绯铃
- 类型：白尾灵狐拟人桌宠
- 核心性格：安静、细心、很爱主人、偶尔腹黑毒舌
- 产品气质：桌宠是主体，搜索只是她暂时已具备的一项能力

已固化的角色素材文档：

- `OC_PROFILE.md`
- `OC_ART_PROMPT.md`
- `PET_ANIMATION_PLAN.md`
- `OC_VISUAL_LOCK.md`
- `OC_ART_MASTER.md`
- `FULLBODY_MASTER_BRIEF.md`
- `STATE_SET_BRIEF.md`
- `FIRST_ANIMATION_BRIEF.md`

当前针对 AI 出图阶段新增的关键约束：

## 2026-03-23 绯铃素材目录固化

当前不再把绯铃素材停留在“聊天里确认过几张图”的状态，而是正式在仓库里建立固定目录：

- `assets/characters/feiling/base/`
- `assets/characters/feiling/states/`
- `assets/characters/feiling/animations/`
- `assets/characters/feiling/references/`

并新增：

- `assets/characters/feiling/README.md`
- `assets/characters/feiling/ASSET_MANIFEST.md`

当前阶段判断：

- 全身母版已经足够进入接入阶段
- 第一批状态图已经基本可用
- 后续研发应优先围绕这批固定素材做接入，而不是继续无边界重画

当前最实际的产品节奏：

1. 先把当前母版和状态图落盘到素材目录
2. 先把 `idle / happy / thinking / smug` 接到桌宠里
3. 再补 `blink / idle_breath`
4. 最后视接入效果补 `confused`

## 2026-03-24 绯铃静态状态接入

当前阶段已经从“素材整理”推进到“静态状态真正接进桌宠壳”：

- 绯铃素材已按标准文件名落到：
  - `assets/characters/feiling/base/`
  - `assets/characters/feiling/states/`
  - `assets/characters/feiling/references/source_exports/`
- Electron 桌宠壳现在直接引用绯铃状态图
- 主进程维护当前桌宠状态，桌宠壳可根据状态切图

当前最小状态机：

1. 默认 `idle`
2. 打开搜索窗口时 `happy_soft`
3. 收起搜索窗口时回到 `idle`
4. 桌宠壳内部保留静态状态预览能力，用于开发确认素材

这一步的意义：

- 桌宠第一次真正从“有角色设定”推进到“角色图已经进入运行时界面”
- 后续接动画时，不需要再从 0 搭角色渲染入口
- 当前绯铃素材目录和原始导出图文件名都已统一为英文路径，降低 Windows 环境下的路径兼容风险

## 2026-03-24 绯铃状态联动补充

当前已经从“桌宠壳内手动预览静态状态”推进到“前端行为驱动桌宠状态变化”：

- 搜索壳页面在请求前后会主动切换绯铃状态
- 搜索窗口已挂 preload，可直接调用桌宠状态切换接口

当前联动规则：

1. `idle`
   - 默认待机
2. `happy_soft`
   - 打开搜索窗口
   - 健康检查成功
   - 打开文件/目录成功
3. `thinking`
   - 发起索引、内容搜索、文件名搜索、根目录查询
4. `smug`
   - 搜索命中结果
5. `confused`
   - 请求失败
   - 搜索空结果
   - 根目录为空

这一步的价值高于先做动画，因为它先建立了“角色状态和系统行为的骨架绑定”。

## 2026-03-24 绯铃待机眨眼任务单

当前准备进入动画阶段时，没有直接扩成完整精灵图系统，而是先单独拆出：

- `IDLE_BLINK_BRIEF.md`

原因：

- `blink` 是最轻的动画入口
- 最容易让桌宠“活起来”
- 又不会立刻把素材量和代码复杂度拉高

当前动画策略：

1. 先只做 `idle blink`
2. 先只需要两张补充图：
   - `blink_half`
   - `blink_closed`
3. 跑通后，再考虑把眨眼扩到其他状态

- 不只要有人设，还要有独立的视觉锁定文档
- 当前重点锁定：
  - 2 到 2.5 头身
  - 圆脸、大眼、团子感
  - 白毛狐耳红瞳
  - 红白蓝轻制服
  - 强 Q 版桌宠，而不是普通立绘
