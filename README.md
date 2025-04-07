### **README.md**

# 动漫文件组织工具

![GitHub Logo](https://github.com/favicon.ico)
![GitHub License](https://img.shields.io/github/license/your-username/your-repo)
![GitHub Stars](https://img.shields.io/github/stars/your-username/your-repo)
![GitHub Forks](https://img.shields.io/github/forks/your-username/your-repo)

一个基于 Python 和 TMDB API 的动漫文件组织工具，用于自动整理和重命名动漫文件。

## 功能特点

- **自动整理文件**：根据 TMDB 数据自动创建季文件夹并重命名文件。
- **支持多种文件类型**：支持视频文件（如 `.mp4`、`.mkv`）和字幕文件（如 `.srt`、`.txt`）。
- **批量或逐个确认**：提供批量确认或逐个确认重命名操作的选项。
- **用户友好的界面**：基于 PyQt6 的图形用户界面，操作简单直观。
- **错误处理**：记录详细的错误信息，确保文件处理过程中的安全性。

## 安装步骤

### **1. 克隆仓库**

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### **2. 安装依赖**

确保已安装 Python 3.6 或更高版本。

```bash
pip install -r requirements.txt
```

### **3. 获取 TMDB API 密钥**

1. 访问 [TMDB 开发者页面](https://www.themoviedb.org/settings/api) 注册并获取 API 密钥。
2. 创建一个名为 `api_key.txt` 的文件，并将 API 密钥保存到该文件中。

### **4. 运行程序**

```bash
python TMDB-Episode-Information-Fetcher_V1.1.0.20241221_Releases.py
```

## 使用方法

1. **选择文件夹**：点击“浏览”按钮，选择包含动漫文件的文件夹。
2. **选择动漫**：根据文件夹名从 TMDB 搜索结果中选择正确的动漫。
3. **确认重命名**：在批量确认对话框中，选择“批量确认”或“逐个确认”来完成文件重命名操作。
4. **查看状态**：在状态文本框中查看文件处理的详细信息。

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. ** Fork ** 本项目到你的 GitHub 账号。
2. 创建一个新的分支：`git checkout -b feature/your-feature`
3. 提交你的更改：`git commit -m "Add some feature"`
4. 推送到分支：`git push origin feature/your-feature`
5. 提交 Pull Request。

## 许可证

本项目采用 [MIT License](LICENSE) 许可证。
