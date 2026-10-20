"""Day 2 · 把词频统计变成 HTTP 接口

启动：
    .\\.venv\\Scripts\\python.exe -m uvicorn app:app --reload

打开：
    http://127.0.0.1:8000/top?n=5
    http://127.0.0.1:8000/docs

任务：补完 /top 里的 TODO（五步，注释里写清楚了）。
"""

from fastapi import FastAPI, Query

from day1_word_freq import DATA, count_words, load_text, tokenize, top_n

app = FastAPI(title="Word Frequency API")


@app.get("/")
def root() -> dict:
    return {"hello": "world"}


@app.get("/top")
def top(n: int = Query(default=10, ge=1, le=50)) -> list[dict]:
    # TODO:
    # 1. text = load_text(DATA)
    # 2. words = tokenize(text)
    # 3. counts = count_words(words)
    # 4. pairs = top_n(counts, n)          -> [("system", 4), ("way", 2), ...]
    # 5. 把 pairs 转成 [{"word": ..., "count": ...}, ...] 并 return
    pass
