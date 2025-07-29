<div align="center">
  <img src="yimu-frontend/public/logo.png" alt="一木记账 Logo" width="200">
</div>

# 一木记账年度总结分析工具

> ⚠️ **注意：这是一个早期开发项目**  
> 该项目目前处于开发阶段，功能还在持续完善中。欢迎试用并提供反馈！

用于分析 **「一木记账」** 数据，并生成可爱手帐风的年度总结报告

## 🚧 开发状态

目前已完成开屏页面和财务总览页面，其他分析维度正在持续开发中。

**欢迎您：**
- 🎯 提出更多年度总结分析维度的想法
- 💡 分享您希望看到的财务洞察内容  
- 🎨 建议手帐风格的设计改进
- 🐛 报告使用过程中遇到的问题

您的每一个建议都有助于项目的完善！

## 🚀 功能特性

### 📄 手帐风格页面展示

- [x] **开屏页面** - 手帐剪贴风格的欢迎界面，展示精美的年度记账封面  
  ![开屏页面](yimu-frontend/public/开屏页面.png)

- [x] **财务总览页面** - 年度财务数据概览，包括收支统计、储蓄率和核心财务指标  
  ![财务总览](yimu-frontend/public/财务总览.png)

- [ ] **更多维度页面** - 这不是全部的维度，我们正在规划更多有趣的分析维度，敬请期待！

## 📥 数据导入说明

在开始使用前，请确保：

1. **导出一木记账数据**：在一木记账App中选择导出功能
2. **文件格式选择**：请选择 **ZIP 格式** 进行导出
3. **解压放置**：将下载的ZIP文件解压后，将整个文件夹放到本项目的根目录下

```
YimuAnnualSummary/
├── yimu-backend/
├── yimu-frontend/
└── 账单_XXXXXXXXXXXX/  ← 解压后的数据文件夹放在这里
    ├── IMG_20241223_132934.jpg
    ├── IMG_20241226_222246.jpg
    └── 账单_XXXXXXXXXXXX.xls
```

## 🚀 快速开始

### 1. 后端设置

```bash
# 进入后端目录
cd yimu-backend

# 安装 Python 依赖（使用 uv）
uv sync

# 启动后端服务
uv run main.py
```

后端服务将在 `http://localhost:8000` 启动，API 文档可在 `http://localhost:8000/docs` 查看。

### 2. 前端设置

```bash
# 进入前端目录
cd yimu-frontend

# 安装依赖
npm install

# 开发模式启动
npm run tauri dev
```

### 3. 构建生产版本

```bash
# 构建桌面应用
cd yimu-frontend
npm run tauri build
```

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 🙏 致谢

- [星夜浪漫宇宙温柔字体](https://font.chinaz.com/22112237387.htm)
- [EffectEmoji](https://t.me/addemoji/EffectEmoji) - Telegram 动态表情包
- [PencilEmoji](https://t.me/addemoji/PencilEmoji) - Telegram 手绘表情包  
- [CuteEmoji](https://t.me/addemoji/CuteEmoji) - Telegram 可爱表情包

---

✨ **享受你的手帐风格财务总结之旅！** ✨

如有问题或建议，请提交 Issue 或联系开发者。