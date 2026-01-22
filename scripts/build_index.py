import os, json

def main():
    base = os.path.join(os.path.dirname(__file__), "..", "data")
    emb = os.path.join(base, "embeddings.json")
    idx = os.path.join(base, "index.json")
    if os.path.exists(emb):
        with open(emb, "r", encoding="utf-8") as f:
            e = json.load(f)
    else:
        e = {}
    index = {"items": list(e.keys())}
    os.makedirs(base, exist_ok=True)
    with open(idx, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print("Index written to", idx)

if __name__ == "__main__":
    main()
