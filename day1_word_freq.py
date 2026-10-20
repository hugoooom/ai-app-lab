"""Day 1 · 词频统计

把 data/sample.txt 里出现次数最多的 10 个词打印出来。
输出格式：每行 `word count`，按次数从高到低。

规则：
- 全部转小写
- 按空白分词
- 去掉单词两端的标点
- 空字符串不算

先自己写。卡住超过 20 分钟，再去看 README 的提示。
"""

from pathlib import Path

DATA = Path(__file__).parent / "data" / "sample.txt"
PUNCT = ".,!?;:\"'()[]{}"
STOPWORDS = {"the", "is", "a", "an", "and", "of", "to", "in", "we", "are", "but", "that", "it"}

def load_text(path: Path) -> str:
    with open(path, mode='r', encoding='utf-8') as f:
        return f.read()

    pass  # TODO


def tokenize(text: str) -> list[str]:
    """转小写、按空白切分、去掉两端标点、丢掉空串。"""
    words = []
    for raw in text.lower().split():          # 无参数 split() = 按任意空白切
        w = raw.strip(PUNCT)                  # strip(chars) 才是"去掉两端的这些字符"
        if w:
            words.append(w)
    return words

def count_words(words: list[str]) -> dict[str, int]:
    """统计每个词出现的次数。"""
    ans={}
    for i in words:
        if i in STOPWORDS:
            continue
        if i in ans:
            ans[i]+=1
        else:
            ans[i]=1
    return ans



def top_n(counts: dict[str, int], n: int = 10) -> list[tuple[str, int]]:
    """按次数从高到低排序，返回前 n 个 (词, 次数)。"""
    ans=[]
    for word, count in counts.items():
        ans.append((word, count))
    return sorted(ans, key=lambda x: x[1], reverse=True)[:n]



def main() -> None:
    text = load_text(DATA)
    words = tokenize(text)
    counts = count_words(words)
    for word, count in top_n(counts):
        print(word, count)


if __name__ == "__main__":
    main()
