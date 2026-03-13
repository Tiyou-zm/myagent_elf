# 新电脑续学指南

这份文档的目标是：在一台新电脑上，把这个仓库拉下来后，尽量无缝续接我们当前的学习与开发状态。

## 一、先理解这个仓库里最重要的 4 份文件

在新电脑上开始之前，先按顺序读完下面这些文件：

1. `README.md`
2. `PROJECT_CONTEXT.md`
3. `LEARNING_JOURNAL.md`
4. `TEACHING_FLOW.md`

它们分别负责：

- `README.md`：当前仓库状态、接口、约定、学习结论
- `PROJECT_CONTEXT.md`：项目边界、架构分层、Git 连接方案、当前阶段
- `LEARNING_JOURNAL.md`：我们每一步学了什么、做了什么、为什么这么做
- `TEACHING_FLOW.md`：后续准备怎么教、怎么继续拆知识点

如果这些文件都读完，哪怕换电脑、换线程，也能把当前上下文接回来。

## 二、新电脑需要准备什么

至少准备这些环境：

- Git
- Python 3.12+
- VSCode
- Codex / 当前对话环境

建议：

- Git 和 Python 都加入系统路径
- VSCode 能正常打开本地仓库

## 三、推荐的 GitHub 连接方式

这台项目仓库当前已经从 HTTPS push 切到了 `SSH over 443`。

原因：

- 之前这台机器的 HTTPS push 有偶发连接重置
- SSH over 443 更稳定，后续应优先使用

所以新电脑也建议直接配置成同样方式。

## 四、新电脑 Git 配置步骤

### 1. 生成新的 SSH key

在 PowerShell 里执行：

```powershell
ssh-keygen -t ed25519 -C "github-agent-study"
```

默认会生成：

- 私钥：`C:\Users\你的用户名\.ssh\id_ed25519`
- 公钥：`C:\Users\你的用户名\.ssh\id_ed25519.pub`

### 2. 配置 SSH over 443

创建文件：

- `C:\Users\你的用户名\.ssh\config`

写入：

```sshconfig
Host github.com
  HostName ssh.github.com
  Port 443
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
```

### 3. 把公钥加到 GitHub

查看公钥：

```powershell
Get-Content $HOME\.ssh\id_ed25519.pub
```

把输出的一整行复制到 GitHub：

- [GitHub SSH Keys](https://github.com/settings/keys)

### 4. 测试 SSH

```powershell
ssh -T git@github.com
```

看到类似下面的信息就说明通了：

```text
Hi <your-name>! You've successfully authenticated...
```

## 五、克隆仓库

使用 SSH 地址克隆：

```powershell
git clone git@github.com:Tiyou-zm/myagent_elf.git
```

进入目录：

```powershell
cd myagent_elf
```

确认远程地址：

```powershell
git remote -v
```

应看到：

```text
origin  git@github.com:Tiyou-zm/myagent_elf.git (fetch)
origin  git@github.com:Tiyou-zm/myagent_elf.git (push)
```

## 六、开始续接学习前要做什么

先不要急着写代码，先把上下文重新装进来。

### 1. 在 VSCode 打开仓库

### 2. 让 Codex 先读这 4 份文件

建议开场直接说这句话：

```text
先读 README、PROJECT_CONTEXT、LEARNING_JOURNAL、TEACHING_FLOW，然后继续上次的学习节奏。
```

如果你想更稳一点，可以直接说：

```text
先读 README、PROJECT_CONTEXT、LEARNING_JOURNAL、TEACHING_FLOW，总结当前项目状态、昨天学到哪里了、下一步最适合继续讲什么，再继续。
```

### 3. 如果还想让它对齐当前代码状态

再补一句：

```text
读完文档后，再看 src/index_service 当前实现，确认和文档一致后继续。
```

## 七、如何判断是不是“无缝续上了”

如果新电脑上的对话已经能说清楚下面这些内容，就说明基本续接成功：

- 这个项目的 `v1` 是什么
- 为什么现在先做本地文件检索助理
- 当前 Python 服务分成哪几层
- 内容检索和文件名检索为什么分开
- 当前增量索引为什么只做到文件级
- 当前 Git 为什么走 SSH over 443

## 八、后续协作约定

在新电脑上也继续沿用这些约定：

- 默认工作方式是边做边学
- 每推进一小步，都同步 `README.md`、`PROJECT_CONTEXT.md`、`LEARNING_JOURNAL.md`
- Git 提交信息默认写成十几到二十字左右的浓缩简介
- 继续优先用 SSH 推送 GitHub

## 九、一句最短恢复提示词

如果你赶时间，最短可以直接发：

```text
先读 README、PROJECT_CONTEXT、LEARNING_JOURNAL、TEACHING_FLOW，再从上次学习进度继续。
```

这句话就是以后换电脑、换线程时的默认恢复入口。
