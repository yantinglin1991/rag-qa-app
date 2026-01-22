import os, json

def main():
    base = os.path.join(os.path.dirname(__file__), "..", "data", "docs")
    base = os.path.abspath(base)
    out = os.path.join(os.path.dirname(__file__), "..", "data", "embeddings.json")
    embeddings = {}
    if os.path.isdir(base):
        for p in os.listdir(base):
            fp = os.path.join(base, p)
            if os.path.isfile(fp):
                with open(fp, "r", encoding="utf-8") as f:
                    text = f.read()
                embeddings[p] = [1.0] * 8
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(embeddings, f, ensure_ascii=False, indent=2)
    print("Embeddings written to", out)

if __name__ == "__main__":
    main()
