# 🗣️ 语音交互式 AICRM 系统

基于 LangGraph + 通义千问大模型构建的智能客户管理助手，支持 **文本输入** 与 **语音文件上传** 两种交互方式，集成医学知识库检索、实时联网搜索、数据库查询等能力。

## ✨ 主要特性

- 🎤 **语音识别**：上传 `.wav` 音频文件，自动转写成文字（基于 Qwen3-ASR-Flash）
- 🔊 **语音合成**：AI 回答可生成 MP3 语音（基于 Edge-TTS），保存至本地
- 🧠 **智能工具调用**：
  - `rag_medical`：检索本地医学知识库（疾病、药物、治疗方案）
  - `tavily_search`：获取最新医疗资讯、药品动态（底层使用百度搜索 API）
  - `sql_agent`：查询 MySQL/SQLite 中的用户、就诊记录等结构化数据
- 💾 **对话记忆**：基于 SQLite 的 checkpoint，支持多线程（thread_id）与多用户（user_id）
- 🖥️ **交互式终端**：每轮对话可选文本输入或上传 WAV 文件，回答后可选择是否生成语音

## 🛠️ 技术栈

| 组件           | 技术                                                                 |
| -------------- | -------------------------------------------------------------------- |
| 大模型         | 通义千问 (qwen-turbo / qwen-plus)，通过 LangChain ChatOpenAI 调用    |
| 语音识别 (ASR) | Qwen3-ASR-Flash (阿里云百炼)                                         |
| 语音合成 (TTS) | Edge-TTS (微软 Azure 边缘语音，免费)                                 |
| 向量数据库     | Chroma (存储医学知识条文)                                            |
| 搜索引擎       | 百度搜索 API (千帆平台)                                              |
| SQL Agent      | LangChain SQLDatabaseToolkit + MySQL / SQLite                        |
| 记忆存储       | SQLite (LangGraph SqliteSaver)                                       |
| 其他           | LangChain, LangGraph, python-dotenv, pydub (音频格式转换)            |

## 📦 环境准备

### 1. 克隆项目
```bash
git clone https://github.com/elenacharlotte1345-lab/AI_CRM.git
cd AI_project
```

### 2. 创建虚拟环境（推荐）
```bash
python -m venv py312_env
# 激活环境 (Windows)
py312_env\Scripts\activate
# 激活环境 (Linux/Mac)
source py312_env/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```
若没有 `requirements.txt`，请手动安装：
```bash
pip install langchain langgraph langchain-openai langchain-community chromadb dashscope edge-tts pydub python-dotenv pymysql
```

> **注意**：音频格式转换需要 `ffmpeg`，请根据操作系统自行安装并加入 PATH。

### 4. 配置环境变量

创建 `.env` 文件（在`utils`文件夹下），填入以下内容：

```ini
# 通义千问 API Key（阿里云百炼）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# 百度搜索 API Key（千帆平台）
BAIDU_API_KEY=your_baidu_api_key

# 可选：通义千问具体模型配置
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-turbo
QWEN_EMBEDDING_MODEL=text-embedding-v1
```

> 获取方式：
> - 通义千问 API Key：[阿里云百炼控制台](https://bailian.console.aliyun.com/)
> - 百度搜索 API Key：[百度千帆平台](https://qianfan.cloud.baidu.com/)

### 5. 数据库初始化

- 默认使用 MySQL（配置见 `utils/config.py`，数据库账号和密码自己填），也可以改为 SQLite。
- 首次运行 SQL Agent 时会自动创建表结构并插入示例数据。

## 🚀 快速开始

### 交互模式（推荐）
```bash
python agent.py 
```

进入交互菜单后：
- 输入 `1` → 直接打字提问
- 输入 `2` → 上传 `.wav` 文件（例如 `test.wav`）
- 输入 `0` → 退出对话

每次回答后，可选择是否将回答转为语音（MP3 保存至 `temp_audio/` 目录）。

### 指定线程和用户
```bash
python agent.py --thread 5 --user 123
```

## 📂 项目结构

```
AI_project/
├── agent.py                 # 主程序入口
├── utils/                   # 工具模块
│   ├── asr.py               # 语音识别 (Qwen3-ASR-Flash)
│   ├── tts.py               # 语音合成 (Edge-TTS)
│   ├── baidu_search.py      # 百度搜索封装
│   ├── config.py            # 配置（数据库等）
│   ├── llms.py              # 大模型初始化
│   ├── logger.py            # 日志管理
│   ├── memory_sqlite.py     # 对话记忆 (SQLite)
│   ├── models.py            # 数据模型 & 系统提示词
│   ├── rag_medical.py       # 医学知识库检索 (Chroma)
│   ├── sql_agent.py         # SQL 查询代理
│   ├── tools.py             # 工具注册
│   └── .env                 # 敏感环境变量
├── data/                    # 数据库及知识文件
│   ├── medical_content.txt  # 医学知识条文
│   ├── schema_mysql.sql     # MySQL 数据库（如使用）
│   └── memory.db            # 对话记忆数据库
├── temp_audio/              # 回答语音输出目录（自动创建）
├── requirements.txt         # 依赖包列表
└── README.md
```

## 📝 使用示例

### 示例 1：文本查询医学知识
```
请选择输入方式 (1/2/0): 1
📝 请输入文本: 骨质疏松的定义和临床表现是什么？
🤖 AI 正在思考...
💬 回答：骨质疏松是一种代谢性骨病，特征是骨量减少、骨微结构破坏...
🔧 使用工具：rag_medical
📚 医学知识：第1条：骨质疏松定义...
🔊 是否将回答转为语音？(y/n): y
✅ 语音已保存至: temp_audio/response_abc123.mp3
```

### 示例 2：上传语音文件查询最新资讯
```
请选择输入方式 (1/2/0): 2
🎤 请输入 .wav 文件路径: test1.wav
📝 识别结果: 最近有什么治疗高血压的新药上市？
🤖 AI 正在思考...
💬 回答：根据最新信息，2025年国内批准了...
🔧 使用工具：tavily_search
🔊 是否将回答转为语音？(y/n): n
```

### 示例 3：查询数据库（用户信息）
```
请选择输入方式 (1/2/0): 1
📝 请输入文本: 显示所有用户的基本信息
🤖 AI 正在思考...
💬 回答：查询结果：用户表中有3条记录...
🔧 使用工具：sql_agent
🗄️ SQL结果：[(1, '张三', ...), (2, '李四', ...)]
```

## ⚙️ 高级配置

- **切换数据库类型**：修改 `utils/config.py` 中的 `DB_TYPE = "mysql"` 或 `"sqlite"`，并填入对应的 MySQL 连接信息。
- **自定义 TTS 音色**：修改 `utils/tts.py` 中的 `DEFAULT_VOICE`，可用 `edge-tts --list-voices` 查看所有音色。
- **调整医学知识库**：替换 `data/medical_content.txt` 内容，删除 `utils/chroma_medical` 文件夹后重启程序，会自动重建向量库。

## 🐛 常见问题

### 1. ASR 识别失败（`url error` 或 `InvalidParameter`）
- 检查 `DASHSCOPE_API_KEY` 是否正确配置且服务已开通。
- 确保音频格式为 **16kHz 单声道 PCM WAV**。可用 `pydub` 自动转换（已在 `asr.py` 中集成）。
- 尝试关闭代理或设置 `dashscope.base_http_api_url`。

### 2. 百度搜索返回空结果
- 确认 `.env` 中的 `BAIDU_API_KEY` 有效。
- 检查网络是否能正常访问 `qianfan.baidubce.com`。

### 3. 语音合成失败
- 确保已安装 `edge-tts`：`pip install edge-tts`
- 检查网络连接（Edge-TTS 需要访问微软服务）。

### 4. SQL Agent 连接 MySQL 失败
- 确认 MySQL 服务已启动，用户名、密码、数据库名正确。
- 如果提示 `pymysql` 缺失：`pip install pymysql`。
