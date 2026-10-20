# Day 1 · 从能跑开始

90 分钟，只做三件事：跑通环境、写出第一个完整程序、提交一次 git。

## 环境（已确认）

- Python 3.13.9 ✓
- Git 2.54 ✓

## 命令（PowerShell）

```powershell
cd C:\Users\鼎室\Desktop\deepseek\deepsleep\ai-start
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python day1_word_freq.py
```

激活时报「禁止运行脚本」不用管，直接用解释器跑：

```powershell
.\.venv\Scripts\python.exe day1_word_freq.py
```

## 今天的任务

`day1_word_freq.py` 里有 4 个空函数，把它们填完：

1. `load_text` — 读文件
2. `tokenize` — 转小写、按空白切、去标点
3. `count_words` — 统计次数
4. `top_n` — 排序取前 10

`main()` 已经写好了，别改。填完直接运行。

## 验收标准

- 输出 10 行，每行 `word count`
- **第一行是 `the 9`**
- 不报错

## 卡住怎么办

- 一个函数卡 20 分钟 → 先跳过，写下一个，回头再补
- 整体卡 2 小时 → 把报错和你的代码贴出来问，别硬耗
- **不许搜「词频统计 Python 代码」**；可以搜「Python 怎么读文件」「dict 怎么按 value 排序」

区别在于：查 API 可以，抄答案不行。

## 做完之后（还有时间的话）

1. 自己造一个 `data/sample.csv`，写第二个程序：读 CSV，算某一列的和
2. `git init` → `git add .` → `git commit -m "day1: word frequency"`

## 明天

D2：给这个脚本套一个 FastAPI 接口，`GET /top?n=10` 返回 JSON。

---

# Day 2 · 把脚本变成接口

## 装依赖（在**你自己的** PowerShell 窗口里跑）

```powershell
cd C:\Users\鼎室\Desktop\deepseek\deepsleep\ai-start
.\.venv\Scripts\python.exe -m pip install fastapi "uvicorn[standard]" -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 启动

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

然后打开：

- http://127.0.0.1:8000/top?n=5
- http://127.0.0.1:8000/docs ← 这个会给你惊喜

端口被占用就加 `--port 8001`。

## 任务

`app.py` 里 `/top` 函数有一个 TODO，五步都在注释里。补完就行。

## 验收标准

- `/top?n=5` 返回 JSON 数组
- 第一个元素是 `{"word": "system", "count": 4}`
- `/docs` 里能直接点「Try it out」调通

## 概念（做完再看）

- **路由**：URL 路径 → 函数
- **查询参数**：`?n=5` → 函数参数 `n`，`Query(ge=1, le=50)` 做校验
- **自动文档**：FastAPI 读你的类型注解，自动生成 Swagger UI
- **序列化**：你返回 Python 的 dict / list，框架自动转 JSON。这就是为什么第 5 步要把 tuple 转成 dict

## 加分题（做完主任务再说）

加一个 `GET /word/{w}`，返回某个词的次数。提示：路径参数是 `@app.get("/word/{w}")` + `def word(w: str)`。
