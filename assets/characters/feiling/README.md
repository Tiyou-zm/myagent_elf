# 绯铃素材目录

这个目录用于收口绯铃的母版、状态图和后续动画素材。

## 目录结构

- `base/`
  - 存放全身母版和中性基准图
- `states/`
  - 存放状态图
- `animations/`
  - 存放精灵图、序列帧和动画说明
- `references/`
  - 存放外部参考图、原始导出图和对照图

## 当前文件命名

- `base/feiling_master_v1.png`
- `states/feiling_idle_v1.png`
- `states/feiling_happy_soft_v1.png`
- `states/feiling_thinking_v1.png`
- `states/feiling_confused_v1.png`
- `states/feiling_smug_v1.png`

## 使用约定

- `references/source_exports/` 用来保留原始导出图。
- `base/` 和 `states/` 只放标准命名后的接入版本。
- 后续所有状态图和动画，都以 `base/feiling_master_v1.png` 为唯一母版继续扩展。
- 当前这批素材是 PNG，已确认带透明通道。
- 当前这批素材现在已经是可直接接入桌宠的透明背景 PNG。
- 当前绯铃素材目录中的文件和子目录都统一使用英文命名，避免后续代码、脚本和工具链在 Windows 环境里因为中文路径踩坑。

## 当前已接入的眨眼素材

- `animations/feiling_idle_blink_half_v1.png`
- `animations/feiling_idle_blink_closed_v1.png`
- `animations/feiling_idle_blink_half_overlay_v2.png`
- `animations/feiling_idle_blink_closed_overlay_v2.png`

说明：

- 当前先只给 `idle` 状态接眨眼
- 其他状态暂时不做眨眼扩展
- 其中真正运行时使用的是 `overlay` 版本
- 这样可以只覆盖眼睛区域，不会把手部、尾巴和身体姿势一起切坏


- eferences/legacy_raster_exports/ 保存旧 JPG 导出归档，不参与当前运行时引用。


## 2026-03-24 透明运行时版本

当前运行时正式切换到透明 PNG：
- `base/feiling_master_v1.png`
- `states/feiling_idle_v1.png`
- `states/feiling_happy_soft_v1.png`
- `states/feiling_thinking_v1.png`
- `states/feiling_confused_v1.png`
- `states/feiling_smug_v1.png`
- `animations/feiling_idle_blink_half_v1.png`
- `animations/feiling_idle_blink_closed_v1.png`
- `animations/feiling_idle_blink_half_overlay_v2.png`
- `animations/feiling_idle_blink_closed_overlay_v2.png`

旧 JPG 导出图已归档到：
- `references/legacy_raster_exports/`

当前 `source_exports/` 只保留透明 PNG 源文件。

## 2026-03-24 第二轮透明素材覆盖

桌面 `绯铃/feelingv1.0/` 目录中的新一批透明 PNG 已经覆盖进当前正式素材树。

当前可直接使用的版本包括：

- `base/feiling_master_v1.png`
- `states/feiling_idle_v1.png`
- `states/feiling_happy_soft_v1.png`
- `states/feiling_thinking_v1.png`
- `states/feiling_confused_v1.png`
- `states/feiling_smug_v1.png`
- `animations/feiling_idle_blink_half_v1.png`
- `animations/feiling_idle_blink_closed_v1.png`

当前原则：

- 先让桌宠继续使用这一版可用透明素材
- 后续如果母版继续微调，仍然沿用现有命名直接覆盖
