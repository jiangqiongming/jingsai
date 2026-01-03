# 党史知识竞赛系统

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.3-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 项目简介

这是一个基于Flask的党史知识竞赛系统，支持用户答题、查看排行榜和成绩记录等功能。

## 功能特点

- 用户登录系统
- 答题功能（20道党史相关题目）
- 实时排行榜（按得分和用时排序）
- 个人成绩记录查看
- 每日答题次数限制（每人每天3次）
- 毫秒级时间精度，确保公平排序
- 响应式设计（支持移动端访问）

## 技术栈

- 后端：Flask 3.0.3
- 前端：HTML, CSS, JavaScript
- 数据存储：JSON文件

## 安装部署

### 本地部署

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/党史知识竞赛系统.git
   cd 党史知识竞赛系统
   ```

2. 安装Python 3.7+

3. 创建虚拟环境（推荐）：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

5. 运行应用：
   ```bash
   python app.py
   ```

6. 访问 `http://127.0.0.1:5000`

### 部署到云平台

本项目支持部署到以下平台：
- Heroku
- PythonAnywhere
- 任何支持Python的云服务器

## 使用说明

1. 使用预设用户名登录
2. 点击"开始答题"进入答题页面
3. 完成答题后查看结果和排行榜
4. 可以查看个人历史记录

## 项目结构

```
├── app.py               # 主应用文件
├── requirements.txt      # 依赖包列表
├── Procfile             # 部署配置文件
├── .gitignore           # Git忽略文件
├── user_records.json     # 用户答题记录存储
└── templates/            # 前端模板文件
    ├── login.html        # 登录页面
    ├── quiz.html         # 答题页面
    ├── rankings.html     # 排行榜页面
    ├── results.html      # 结果页面
    ├── user_records.html # 个人记录页面
    └── no_attempts.html  # 无答题次数提示页面
```

## 特色功能

- 精确到毫秒的答题时间记录
- 每日答题次数限制，防止刷分
- 按得分优先、用时次之的排序算法
- 详细的答题历史记录
- 响应式UI设计，支持移动端访问

## 自定义配置

### 修改预设人员名单

在`app.py`文件中的`PRESET_USERS`列表中修改预设人员名单。

### 修改题目

在`app.py`文件中的`QUESTIONS`列表中修改或添加题目。

## 数据存储

系统使用JSON文件存储数据：

1. `user_records.json` - 存储用户的所有答题记录和最佳成绩

## 安全说明

- 仅支持预设用户名登录
- 答题过程防刷新、防重复提交
- 数据文件本地存储，确保数据安全

## 维护说明

- 题目存储在app.py中，可按需修改
- 用户记录自动存储在user_records.json中
- 支持简单的数据备份和恢复

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件至：your.email@example.com