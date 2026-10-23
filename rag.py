"""PDF 读取与文本切分。

RAG 的第一步：把文档变成一段一段的文本。

为什么不直接整篇丢给模型：
- 上下文窗口有限，几十页文档放不进去
- 检索需要"精确到一段"，整篇召回等于没召回
- token 越多越贵越慢
"""

from pathlib import Path

from pypdf import PdfReader


def extract_text(pdf_path: Path) -> str:
    """把 PDF 每一页的文字抽出来，拼成一个字符串。"""
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """把长文本切成大小相近的块。

    要求：
    - 每块最多 chunk_size 个字符
    - 相邻两块之间重叠 overlap 个字符
      （防止一句话正好被切断，两边都读不到完整语义）
    - 每块去掉首尾空白，空块丢掉
    - 切完不能丢内容：把所有块拼起来（去掉重叠部分）应该覆盖原文
    """
    n=0
    ans=[]
    while len(text)-n>chunk_size:
        ans.append(text[n:n+chunk_size])
        n+=chunk_size-overlap
    ans.append(text[n:])
    return ans
