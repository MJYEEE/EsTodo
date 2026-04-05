# EsTodo

待办事项 + 番茄钟应用

## 功能特性

- ✅ 待办事项管理（增删改查）
- ✅ 子待办支持（无限层级）
- ✅ Markdown 内容
- ✅ 优先级标记
- ⏳ 番茄钟（开发中）
- ⏳ 番茄日历（开发中）
- ⏳ 导入导出（开发中）
- ⏳ 标签系统（开发中）

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

## 项目结构

```
EsTodo/
├── src/
│   └── estodo/
│       ├── __init__.py
│       ├── main.py              # 入口
│       ├── database.py          # 数据库管理
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
│           ├── theme.py
│           └── markdown.py
├── requirements.txt
└── README.md
```

## 开发计划

### v0.1 (当前)
- 基础待办功能
- 子待办
- Markdown 内容

### v0.2
- 番茄钟基础计时
- 系统通知

### v0.3
- 番茄钟与待办关联
- 番茄日历热力图

### v0.4
- 优先级
- 标签系统

### v0.5
- JSON 导入导出
- 深色/浅色主题切换

### v0.6
- PyInstaller 打包
- GitHub Actions CI/CD

## License

MIT
