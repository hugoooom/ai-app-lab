# AI App Lab

一个从零搭起来的 AI 应用，走完了这条链路：

**文本处理 → FastAPI 服务 → 大模型接入 → 多轮记忆 → RAG 检索问答 → 极简前端**

没有框架脚手架，没有前端构建，每一步的取舍和踩坑都记在 [NOTES.md](NOTES.md) 里。

## 能做什么

- 上传 PDF，自动抽取文字、切分、向量化
- 用自然语言提问，答案**只基于文档内容**，同时返回命中的原文片段和相似度
- 多轮对话，同一个会话共享上下文（SQLite 持久化）
- 单轮问答、词频统计（早期的练习，保留作对照）

## 架构

```
PDF ──pypdf──> 文本 ──split_text──> 分块 ──embedding──> 向量 ──> 内存库
                                                                  │
问题 ──embedding──> 向量 ──cosine 相似度──> Top-K 分块 ──> 拼 prompt ──> LLM ──> 回答
```

核心思路就是 RAG 的那句话：**先检索，再生成**。模型不知道你的文档，所以每次提问前，把最相关的几段原文递到它眼前。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

copy .env.example .env          # 填入 LLM_API_KEY
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

打开：

- **http://127.0.0.1:8000/ui** — 前端页面
- **http://127.0.0.1:8000/docs** — 交互式 API 文档

`.env` 三个变量：

```
LLM_API_KEY=你的key
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4-flash
```

默认接的是智谱，但用的是 OpenAI 兼容接口，换任何兼容服务商只改 `LLM_BASE_URL` 和 `LLM_MODEL`。

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 健康检查 |
| GET | `/top?n=5` | 词频 Top N |
| GET | `/ask?q=` | 单轮问答（无记忆） |
| GET | `/chat?q=&session_id=` | 多轮对话（有记忆） |
| GET | `/chat/{session_id}/history` | 查看会话历史 |
| POST | `/upload` | 上传 PDF：切分 + 向量化 + 入索引 |
| GET | `/doc/ask?q=&doc_id=&k=3` | 基于文档回答问题 |
| GET | `/ui` | 极简前端 |

示例：

```bash
curl -X POST http://127.0.0.1:8000/upload -F "file=@data/sample.pdf"
# {"doc_id":"sample.pdf","chars":1608,"chunks":4}

curl "http://127.0.0.1:8000/doc/ask?q=What%20is%20chunk%20overlap%3F&doc_id=sample.pdf&k=2"
# {"q":"...","answer":"...","sources":[{"score":0.5329,"text":"..."}]}
```

## 几个关键取舍

**切 500 字，重叠 50 字。** 太小一句话不完整，检索出来是碎片；太大一块里 90% 是无关内容，精度下降还费 token。重叠是为了防止一句话正好被切在边界上，两块都读不到完整语义。

**embedding 分批发送。** 接口一次最多 64 条，所以按「64 条 / 8000 字」双上限切批；返回结果按 `index` 回填，不假设顺序。

**问答时强制约束模型。** system prompt 明确「资料里没有就说不知道」，并把命中的原文和相似度一起返回，方便判断它是真读了资料还是在编。

**回答被截断时要让人知道。** `max_tokens` 是硬上限，模型写到一半会被切断。用 `finish_reason == "length"` 判断，接口返回 `truncated: true`，前端给出提示——不然用户会以为那就是完整答案。

**密钥只走环境变量。** `.env` 在 `.gitignore` 里，代码里没有硬编码的 key。

## 已知限制

这是一个学习项目，不是生产系统：

- 向量只存在进程内存里，**服务重启就丢**，需要重新上传
- 没有鉴权、没有限流，`session_id` 谁拿到谁能读
- SQLite 存对话，单机可用，不支持并发写入
- 还没有评测集 —— 检索效果目前靠肉眼看，这不可靠

## 下一步

- [ ] 检索评测：50 条问题 + 标准答案，量出召回率，再调 chunk 参数
- [ ] 向量持久化（SQLite 存 JSON / Chroma）
- [ ] 流式输出
- [ ] 部署到公网

## 技术栈

Python 3.13 · FastAPI · Uvicorn · OpenAI 兼容 SDK（智谱 `glm-4-flash` / `embedding-3`）· SQLite · pypdf

前端是一张 HTML，没有任何框架或构建步骤。

## 目录结构

```
.
├── app.py                # FastAPI 路由
├── rag.py                # 抽取 / 切分 / 向量化 / 检索
├── db.py                 # SQLite 会话存储
├── day1_word_freq.py     # 词频统计（Day 1）
├── static/index.html     # 前端页面
├── tools/                # 测试辅助脚本
├── data/sample.pdf       # 测试文档
├── NOTES.md              # 每日学习记录
└── requirements.txt
```

## 关于这个仓库

起因是想搞清楚 RAG 到底是怎么运转的，所以没有直接拿现成框架拼，而是把每一步拆开自己写一遍：怎么切、怎么算相似度、怎么拼 prompt、怎么防止模型瞎编。

`NOTES.md` 记录了每天做了什么、卡在哪、后来怎么想通的——比 README 更接近真实过程。
