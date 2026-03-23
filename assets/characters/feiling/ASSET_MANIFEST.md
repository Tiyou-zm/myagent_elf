# 绯铃素材清单

## 当前阶段结论

绯铃已经进入“可以开始接入桌宠”的阶段。

当前这组图已经足够承担 `v1` 素材起步：

- 1 张全身母版
- 5 张可用状态图

它们已经可以支撑：

- 桌宠静态展示
- 状态切换
- 后续 `idle_breath` 和 `blink` 的动画制作

## 文件落盘

### 母版

- `base/feiling_master_v1.png`
  - 当前确认的全身中性母版
  - 用于后续所有状态图和动画扩展

### 状态图

- `states/feiling_idle_v1.png`
  - 中性待机
  - 可直接复用母版，或复制母版作为待机图

- `states/feiling_happy_soft_v1.png`
  - 轻微微笑、站姿稳定
  - 适合做通用开心态、欢迎态、搜索完成态

- `states/feiling_thinking_v1.png`
  - 托腮思考
  - 适合做搜索中、判断中、检索中状态

- `states/feiling_confused_v1.png`
  - 困惑
  - 适合做没理解指令、等待澄清、搜索结果不明显时的反馈

- `states/feiling_smug_v1.png`
  - 小腹黑得意
  - 适合做“我就知道”“我已经帮你找到了”的轻得意反馈

### 原始导出图

- `references/source_exports/feiling_master_source_v1.png`
- `references/source_exports/feiling_state_idle_source_v1.png`
- `references/source_exports/feiling_state_happy_source_v1.png`
- `references/source_exports/feiling_state_thinking_source_v1.png`
- `references/source_exports/feiling_state_confused_source_v1.png`
- `references/source_exports/feiling_state_smug_source_v1.png`
- `references/source_exports/feiling_idle_blink_half_source_v1.png`
- `references/source_exports/feiling_idle_blink_closed_source_v1.png`

说明：

- 这些文件用于保留你最初导出的原始版本
- 标准接入仍然优先使用 `base/` 和 `states/` 里的规范命名文件
- 当前绯铃素材目录已统一改成英文路径

### 动画接入图

- `animations/feiling_idle_blink_half_v1.png`
- `animations/feiling_idle_blink_closed_v1.png`
- `animations/feiling_idle_blink_half_overlay_v2.png`
- `animations/feiling_idle_blink_closed_overlay_v2.png`

说明：

- 当前只做 `idle blink`
- 不扩展到 `happy_soft`、`thinking`、`confused`、`smug`
- 运行时优先使用 `overlay` 版本，避免整张切图导致手部动作不一致

## 当前观察

### 已经足够好的地方

- 母版全身比例已经稳定
- 脸、发型、服装方向都统一了
- 绯铃的核心识别点已经明确：
  - 白毛
  - 狐耳
  - 红瞳
  - 红白蓝轻制服
  - 软糯但不低幼

### 还可以后续补强的地方

- 当前这些文件是 PNG，已确认带透明通道
- 这些文件现在已经是桌宠运行时使用的透明 PNG
- “思考”和“困惑”虽然已经都有了，但后面仍可继续拉开动作和神情差异
- `smug` 这张已经可用，但后面接入桌宠时要控制频率，避免角色显得太轻佻

## 接入优先级建议

先接这 4 类：

1. `idle`
2. `happy_soft`
3. `thinking`
4. `smug`

然后再补：

5. `confused`
6. `idle_breath`
7. `blink`


- eferences/legacy_raster_exports/ 保存旧 JPG 导出归档，不参与当前运行时引用。

