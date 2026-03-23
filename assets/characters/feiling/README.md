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

- `base/feiling_master_v1.jpg`
- `states/feiling_idle_v1.jpg`
- `states/feiling_happy_soft_v1.jpg`
- `states/feiling_thinking_v1.jpg`
- `states/feiling_confused_v1.jpg`
- `states/feiling_smug_v1.jpg`

## 使用约定

- `references/source_exports/` 用来保留原始导出图。
- `base/` 和 `states/` 只放标准命名后的接入版本。
- 后续所有状态图和动画，都以 `base/feiling_master_v1.jpg` 为唯一母版继续扩展。
- 当前这批素材是 JPG，棋盘格背景已经烘焙进图片里。
- 所以它们现在适合先做桌宠开发接入，但最终正式版仍建议换成透明背景 PNG。
- 当前绯铃素材目录中的文件和子目录都统一使用英文命名，避免后续代码、脚本和工具链在 Windows 环境里因为中文路径踩坑。

## 当前已接入的眨眼素材

- `animations/feiling_idle_blink_half_v1.jpg`
- `animations/feiling_idle_blink_closed_v1.png`
- `animations/feiling_idle_blink_half_overlay_v1.png`
- `animations/feiling_idle_blink_closed_overlay_v1.png`

说明：

- 当前先只给 `idle` 状态接眨眼
- 其他状态暂时不做眨眼扩展
- 其中真正运行时使用的是 `overlay` 版本
- 这样可以只覆盖眼睛区域，不会把手部、尾巴和身体姿势一起切坏
