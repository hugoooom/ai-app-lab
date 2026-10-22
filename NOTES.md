# 学习日志

按天记录，不修饰。写给自己，也写给以后想看这个人怎么学的人。

---

## Day 1 · 2026-10-19

**目标**：跑通环境，写出第一个完整程序（词频统计），建 git 仓库。

**完成**

- 词频统计：读文件 → 分词 → 字典计数 → 排序取 Top 10
- 加停用词过滤后，`the` 掉出榜单，`system 4` 升到第一
- 第一次 commit

**踩坑**

- 会语法不等于会写程序。`split()`、`dict` 都懂，但要写一个"读文件→处理→输出"的完整程序时卡住了。
- `strip(chars)` 是"去掉两端的这些字符"，不是"去掉这个字符串"。这是当时卡最久的一个点。
- 函数写完后 `return` 下面还留着 `pass`，死代码，自己没发现。

**命令**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe day1_word_freq.py
```

---

## Day 2 · 2026-10-20

**目标**：把脚本变成 HTTP 接口。

**完成**

- FastAPI 封装 `GET /top?n=`，复用 Day 1 的四个函数
- `Query(ge=1, le=50)` 参数校验，`n=100` 返回 422
- `/docs` 自动生成 Swagger 交互文档

**踩坑**

- `pip install` 之后仍然 `ModuleNotFoundError`：用的是系统 Python `D:\python\python.exe`，包装在项目的 `.venv` 里。**用哪个 python.exe，就用哪个环境的包。**
- `python app.py` 不会启动服务。`app.py` 只定义了 `app` 对象，启动要靠 `python -m uvicorn app:app`，`app:app` 是"模块:变量"。
- import 写了 `tokeniz`，少一个 `e`。Python 3.13 直接提示 `Did you mean: 'tokenize'?`——报错信息值得读。
- PyCharm 一直标红，但解释器和包都对。是索引缓存过期，清缓存重启才消失。**编辑器标红不等于代码错，能不能跑由终端说了算。**
- `pass` 返回 `None`，但返回注解写的是 `-> list[dict]`，FastAPI 校验失败，接口返回 500。类型注解不是装饰，是真会拿来校验的。

**命令**

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

**复盘**

- Python 报错只看最后一行，前面的是调用栈。
- 看到 `ModuleNotFoundError`，第一反应是"我现在用的是哪个 Python"。
- 一个函数卡 20 分钟就先跳过；整体卡 2 小时就求助，不硬耗。

---

## Day 3 · 2026-10-21

**目标**：把大模型接进接口。

**完成**

- 用 OpenAI 兼容 SDK 接智谱 `glm-4-flash`
- `GET /ask?q=` 返回模型回答
- key 放 `.env`，`.gitignore` 里排掉，不进仓库

**踩坑**

- 老师没教过 SDK，看到 `client.chat.completions.create(...)` 一脸懵。后来知道所有库的读法都一样：先看必填参数（`inspect.signature`），再看官方 quickstart，最后写最小脚本。
- 改完 `.env` 没重启服务，一直 401。`--reload` 只监听 `.py`，不会重新读 `.env`。
- 模型的回答是错的：把 RAG 解释成"对话式检索技术"。**调通 ≠ 答对**，这就是以后要做评测集的原因。

**命令**

```powershell
.\.venv\Scripts\python.exe try_llm.py
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

**复盘**

- 先让最小脚本跑通，再集成进项目。一次只让一个变量出错。
- 读陌生库的三个动作：看签名 → 看 quickstart → 跑最小例子。

---

## Day 4 · 2026-10-22

**目标**：让模型"记住"上一句话。

**完成**

- `db.py`：SQLite 存储层，`init_db` / `save_message` / `load_messages`
- `GET /chat?q=&session_id=`：多轮对话
- `GET /chat/{session_id}/history`：查看某会话的历史
- 验证：同一个 session 里问"我叫什么"，它能答出"小明"；换个 session 就不知道了

**踩坑 / 想明白的事**

- 模型没有记忆。所谓"多轮对话"，是每次把历史重新拼进 `messages` 再发过去。记忆存在自己这边。
- `messages` 的顺序是硬性的：system 在最前，历史在中间，这一句在最后。
- SQL 必须用 `?` 占位符。用 f-string 拼就是注入漏洞。
- `limit=10` 不是随便写的：上下文越长越贵越慢，还有窗口上限。

**命令**

```powershell
.\.venv\Scripts\python.exe db.py          # 单独测存储层
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

**复盘**

- 先测存储层，再接接口。分层测试比一把梭快。
- 换 session 验证隔离，是比"能用"更进一步的验证。
