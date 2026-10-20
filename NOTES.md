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
