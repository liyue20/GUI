# AIGUI Model Service

AIGUI Model Service 是一个基于 FastAPI 的 AI GUI 布局和样式生成服务，能够将 Markdown 文本智能转换为具有优化布局和样式的 HTML 页面。

## 功能特性

- 🎨 智能布局生成：基于 AI 模型的自适应布局方案
- 📝 Markdown 转换：支持标准 Markdown 语法解析
- 🎯 样式优化：自动生成符合设计规范的样式
- 🎨 主题定制：支持自定义主题色
- ⚡ 高性能：支持并发请求处理
- 🔄 实时预览：提供即时的 HTML 预览功能

## 快速开始

### 环境要求

- Python 3.8+
- CUDA (可选，用于 GPU 加速)
- 足够的磁盘空间用于模型存储

### 安装步骤

1. 克隆项目
```bash
git clone https://gitlab.dingdao.com/dingdao/aigui/runtime/aigui-model-service.git
cd aigui-model-service
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 检查模型文件
确保以下模型文件存在：
- `/data/models/layout/layoutModel_05.pth`
- `/data/models/style/styleModel.pth`

### 启动服务

有以下三种启动方式：

1. **使用 Makefile（推荐）**
```bash
make start-server  # 启动服务
make run          # 运行服务
make html         # 生成 HTML
```

2. **直接启动**
```bash
python main.py
```

3. **本地调试模式**
```bash
python src/api/endpoints/layout_api_local.py
```

### 验证服务

1. 健康检查
```bash
curl http://localhost:8000/health/check
```

2. 访问 API 文档
```
http://localhost:8000/docs
```

## API 使用说明

### 布局生成 API

**接口**：`POST /api/layout/generate`

**请求参数**：
```json
{
    "markdown_text": "您的 Markdown 文本",
    "card_width": 800,
    "card_height": 600,
    "theme_color": "#FF5733"
}
```

**响应**：
```json
{
    "layout_json": "生成的 HTML 内容"
}
```

## 项目结构

```
aigui-model-service/
├── main.py                 # 主入口文件
├── src/
│   ├── api/               # API 层
│   │   ├── endpoints/     # API 端点
│   │   └── schemas/       # 数据模型
│   ├── services/          # 服务层
│   │   ├── layout_agent/  # 布局生成服务
│   │   └── style_agent/   # 样式生成服务
│   └── utils/             # 工具类
└── data/                  # 模型数据
    └── models/
        ├── layout/
        └── style/
```

## 开发指南

### 本地开发

1. 启用开发模式
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. 代码风格
- 遵循 PEP 8 规范
- 使用 pylint 进行代码检查

### 调试技巧

1. 查看日志
```bash
tail -f logs/app.log
```

2. 性能分析
```bash
python -m cProfile -o output.prof main.py
```

## 常见问题

1. **模型加载失败**
- 检查模型文件路径是否正确
- 确认 CUDA 环境配置（如果使用 GPU）

2. **内存使用过高**
- 调整并发请求数限制
- 检查大文件处理逻辑

## 维护者

- in_liyue@dingdao.com

## 更新日志

### v1.0.1 (2024/12/24)
- 初始版本发布
- 支持基础布局生成
- 添加样式优化功能

## License

Copyright © 2024 DingDao

{

    "markdown_text": "# 请假事由\\n尊敬的领导，最近状态不好，想调整心情打算安排短途旅游，预计请假 1 天。我会提前完成手头上的工作！\\n\\n**2024/11/01 9:00 开始**  \\n**2024/11/03 18:00 截止**\\n\\n---\\n\\n# 当月日历\\n**2024年10月25日**\\n\\n| 日 | 一 | 二 | 三 | 四 | 五 | 六 |\\n|----|----|----|----|----|----|----|\\n| 1  | 2  | 3  | 4  | 5  | ... |    |\\n\\n---\\n\\n# 旅游推荐\\n\\n根据您的假期时长，查询了近期适合出游的地点，建议前往以下地区及景点：\\n\\n### **01. 杭州 - 浙江省** 1200.8KM  \\n西湖、九溪烟树、灵隐寺  \\n\\n### **02. 南京 - 江苏省** 1200.8KM  \\n中山陵、玄武湖、绣球山  \\n\\n### **03. 西安 - 陕西省** 1200.8KM  \\n古城墙、大雁塔、终南山  \\n\\n---\\n\\n# 目的地天气\\n![旅游图片](https://img95.699pic.com/photo/60016/8156.jpg_wh300.jpg)\\n\\n**上海天气--20°C--Shanghai**\\n\\n查询了目的地上海近期适合出游的天气，建议在 **12月25日-27日** 安排出行。\\n\\n---\\n\\n**请假事由**\\n\\n因个人计划，拟于近期前往上海进行短期旅游，特此申请请假三天。\\n\\n**2024/12/25 9:00 开始**  \\n**2024/12/27 18:00 截止**",
    "card_width": "1080",
    "card_height": "1060",
    "theme_color": ""
}
