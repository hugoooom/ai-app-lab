"""AI App Lab · FastAPI 服务

启动：
    .\\.venv\\Scripts\\python.exe -m uvicorn app:app --reload

接口：
    GET /                          健康检查
    GET /top?n=5                   词频 Top N
    GET /ask?q=...                 单轮问答（无记忆）
    GET /chat?q=...&session_id=    多轮对话（有记忆）
    GET /chat/{session_id}/history 查看某会话历史

任务：补完 /chat 里的 TODO。
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from openai import OpenAI

from day1_word_freq import DATA, count_words, load_text, tokenize, top_n
from db import init_db, load_messages, save_message

load_dotenv()
init_db()

app = FastAPI(title="AI App Lab API")

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
)
MODEL = os.getenv("LLM_MODEL", "glm-4-flash")


@app.get("/")
def root() -> dict:
    return {"hello": "world"}


@app.get("/top")
def top(n: int = Query(default=10, ge=1, le=50)) -> list[dict]:
    text = load_text(DATA)
    words = tokenize(text)
    counts = count_words(words)
    pairs = top_n(counts, n)
    ans = []
    for word, count in pairs:
        ans.append({"word": word, "count": count})
    return ans


@app.get("/ask")
def ask(q: str = Query(..., min_length=1, max_length=500)) -> dict:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一个简洁的助手，用中文回答。"},
            {"role": "user", "content": q},
        ],
        max_tokens=200,
    )
    answer = resp.choices[0].message.content
    return {"q": q, "answer": answer}


@app.get("/chat")
def chat(
    q: str = Query(..., min_length=1, max_length=500),
    session_id: str = Query(default="default", min_length=1, max_length=64),
) -> dict:
    history = load_messages(session_id)
    messages = [{"role": "system", "content": "你是一个简洁的助手，用中文回答。"}] + history + [{"role": "user", "content": q}]
    resp = client.chat.completions.create(model=MODEL, messages=messages, max_tokens=300)
    answer = resp.choices[0].message.content
    save_message(session_id, "user", q)
    save_message(session_id, "assistant", answer)
    return {"session_id": session_id, "answer": answer}


@app.get("/chat/{session_id}/history")
def chat_history(session_id: str) -> list[dict]:
    return load_messages(session_id, limit=50)
