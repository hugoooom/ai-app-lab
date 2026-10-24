"""探测当前 API 账号支持哪个 embedding 模型。

用法：
    .\\.venv\\Scripts\\python.exe tools/check_embedding.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
)

CANDIDATES = [
    "embedding-3",
    "embedding-2",
    "text-embedding-3-small",
    "BAAI/bge-m3",
]

for model in CANDIDATES:
    try:
        resp = client.embeddings.create(model=model, input=["hello world"])
        dim = len(resp.data[0].embedding)
        print(f"OK    {model}  dim={dim}")
    except Exception as exc:
        message = str(exc).replace("\n", " ")[:160]
        print(f"FAIL  {model}  {message}")
