# rerank_demo.py —— 对比"向量召回(bi-encoder)" vs "LLM重排(cross-encoder)"
import os, sys, re, requests, numpy as np

sys.stdout.reconfigure(encoding="utf-8")
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

EMB = "bge-m3"          # 算向量(bi-encoder)
LLM = "qwen2.5:7b"      # 当 cross-encoder 打分

QUERY = "茅台在海外市场的扩张计划"
DOCS = [
    "贵州茅台计划2027年将海外营收占比提升至8%，正在扩张东南亚经销网络。",  # 真相关
    "贵州茅台的酿造工艺需要多次蒸馏和长期窖藏，是其品质的核心。",           # 提了茅台,但跟海外无关(陷阱)
    "贵州茅台董事长陈华表示，公司目前暂无拆股计划。",                       # 提了茅台,但无关
    "比亚迪在欧洲新能源汽车市场销量大增，海外扩张顺利。",                   # 提了海外扩张,但不是茅台(陷阱)
    "今天天气不错，适合出去散步。",                                       # 完全无关
]

def embed(t):
    r = requests.post("http://localhost:11434/api/embeddings",
                      json={"model": EMB, "prompt": t}, timeout=120)
    return np.array(r.json()["embedding"])

def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

def llm_score(q, d):
    # cross-encoder 的精髓:问题和文档"一起"喂给模型,让它直接判相关性
    prompt = (f"问题：{q}\n文档：{d}\n"
              f"这份文档对回答上面这个问题的相关性有多高？只回答一个 0 到 10 的整数，别的都别说。")
    r = requests.post("http://localhost:11434/api/generate",
                      json={"model": LLM, "prompt": prompt, "stream": False}, timeout=120)
    m = re.search(r"\d+", r.json()["response"])     # 从回答里抠出那个数字
    return int(m.group()) if m else -1

qv = embed(QUERY)
print("查询:", QUERY, "\n")

# 每个分数只算一次,存成 (分数, 文档) 的列表,再排序
emb_scored = [(cos(qv, embed(d)), d) for d in DOCS]
llm_scored = [(llm_score(QUERY, d), d) for d in DOCS]

print("--- ① 向量召回 bi-encoder(按余弦排序)---")
for s, d in sorted(emb_scored, key=lambda x: -x[0]):
    print(f"  {s:.3f}   {d}")

print("\n--- ② LLM重排 cross-encoder(按相关性分排序)---")
for s, d in sorted(llm_scored, key=lambda x: -x[0]):
    print(f"  {s:>2}    {d}")
