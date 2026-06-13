# compare_embed.py —— 自己玩:对比不同 embedding 模型的"语义分辨力"
import os, sys, requests, numpy as np

sys.stdout.reconfigure(encoding="utf-8")          # 终端正常显示中文
os.environ["NO_PROXY"] = "localhost,127.0.0.1"    # 本地请求不走 Clash 代理

# ───── 你改这两块就行 ─────
BASE   = "贵州茅台"                                  # 基准词
OTHERS = ["贵州茅台", "五粮液", "白酒龙头", "新能源汽车", "今天晚饭吃什么"]   # 跟它比的一串
MODELS = ["nomic-embed-text", "bge-m3"]            # 要对比的模型(Ollama 里有的)
# ──────────────────────────

def embed(model, text):
    r = requests.post("http://localhost:11434/api/embeddings",
                      json={"model": model, "prompt": text}, timeout=120)
    return np.array(r.json()["embedding"])

def cosine(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

for m in MODELS:
    print(f"=== {m} ===")
    base_vec = embed(m, BASE)
    for w in OTHERS:
        print(f"  {cosine(base_vec, embed(m, w)):.4f}   {BASE}  vs  {w}")
    print()
