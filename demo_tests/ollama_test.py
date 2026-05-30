"""
ollama_test.py
Verifies Ollama server + model responds.

Run from repo root:
    python demo_tests/ollama_test.py --model llama3.2:1b
"""
import argparse, json, sys, urllib.request


def post_json(url: str, payload: dict, timeout=60):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default="http://localhost:11434")
    ap.add_argument("--model", default="llama3.2:1b")
    args = ap.parse_args()

    url = args.server.rstrip("/") + "/api/generate"
    payload = {"model": args.model, "prompt": "Return the word OK if you can read this.", "stream": False}

    print("=== OLLAMA TEST ===")
    print(f"Server: {args.server}")
    print(f"Model : {args.model}")

    try:
        raw = post_json(url, payload, timeout=60)
        j = json.loads(raw)
        out = (j.get("response") or "").strip()
        print(f"Response: {out[:200]}")
        if out:
            print("PASS: Ollama server reachable and generate returned.")
        else:
            print("WARN: Ollama responded but output was empty.")
    except Exception as e:
        print("FAIL:", repr(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
