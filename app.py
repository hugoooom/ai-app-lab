"""AI App Lab · FastAPI 服务

启动：
    .\\.venv\\Scripts\\python.exe -m uvicorn app:app --reload

接口：
    GET /            健康检查
    GET /top?n=5     词频 Top N
    GET /ask?q=...   调用大模型回答（Day 3，待实现）

任务：补完 /ask 里的 TODO。
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from openai import OpenAI

from day1_word_freq import DATA, count_words, load_text, tokenize, top_n

load_dotenv()

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
    # TODO（Day 3 就这一件事）：
    # 1. resp = client.chat.completions.create(...)
    #      参数：
    #        model=MODEL
    #        messages=[
    #            {"role": "system", "content": "你是一个简洁的助手，用中文回答。"},
    #            {"role": "user", "content": q},
    #        ]
    #        max_tokens=200
    # 2. answer = resp.choices[0].message.content
    # 3. return {"q": q, "answer": answer}
    pass
