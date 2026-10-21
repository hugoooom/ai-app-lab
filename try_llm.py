"""最小验证脚本：先脱离 FastAPI，确认大模型能调通。

用法：


跑通之后再去看 app.py 里的 /ask，要抄的只有中间那一段。
改完 .env 记得重新运行本脚本（.env 不会被自动重载）。
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 1. client：一个配好了 base_url 和 key 的 HTTP 客户端
#    它本身不发请求，只是记住"往哪发、拿什么证明身份"
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
)

# 2. messages：对话历史。模型没有记忆，每次都要把上下文一起传过去
#    system = 人设，user = 你说的话，assistant = 模型说过的话
resp = client.chat.completions.create(
    model=os.getenv("LLM_MODEL", "glm-4-flash"),
    messages=[
        {"role": "system", "content": "你是一个简洁的助手，用中文回答。"},
        {"role": "user", "content": "用一句话解释什么是 RAG"},
    ],
    max_tokens=200,
)

# 3. resp 是一个对象，不是字符串。回答藏在 choices[0].message.content
print("type:  ", type(resp).__name__)
print("model: ", resp.model)
print("tokens:", resp.usage.total_tokens)
print("answer:", resp.choices[0].message.content)
