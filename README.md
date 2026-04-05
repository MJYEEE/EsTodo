# EsTodo

待办事项 + 番茄钟应用

## 📦 快速下载

从 [Releases](https://github.com/你的用户名/EsTodo/releases) 页面下载最新版本：

- **Windows**: `EsTodo-windows.zip` - 解压后直接运行 `EsTodo.exe`
- **Linux**: `EsTodo-linux.tar.gz` - 解压后运行 `EsTodo`

## 功能特性

- ✅ 待办事项管理（增删改查）
- ✅ 子待办支持（无限层级）
- ✅ Markdown 内容
- ✅ 优先级标记
- ✅ 深色/浅色主题切换
- ✅ 番茄钟（工作/短休息/长休息）
- ✅ 番茄钟暂停/继续/停止
- ✅ 系统通知（plyer）
- ✅ 番茄钟与待办关联
- ✅ 番茄日历热力图（GitHub 风格）
- ✅ 点击日期查看当天番茄钟详情
- ✅ 标签系统（新建/编辑/删除标签，待办可关联标签）
- ✅ JSON 导入导出（备份/迁移数据）
- ✅ PyInstaller 打包（Windows/Linux 单文件 exe）
- ✅ GitHub Actions CI/CD（自动构建 Release）

## 安装

### 环境要求

- Python 3.12+
- conda

### 开发环境设置

```bash
# 激活虚拟环境
conda activate estodo

# 安装依赖
pip install -r requirements.txt
```

## 运行

```bash
# 激活环境
conda activate estodo

# 运行应用
python -m estodo.main
```

或者直接运行：

```bash
python src/estodo/main.py
```

## 开发计划

### v0.1
- 基础待办功能
- 子待办
- Markdown 内容

### v0.2
- 番茄钟基础计时（工作/短休息/长休息）
- 番茄钟暂停/继续/停止
- 系统通知（plyer）
- 番茄钟与待办关联
- 深色/浅色主题切换
- 优先级标记

### v0.3
- 番茄日历热力图（GitHub 风格）
- 点击日期查看当天番茄钟详情

### v0.4
- 标签系统（新建/编辑/删除标签，待办可关联标签）

### v0.5
- JSON 导入导出（备份/迁移数据）

### v0.6 (当前)
- PyInstaller 打包（Windows/Linux 单文件 exe）
- GitHub Actions CI/CD（自动构建 Release）

## 快捷键

- `Ctrl+N` - 新建待办
- `Ctrl+P` - 打开/关闭番茄钟
- `Ctrl+Q` - 退出

## 数据导入导出

### 导出数据

1. 菜单栏点击「文件 → 导出...」
2. 选择保存位置
3. 点击「保存」

导出的 JSON 文件包含：
- 所有标签
- 所有待办事项（含子待办）
- 所有番茄钟记录
- 待办与标签的关联关系

### 导入数据

1. 菜单栏点击「文件 → 导入...」
2. 选择要导入的 JSON 文件
3. 选择导入方式：
   - **「是」** - 替换：删除所有现有数据后导入
   - **「否」** - 合并：保留现有数据，追加导入（可能重复）
4. 点击「确定」

导入后会显示导入的统计信息。

## 打包与发布

### Windows 本地打包

```powershell
# 在 PowerShell 中运行
.\build-windows.ps1
```

### Linux 本地打包

```bash
# 在 Bash 中运行
./build-linux.sh
```

### GitHub Actions CI/CD

**打标签并发布：**

```bash
# 打版本标签
git tag -a v0.6.0 -m "Release v0.6.0"
git push origin v0.6.0
```

GitHub Actions 会自动：
1. 在 Windows 和 Linux 上构建
2. 生成 `EsTodo-windows.zip` 和 `EsTodo-linux.tar.gz`
3. 创建 GitHub Release 并上传构建产物

**手动触发构建：**

也可以在 GitHub 仓库的 Actions 页面手动触发工作流。

### 下载使用

从 [Releases](https://github.com/MJYEEE/EsTodo/releases) 页面下载：

- **Windows**: 下载 `EsTodo-windows.zip`，解压后直接运行 `EsTodo.exe`
- **Linux**: 下载 `EsTodo-linux.tar.gz`，解压后运行 `EsTodo`

## 项目结构

```
EsTodo/
├── .github/
│   └── workflows/
│       └── build.yml          # GitHub Actions 构建配置
├── src/
│   └── estodo/
│       ├── __init__.py
│       ├── main.py              # 入口
│       ├── database.py          # 数据库管理
│       ├── import_export.py     # 导入导出功能
│       ├── models/              # 数据模型
│       │   ├── __init__.py
│       │   ├── todo.py
│       │   ├── pomodoro.py
│       │   └── tag.py
│       └── views/               # UI 组件
│           ├── __init__.py
│           ├── main_window.py
│           ├── todo_tree.py
│           ├── todo_editor.py
│           ├── pomodoro_timer.py
│           ├── heatmap.py
│           ├── day_detail_dialog.py
│           ├── tag_dialog.py
│           ├── tag_selector.py
│           ├── notifications.py
│           ├── theme.py
│           └── markdown.py
├── estodo.spec                  # PyInstaller spec 文件
├── build-windows.ps1           # Windows 打包脚本
├── build-linux.sh              # Linux 打包脚本
├── requirements.txt
├── README.md
└── run.sh
```

## License

MIT
