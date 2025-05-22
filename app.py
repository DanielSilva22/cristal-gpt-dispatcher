from flask import Flask, request, jsonify
import os
import json
from git import Repo

app = Flask(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
REPO_URL = f"https://{GITHUB_TOKEN}@github.com/DanielSilva22/cristal-semantique-core1.git"
LOCAL_REPO = "/tmp/gpt-dispatcher"

@app.route("/", methods=["GET"])
def home():
    return "GPT Dispatcher ready", 200

@app.route("/push", methods=["POST"])
def push_queue_file():
    payload = request.get_json()
    filename = payload.get("filename")
    data = payload.get("data")

    if not filename or not data:
        return jsonify({"error": "filename or data missing"}), 400

    if not os.path.exists(LOCAL_REPO):
        Repo.clone_from(REPO_URL, LOCAL_REPO)

    queue_path = os.path.join(LOCAL_REPO, "queue")
    os.makedirs(queue_path, exist_ok=True)

    full_path = os.path.join(queue_path, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))

    repo = Repo(LOCAL_REPO)
    repo.git.add(full_path)
    repo.index.commit(f"[GPT Dispatcher] {filename}")
    repo.remote().push()

    return jsonify({"status": "pushed", "file": filename}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
