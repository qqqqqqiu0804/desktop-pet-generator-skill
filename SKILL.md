# Desktop Pet Generator (桌面宠物生成器)

## 技能描述

根据用户提供的宠物照片，一键生成完整的 Windows 桌面宠物程序。生成的桌宠支持透明背景、自由行走、鼠标拖拽、双击互动、系统托盘等功能，并可直接打包为独立 EXE 文件运行。

## 适用场景

- 用户提供宠物/角色图片，要求制作桌面宠物
- 需要生成可运行的桌宠程序源码项目
- 需要打包成独立 EXE 可执行文件

## 输入要求

- **必需**：1 张或多张宠物/角色图片（推荐 3 张不同姿态：站立、坐姿、趴卧）
- **可选**：宠物名称、行走速度、窗口大小等自定义参数

## 输出产物

1. 完整的 Python 桌宠项目（PyQt5 实现）
2. 图片背景自动处理脚本（支持 AI 智能抠图）
3. PyInstaller 打包配置
4. 一键构建脚本（Windows batch）
5. 使用说明文档

## 核心功能

### 窗口特性
- 无边框透明窗口，始终置顶
- 支持鼠标拖拽移动到任意位置
- 双击宠物触发跳跃动画

### 动画系统
- 自动左右行走，屏幕边缘反弹
- 待机呼吸动画效果
- 跳跃抛物线动画
- 多种形象切换（站立/坐姿/趴卧）

### 系统托盘
- 右下角托盘图标
- 右键菜单：显示/隐藏、行走开关、切换形象、退出
- 双击托盘快速显示/隐藏

### 打包部署
- 单文件 EXE，无需 Python 环境
- 资源内嵌，分发方便

## 使用流程

### 1. 准备图片
将宠物图片放入项目 `assets/` 目录，命名为：
- `pet_stand.jpg/png` - 站立形象（必需）
- `pet_sit.jpg/png` - 坐姿形象（可选）
- `pet_lie.jpg/png` - 趴卧形象（可选）

### 2. 处理背景
```bash
# 基础抠图（纯色背景）
python process_images.py

# AI智能抠图（复杂背景推荐）
pip install rembg
python process_images.py --ai
```

### 3. 运行测试
```bash
pip install -r requirements.txt
python main.py
```

### 4. 打包 EXE
```bash
build.bat
```
生成的 `dist/DesktopPet.exe` 即为独立可执行文件。

## 技术栈

- **GUI 框架**：PyQt5
- **图像处理**：Pillow
- **AI 抠图**：rembg（可选）
- **打包工具**：PyInstaller

## 可调参数

在 `main.py` 中可调整：
- `pet_size`：宠物显示尺寸（默认 120x140）
- `walk_speed`：行走速度（默认 2 像素/帧）
- 跳跃高度、重力加速度等动画参数

## 项目结构

```
desktop-pet/
├── main.py              # 主程序
├── process_images.py    # 背景去除脚本
├── requirements.txt     # 依赖列表
├── desktop_pet.spec     # 打包配置
├── build.bat            # 一键打包脚本
├── README.md            # 使用说明
└── assets/              # 图片资源
    ├── pet_stand.jpg    # 原图
    ├── pet_sit.jpg
    ├── pet_lie.jpg
    ├── pet_stand.png    # 处理后透明图
    └── tray_icon.ico    # 托盘图标
```
