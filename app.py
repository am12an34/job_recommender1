from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.route('/match_jobs', methods=['POST'])
def match_jobs():
    data = request.get_json()
    user_skills = data.get("skills", [])
    jobs = data.get("jobs", [])

    if not user_skills or not jobs:
        return jsonify({"error": "Skills or Jobs missing"}), 400

    try:
        user_embedding = model.encode(", ".join(user_skills), convert_to_tensor=True)
    except Exception as e:
        return jsonify({"error": "Failed to process skills", "details": str(e)}), 500

    job_texts = [f"{job['title']} {', '.join(job['required_skills'])}" for job in jobs]
    job_embeddings = model.encode(job_texts, convert_to_tensor=True)

    similarities = util.pytorch_cos_sim(user_embedding, job_embeddings)[0].tolist()
    matched_job_ids = [job["id"] for job, _ in sorted(zip(jobs, similarities), key=lambda x: x[1], reverse=True)]

    return jsonify({"matched_jobs": matched_job_ids})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
