# Simple MagenticOrchestration Story Sample

这是一个简单易上手的 MagenticOrchestration 示例，演示如何使用两个 AI Agent 协作完成故事生成和分析任务。

## 功能概述

本示例包含两个专门的 AI Agent：

1. **StoryGenerator（故事生成器）**
   - 专门负责创作引人入胜的故事
   - 支持多种文学体裁（悬疑、冒险、科幻、奇幻等）
   - 能够创建完整的故事结构和生动的角色

2. **StorySummarizer（故事总结器）**
   - 专门负责分析和总结故事
   - 提供详细的文学分析和评价
   - 识别主题、角色发展和叙事技巧

## 文件结构

```
simple_magentic_story_sample/
├── app.py                    # 主应用程序
├── story_generator.yaml      # 故事生成器 Agent 配置
├── story_summarizer.yaml     # 故事总结器 Agent 配置
├── requirements.txt          # Python 依赖包
├── .env.example             # 环境变量示例
└── README.md               # 本文件
```

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入以下信息：

```env
# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ORG_ID=your_openai_org_id_here

# 或者使用 Azure OpenAI
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# 模型配置
OpenAI:ChatModelId=gpt-4o
```

### 3. 运行示例

```bash
python app.py
```

## 工作流程

1. **初始化阶段**：加载两个 Agent 的配置
2. **故事生成阶段**：StoryGenerator 创作一个关于图书馆神秘发现的短篇故事
3. **故事分析阶段**：StorySummarizer 对生成的故事进行全面分析
4. **结果输出**：将完整的工作流程结果保存到 `outputs/` 目录

## 输出示例

程序运行后会生成：
- 控制台实时输出显示 Agent 的工作过程
- `outputs/YYYYMMDD_HHMM/story_analysis_report.md` 文件包含完整结果

## 自定义使用

### 修改故事主题

在 `app.py` 中的 `story_task` 变量中修改故事要求：

```python
story_task = """
创建一个关于 [你的主题] 的故事，然后进行全面分析。

工作流程：
1. 故事生成器：创作一个 [具体要求] 的故事
2. 故事总结器：分析故事的 [分析重点]
"""
```

### 调整 Agent 配置

- 编辑 `story_generator.yaml` 来修改故事生成器的行为
- 编辑 `story_summarizer.yaml` 来调整分析器的重点

### 温度参数说明

- **StoryGenerator**: `temperature: 0.8` - 较高的创造性，适合故事创作
- **StorySummarizer**: `temperature: 0.3` - 较低的随机性，确保分析的一致性

## 技术特点

- **异步处理**：使用 `asyncio` 实现高效的异步操作
- **流式输出**：实时显示 Agent 的工作进度
- **错误处理**：包含完整的异常处理和资源清理
- **结果保存**：自动保存带时间戳的分析报告

## 扩展建议

1. **添加更多 Agent**：可以添加编辑器、翻译器等其他 Agent
2. **支持文件输入**：允许用户上传现有故事进行分析
3. **多语言支持**：配置不同语言的故事生成和分析
4. **交互式界面**：添加 Web 界面或命令行交互

## 故障排除

### 常见问题

1. **API 密钥错误**：确保 `.env` 文件中的 API 密钥正确
2. **模型不可用**：检查模型名称是否正确，确保有访问权限
3. **网络连接问题**：确保网络连接正常，可以访问 OpenAI/Azure 服务

### 调试模式

设置环境变量启用详细日志：

```bash
export LOG_LEVEL=DEBUG
python app.py
```

## 许可证

本示例遵循 MIT 许可证。