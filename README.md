# AI App Lab

一个从零开始长起来的 AI 应用开发练习仓库：从最基础的词频统计，逐步做成带 LLM、数据库和公网部署的完整服务。


## 进度

| Day | 内容 | 状态 |
|---|---|---|
| 1 | 词频统计（文件 / 字典 / 排序） | ✅ |
| 2 | FastAPI 封装 `GET /top` 接口 | ✅ |
| 3 | 接入 LLM API，`GET /ask` 问答 | ✅ |
| 4 | SQLite 存对话历史，`GET /chat` 多轮对话 | ✅ |
| 5 | 部署到公网 | ⏳ |

## 接口

### `GET /`

健康检查。

```json
{"hello": "world"}
```

### `GET /top?n=5`

返回文本中出现频率最高的 n 个词，`n` 取值 1–50。

```json
[
  {"word": "system", "count": 4},
  {"word": "way", "count": 2},
  {"word": "build", "count": 2},
  {"word": "application", "count": 2},
  {"word": "data", "count": 2}
]
```

参数越界会返回 `422`，由 FastAPI 的参数校验自动处理。

### `GET /ask?q=...`

调用大模型回答，`q` 长度 1–500。

```json
{"q": "用一句话解释什么是 RAG", "answer": "..."}
```

需要在 `.env` 里配置 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`，参考 `.env.example`。

### `GET /chat?q=...&session_id=...`

多轮对话。同一个 `session_id` 共享上下文，不同 `session_id` 互不可见。

```json
{"session_id": "test1", "answer": "你叫小明。"}
```

历史存在 SQLite 的 `chat.db`（已 gitignore），默认取最近 10 条作为上下文。

### `GET /chat/{session_id}/history`

查看某个会话存下来的全部消息，用于调试。

```json
[{"role": "user", "content": "我叫小明"}, {"role": "assistant", "content": "你好，小明！"}]
```

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

启动后打开 http://127.0.0.1:8000/docs 可以直接调试接口。

## 部署

线上地址：`https://ai-app-lab.onrender.com`（部署完成后替换成真实地址）

平台是 Render 的免费 Web Service，连接 GitHub 仓库，每次 push 自动部署。

| 配置项 | 值 |
|---|---|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| 环境变量 | `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` |

两个必须知道的限制：

- `.env` 不会上传，密钥在平台后台的环境变量里配置。
- 免费实例的文件系统是临时的，`chat.db` 重启即清空；闲置一段时间会休眠，冷启动要等 30–60 秒。演示够用，生产要换成托管数据库。

## 技术栈

- Python 3.13
- FastAPI + Uvicorn
- 大模型：OpenAI 兼容接口（默认智谱 `glm-4-flash`）
- 词频统计为纯标准库实现，无第三方依赖

## 目录结构

```
.
├── app.py              # FastAPI 应用（路由层）
├── db.py               # SQLite 存储层
├── day1_word_freq.py   # 词频统计核心逻辑
├── try_llm.py          # 最小验证脚本（单独测大模型连通性）
├── data/sample.txt     # 测试文本
├── .env.example        # 环境变量模板（复制成 .env 后填 key）
├── requirements.txt
└── NOTES.md            # 每日学习记录（踩坑、命令、复盘）
```

## 说明

- `NOTES.md` 是每天的学习日志，记录原文、命令和踩过的坑，不追求好看。
- 这个仓库会一直往上加，不做重开。
