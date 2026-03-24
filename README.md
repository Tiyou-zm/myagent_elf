# agent_study

这是我们一起搭建个人桌面宠物 Agent 的学习仓库。

当前目标：

- 以“本地文件检索助理”为 `v1`
- 一边学习 Agent 设计，一边把能运行的项目做出来
- 每推进一步，都留下简洁但可回忆的共同笔记

当前分线说明：

- `agent_study` 继续承载：
  - 本地检索后端
  - 搜索窗口
  - Agent 能力实验
- 绯铃桌宠本体已拆到桌面独立项目：
  - `C:\Users\Administrator\Desktop\feiling`
  - 当前先专注做“标准陪伴型桌宠”
  - 等桌宠本体成熟后，再考虑把 agent 能力赋回绯铃
  - 当前可直接双击：
    - `C:\Users\Administrator\Desktop\feiling\run_feiling.bat`
    - `C:\Users\Administrator\Desktop\feiling\stop_feiling.bat`
  - 当前桌宠壳继续单独打磨，不再把气泡、拖拽和主界面遮挡问题带回 `agent_study`
  - 当前仍在继续压缩主窗边界，优先降低对桌面的遮挡
  - 当前已补待机精灵任务单：
    - `C:\Users\Administrator\Desktop\feiling\BLINK_SPRITESHEET_BRIEF.md`
    - `C:\Users\Administrator\Desktop\feiling\IDLE_BREATH_SPRITESHEET_BRIEF.md`
- 当前已补混合表现任务单：
  - `C:\Users\Administrator\Desktop\feiling\LIVE2D_SPRITE_HYBRID_BRIEF.md`
- 当前新增 `EasyVtuber` 实验工具路径：
  - `C:\Users\Administrator\Desktop\EasyVtuber_inspect`
  - 已补 `--output_frames` 导出序列帧能力
  - 已补 `--idle_export_input` 稳定待机输入模式
  - 已补一键脚本：`C:\Users\Administrator\Desktop\EasyVtuber_inspect\export_feiling_idle_frames.ps1`

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
- `POST /api/v1/chat`
- `POST /api/v1/open`

## 本地运行

先安装依赖：

```bash
python -m pip install -r requirements.txt
```

启动服务：

```bash
python -m uvicorn index_service.main:app --app-dir src --reload
```

如果要接本地私有 LLM 配置，可以在仓库根目录放一个不会进 Git 的 `.env.local`，例如：

```text
FEILING_LLM_BASE_URL=...
FEILING_LLM_API_KEY=...
FEILING_LLM_MODEL=...
```

`scripts/start_index_service.ps1` 启动时会自动加载这份本地配置。

## 当前接口说明

`POST /api/v1/index`

- 输入：用户授权的目录列表
- 输出：扫描文件数、实际重建数、未变化跳过数、跳过文件数、删除文件数

`POST /api/v1/search`

- 作用：按文件内容搜索

`POST /api/v1/search/files`

- 作用：按文件名或路径搜索

`POST /api/v1/chat`

- 作用：把“对话输入 -> 检索 -> 绯铃口吻回答 -> 可打开动作”收成一个统一接口
- 当前支持：
  - 本地搜索结果整合
  - 绯铃口吻回答
  - 返回“打开文件 / 打开目录”候选动作
  - 可选接入 OpenAI 兼容 LLM API

`GET /api/v1/roots`

- 作用：查看当前已经登记过的索引根目录

`POST /api/v1/open`

- 作用：触发本地打开文件或打开所在目录

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

如果想直接看一个最小前端怎么调用这些接口，还可以再启动前端壳：

```powershell
.\scripts\start_frontend_shell.ps1
```

然后打开：

```text
http://127.0.0.1:4173
```

这会依次验证：

- `/healthz`
- `/api/v1/index`
- `/api/v1/search`
- `/api/v1/search/files`
- `/api/v1/roots`

这一步的意义是把项目从“代码存在”进一步固定到“服务可启动、接口可重复验证”。

## 当前接口体验补充

为了让接口更像给前端直接使用的产品接口，当前又补了一层响应整理：

- `GET /healthz` 现在除了 `status`，还会返回 `message`
- `POST /api/v1/index` 现在会返回一条摘要式 `message`
- `POST /api/v1/search` 和 `POST /api/v1/search/files` 现在会返回：
  - `message`
  - `total_results`
- 输入不合法时，`400` 错误现在统一成结构化格式：
  - `code`
  - `message`

这一步的意义是让后面 Electron 接口调用时，不用先猜“这次结果该怎么解释”。

## 当前最小前端壳

为了在不正式开做 Electron 的前提下，先看清“前端怎么接后端”，仓库新增了一个很薄的网页壳：

- `playground/index.html`
- `scripts/start_frontend_shell.ps1`

它当前能直接调用：

- 健康检查
- 建立索引
- 内容搜索
- 文件名搜索
- 根目录查询
- 打开文件
- 打开所在目录

同时后端也补上了本地开发用 CORS，允许这个前端壳从 `http://127.0.0.1:4173` 访问 FastAPI。

## 当前最小 Electron 壳

现在又补上了一个真正的桌面宿主，用来承载现有前端壳：

- `package.json`
- `electron/main.js`
- `scripts/start_electron_shell.ps1`

启动方式：

```powershell
.\scripts\start_index_service.ps1
.\scripts\start_electron_shell.ps1
```

当前这层 Electron 先只做两件事：

- 打开桌面窗口
- 加载现有 `playground/index.html`

也就是说，当前已经从“网页壳验证调用链”推进到了“桌面窗口承载这条调用链”。

## 当前统一启动方式

为了避免每次手动分别开后端和 Electron，现在又补了统一编排脚本：

- `scripts/start_desktop_stack.ps1`
- `scripts/stop_desktop_stack.ps1`

启动整套最小桌面栈：

```powershell
.\scripts\start_desktop_stack.ps1
```

关闭整套最小桌面栈：

```powershell
.\scripts\stop_desktop_stack.ps1
```

当前这一步的意义是把“后端 + 桌面壳”从两套分散命令，推进到一个真正可重复使用的开发入口。

## 当前窗口角色拆分

为了不把产品继续推成传统单窗口应用，Electron 现在已经拆成两种窗口角色：

- `electron/pet.html`
  - 作为桌宠入口壳
  - 负责常驻、小窗、唤起搜索
- `playground/index.html`
  - 继续作为搜索与结果窗口
  - 负责索引、搜索、结果展示和动作触发

这意味着当前方向已经明确成：

- 桌宠壳是主入口
- 搜索窗口是功能面板

## 当前桌宠角色设定文档

为了避免桌宠继续停留在“功能壳”阶段，当前已经把基于参考立绘整理出的角色资料单独固化为四份文档：

- `OC_PROFILE.md`
  - 绯铃的完整角色设定卡
- `OC_ART_PROMPT.md`
  - 给 AI 画图平台直接使用的出图需求单
- `PET_ANIMATION_PLAN.md`
  - 后续做桌宠精灵图和状态动作时的清单
- `OC_VISUAL_LOCK.md`
  - 专门锁绯铃的头身比、脸型、Q版程度和负面约束
- `OC_ART_MASTER.md`
  - 给不能接收多文件的出图 agent 使用的单文件总需求
- `FULLBODY_MASTER_BRIEF.md`
  - 专门用于固定绯铃全身母版的任务单
- `STATE_SET_BRIEF.md`
  - 绯铃第一批状态图任务单
- `FIRST_ANIMATION_BRIEF.md`
  - 绯铃第一批动画任务单

## 当前绯铃素材目录

为了把已经确认的母版和状态图真正收口到仓库里，当前新增了：

- `assets/characters/feiling/`
  - `README.md`
  - `ASSET_MANIFEST.md`
  - `base/`
  - `states/`
  - `animations/`
  - `references/`

当前这一步的意义不是继续扩需求，而是先把“已经差不多定下来的绯铃素材”有组织地沉淀成固定目录。

当前判断：

- `base/feiling_master_v1.png`
  - 可以作为第一版全身母版
- 第一批状态图已经基本够用：
  - `idle`
  - `happy_shy`
  - `happy_soft`
  - `thinking`
  - `smug`

需要注意：

- 当前“思考”和“困惑”还没有完全拉开
- 如果后续接入后感觉辨识度不够，再单独补一张更明确的 `confused`

## 当前绯铃静态接入

当前 Electron 桌宠壳已经开始直接接绯铃静态素材：

- `electron/pet.html`
  - 不再使用抽象占位脸，而是直接显示绯铃状态图
- `electron/main.js`
  - 增加桌宠状态管理
  - 当前支持：
    - `idle`
    - `happy_soft`
    - `thinking`
    - `confused`
    - `smug`
- `electron/preload.js`
  - 暴露 `setPetState()`，方便桌宠壳和后续功能触发表情切换

当前桌宠壳已经可以：

- 默认显示 `idle`
- 搜索窗口打开时切到 `happy_soft`
- 搜索窗口收起时回到 `idle`
- 在桌宠壳内手动预览 5 个静态状态

当前素材注意事项：

- 现在接入的是透明 PNG 素材
- 背景已切为真实透明通道
- 适合先做开发接入
- 当前已切到透明 PNG
- 绯铃素材目录现已统一改成英文路径，避免后续脚本、Electron 和外部工具被中文路径绊住

## 当前绯铃状态联动

桌宠当前不再只是“手动切图预览”，而是开始和真实行为绑定：

- `playground/index.html`
  - 搜索壳现在会在请求生命周期里同步绯铃状态
- `electron/main.js`
  - 搜索窗口也挂上了 preload，可接收桌宠状态切换

当前最小联动规则：

1. 默认 `idle`
2. 打开搜索窗口时 `happy_soft`
3. 发起索引、搜索、根目录查询时 `thinking`
4. 有命中结果时 `smug`
5. 空结果或请求失败时 `confused`
6. 打开文件或目录成功时 `happy_soft`

这一步的意义：

- 绯铃第一次不只是“显示在桌面上”
- 而是开始在真实工作流里表达反应

## 当前绯铃待机眨眼

绯铃现在已经开始接第一层动画，但范围控制得很小：

- 只给 `idle` 状态接眨眼
- 暂时不扩展到其他状态

当前新增素材：

- `assets/characters/feiling/animations/feiling_idle_blink_half_v1.png`
- `assets/characters/feiling/animations/feiling_idle_blink_closed_v1.png`
- `assets/characters/feiling/animations/feiling_idle_blink_half_overlay_v2.png`
- `assets/characters/feiling/animations/feiling_idle_blink_closed_overlay_v2.png`

当前实现方式：

- `electron/pet.html`
  - 在 `idle` 状态下定时叠加眼睛覆盖层：
    - 睁眼
    - 半闭眼
    - 闭眼
    - 睁眼

这样做是因为当前整张眨眼图和待机母图的手部动作不一致，直接整张切帧会穿帮。

这一步的意义：

- 先让绯铃“安静活着”
- 不把动画系统一开始做重

## 当前眨眼出图任务

为了避免一上来把动画范围做大，当前又单独补了一份：

- `IDLE_BLINK_BRIEF.md`

这份文档只负责一件事：

- 基于 `feiling_idle_v1.png` 产出第一组待机眨眼图

也就是先做：

- `blink_half`
- `blink_closed`

不扩展到其他状态，不重新设计角色，不把问题一次做重。

当前绯铃的核心方向已经定成：

- 白尾灵狐拟人桌宠
- 很爱主人
- 平时安静细心
- 偶尔会腹黑毒舌一下
- 但本质始终是偏袒主人的陪伴型小助理

当前出图阶段新增的关键结论：

- 角色设定文档不等于视觉锁定文档
- 想让角色稳定接近参考图，必须额外锁住：
  - 头身比
  - 圆脸与大眼比例
  - 团子感
  - 强 Q 版桌宠感

## 当前桌宠形态补充

为了把“桌宠主、搜索辅”的权重真正落到代码里，当前 Electron 又往前推进了一步：

- `electron/main.js`
  - 现在默认只先启动桌宠壳
  - 搜索窗口改成被桌宠唤起时再懒加载
- `electron/pet.html`
  - 现在已经是一个可常驻桌面的最小桌宠壳
  - 保留打开搜索、隐藏搜索、退出桌宠三个动作
  - 会根据搜索窗口是否可见同步显示状态
- `electron/preload.js`
  - 负责把桌宠窗口需要的最小控制能力安全暴露给前端壳

## 当前统一停机补充

统一停机脚本这次也补稳了一轮：

- `scripts/stop_desktop_stack.ps1`
  - 现在会显式等待 Electron 和 Python 进程退出
  - 会再次检查 8000 端口是否仍在监听
  - 只有确认端口释放后才删除运行状态文件

这一步的意义是避免出现“脚本提示停了，但后端端口还挂着”的假停机状态。



## 2026-03-24 透明素材与最小桌宠壳

当前绯铃运行时素材已经正式切到透明 PNG：
- `assets/characters/feiling/base/feiling_master_v1.png`
- `assets/characters/feiling/states/*.png`
- `assets/characters/feiling/animations/*.png`

旧的 JPG 导出图没有删除，而是归档到：
- `assets/characters/feiling/references/legacy_raster_exports/`

当前桌宠壳也已经从“带大卡片面板的开发壳”收口成：
- 默认只显示绯铃本体
- 右侧一个小菜单按钮
- 菜单里承载：
  - 唤起/收起搜索
  - 退出桌宠
  - 开发状态预览

这一步的意义是把产品形态进一步拉回“桌宠主、搜索辅”。

## 2026-03-24 极简可交互桌宠壳

这一轮进一步确认了桌宠层的优先级：

- 保留后端搜索与搜索窗口
- 把当前状态面板型 `pet.html` 收为旧实验
- 重新做一个真正的极简桌宠壳

旧实验已经备份到：

- `electron/pet_state_shell_experiment.html`

当前运行中的桌宠壳只保留：

- 绯铃母版
- 自定义拖拽
- hover 反馈
- click 反馈
- 右侧菜单
- 菜单里的“打开搜索”

这一步的意义：

- 不再让桌宠层继续被状态切图和实验面板牵着走
- 先把“一个能摸、能拖、能叫出搜索的绯铃”做对
- 后续动画与表情系统都建立在这个更稳定的交互骨架上

## 2026-03-24 极简桌宠壳修正

这一轮又针对真实手感补了一次修正：

- 绯铃本体进一步放大
- 拖拽命中区扩到几乎整个全身
- 隐藏状态下的菜单改成真正不可见，避免顶部残留白条/面板感
- 桌宠窗口显式设置透明背景，减少系统层面的透明显示歧义

这一步之后，当前桌宠壳的方向更明确了：

- 先优先保证“像一个能抓起来移动的小桌宠”
- 再继续修菜单细节和后续交互

## 2026-03-24 透明边界裁切

这一轮又根据真实使用时的遮挡感补了一次素材级修正：

- 绯铃运行时 PNG 统一按同一裁切框裁掉外层透明空白
- 保持母版、状态图和眨眼 overlay 仍然能对位
- 同时把桌宠窗口尺寸跟着收紧
- 右侧菜单按钮再往本体方向收了一点

这一步的意义：

- 减少桌宠对桌面的无意义遮挡
- 让拖拽命中区更接近绯铃实际体积
- 避免后面继续靠放大缩小去掩盖素材透明边界过大的问题

## 2026-03-24 WPF 桌宠壳迁移

这一步开始正式把“桌宠本体”从 Electron 迁到 WPF。

原因很明确：

- Electron 更适合作为当前搜索窗口宿主
- 但对“透明、无边框、常驻、可拖拽桌宠”这件事，在当前机器上的稳定性不够理想
- 所以桌宠壳和搜索窗开始分栈：
  - WPF：负责桌宠本体
  - Electron：继续承载现有搜索窗口

当前已经落下的最小 WPF 桌宠壳：

- `desktop/FeilingPetShell`

它当前已经具备：

- 绯铃母版显示
- 透明无边框窗口
- 拖拽
- hover 反馈
- click 反馈
- 右侧菜单
- 菜单里的“打开搜索”

配套脚本：

- `scripts/start_wpf_pet.ps1`
- `scripts/stop_wpf_pet.ps1`
- `scripts/start_search_window.ps1`

当前运行方式：

```powershell
.\scripts\start_wpf_pet.ps1
```

前提：

- 当前机器需要安装 `.NET 8 SDK`

如果要单独拉起现有搜索窗口：

```powershell
.\scripts\start_search_window.ps1
```

这一步的意义：

- 后端和搜索窗口不需要推倒重来
- 桌宠本体终于开始用更适合它的技术栈承载

## 当前 WPF 桌宠交互修正

针对 WPF 桌宠壳里“本体拖不动、菜单点不出来”的问题，当前又补了一轮命中区重构：

- 绯铃本体改成单独的拖拽命中层
- 菜单按钮不再和根层拖拽事件抢鼠标
- hover / click 反馈改为只围绕绯铃本体触发
- 右侧菜单按钮再往本体收了一点

当前目标很明确：

- 先把 WPF 桌宠做成真正可拖、可点、可展开菜单的稳定壳
- 不再优先把精力花在眨眼和多状态切图上
- 当前菜单已补上“退出桌宠”，方便频繁测试时快速收尾

## 当前绯铃设定与素材补充

这一轮又往前补了两件事：

- 用桌面 `绯铃/feelingv1.0/` 里的新一批透明 PNG 覆盖正式素材目录
- 重写 `OC_PROFILE.md`，把绯铃的人格、关系、说话方式和成长方向补成可持续使用的主设定卡

当前可以把绯铃视为：

- 角色设定已基本稳定
- 素材目录已可持续接入
- 后续继续做桌宠时，不需要再回到“角色到底是谁”这个阶段

最新的人设口径也已经收紧：

- 不再强调“腹黑”
- 改成“轻微傲娇、偶尔嘴硬”
- 核心感觉是偏爱主人、会轻轻拿捏一下，但不会攻击性地吐槽
- 语气上比最初设定更阳光一点、更有朝气一点，方便后续做动作和交互反馈

同时已经新增：

- `FEILING_DIALOGUE_GUIDE.md`

后续只要是绯铃会说出来的字，都应优先参考这份台词与语气手册。

## 2026-03-24 气泡式搜索与对话接口

当前搜索窗口不再只做“表单 + 结果列表”，而是开始向真正的对话入口收口：

- `playground/index.html`
  - 已改成气泡式对话界面
- `POST /api/v1/chat`
  - 统一处理：
    - 用户输入
    - 内容搜索 / 文件搜索
    - 绯铃口吻回答
    - 打开文件 / 打开目录候选动作

当前 LLM 接入方式也已经预留成可插拔：

- `FEILING_LLM_BASE_URL`
- `FEILING_LLM_API_KEY`
- `FEILING_LLM_MODEL`

如果这些环境变量存在，后端会按 OpenAI 兼容接口尝试调用；没有配置时，就先走本地检索模板回答。
