"""PDF 读取、文本切分、向量化、检索。

这是 RAG 的全部核心：

    PDF ──抽取──> 文本 ──切分──> 卡片 ──向量化──> 数字
                                                     │
    问题 ──向量化──> 数字 ──算相似度──> 最像的几张卡片 ──> 交给模型

为什么不直接全文喂给模型：
- 上下文窗口有限，几十页放不进去
- token 越多越贵越慢
- 内容一多模型抓不住重点

为什么向量能做"按意思找"：
- 每段文字变成 2048 个数字，意思相近的段落，数字也相近
- "先检索再生成"的核心就是这个相似度计算
"""

import math
import os
from pathlib import Path

from openai import OpenAI
from pypdf import PdfReader

EMBED_MODEL = os.getenv("LLM_EMBED_MODEL", "embedding-3")

# 单次 embedding 请求的上限：条数 + 总字符数（服务商限制，超了会报 1214）
EMBED_BATCH_SIZE = 64
EMBED_BATCH_CHARS = 8000

# 内存里的知识库：doc_id -> [{"text": ..., "vector": [...]}, ...]
# 注意：进程重启就没了。真实项目会存进向量数据库。
STORE: dict[str, list[dict]] = {}


def extract_text(pdf_path: Path) -> str:
    """把 PDF 每一页的文字抽出来，拼成一个字符串。"""
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """把长文本切成大小相近的块。
    - 每块最多 chunk_size 个字符
    - 相邻两块之间重叠 overlap 个字符
      （防止一句话正好被切断，两边都读不到完整语义）
    - 每块去掉首尾空白，空块丢掉
    - 切完不能丢内容：把所有块拼起来（去掉重叠部分）应该覆盖原文
    """
    n = 0
    ans = []
    while len(text) - n > chunk_size:
        piece = text[n:n + chunk_size].strip()
        if piece:
            ans.append(piece)
        n += chunk_size - overlap
    piece = text[n:].strip()
    if piece:
        ans.append(piece)
    return ans


def embed_texts(client: OpenAI, texts: list[str]) -> list[list[float]]:
    """把一组文本变成向量。

    接口一次最多接受 64 条，所以得分批。
    同时限制每批的总字符数：有的服务商还卡 token 上限。
    """
    vectors: list[list[float]] = []
    batch: list[str] = []
    chars = 0

    for text in texts:
        too_many = len(batch) >= EMBED_BATCH_SIZE
        too_long = chars + len(text) > EMBED_BATCH_CHARS
        if batch and (too_many or too_long):
            vectors.extend(_embed_batch(client, batch))
            batch, chars = [], 0
        batch.append(text)
        chars += len(text)

    if batch:
        vectors.extend(_embed_batch(client, batch))
    return vectors


def _embed_batch(client: OpenAI, texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    # 不要假设返回顺序和输入一致，按 index 放回原位
    ordered: list[list[float] | None] = [None] * len(texts)
    for item in resp.data:
        ordered[item.index] = item.embedding
    return [vec for vec in ordered if vec is not None]


def cosine(a: list[float], b: list[float]) -> float:
    """余弦相似度：两个向量的夹角余弦，越接近 1 越相似。

    公式：dot(a, b) / (|a| * |b|)
    """
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def add_document(client: OpenAI, doc_id: str, text: str) -> int:
    """切分 + 向量化 + 存进内存。返回块数。"""
    chunks = split_text(text)
    vectors = embed_texts(client, chunks)
    STORE[doc_id] = [
        {"text": chunk, "vector": vector}
        for chunk, vector in zip(chunks, vectors)
    ]
    return len(chunks)


def search(client: OpenAI, doc_id: str, question: str, k: int = 3) -> list[dict]:
    """找出和问题最像的 k 张卡片。"""
    items = STORE.get(doc_id)
    if not items:
        return []

    query_vector = embed_texts(client, [question])[0]
    scored = [
        {"score": round(cosine(query_vector, item["vector"]), 4), "text": item["text"]}
        for item in items
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k]
