# 应用图标

请在此目录下放置应用图标文件：

## 文件要求

- **文件名**: `icon.ico`
- **格式**: Windows ICO 格式
- **推荐尺寸**: 256x256 像素（包含 16x16, 32x32, 48x48, 64x64, 128x128, 256x256 等多个尺寸）

## 如何获取图标

### 方案一：在线生成

1. 找一张 PNG 图片（推荐正方形）
2. 使用在线工具转换为 ICO 格式：
   - https://convertio.co/zh/png-ico/
   - https://www.icoconverter.com/

### 方案二：使用 Python 生成

如果你有一张 PNG 图片，可以用 Python 转换：

```python
from PIL import Image

# 打开 PNG 图片
img = Image.open("icon.png")

# 保存为 ICO（包含多个尺寸）
img.save("icon.ico", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
```

### 方案三：使用免费图标网站

- https://www.flaticon.com/
- https://icon-icons.com/
- https://www.iconfinder.com/

搜索关键词：`todo`, `checklist`, `task`, `tomato`, `pomodoro`

## 临时方案

如果没有图标文件，打包脚本会自动跳过，使用默认图标。
