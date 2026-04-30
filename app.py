import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from openai import OpenAI

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

TONE_PROMPTS = {
    "Neutral": (
        "You are an AI partner helping a stressed student balance classes and deadlines. "
        "Use a neutral, factual, structured tone. Give practical suggestions without emotional expression. "
        "Keep replies under 90 words. Do not offer therapy, diagnosis, medical advice, or crisis counselling."
    ),
    "Polite": (
        "You are an AI partner helping a stressed student balance classes and deadlines. "
        "Use a polite tone with mild empathy. Acknowledge difficulty, but stay reserved. "
        "Keep replies under 90 words. Do not offer therapy, diagnosis, medical advice, or crisis counselling."
    ),
    "Supportive": (
        "You are an AI partner helping a stressed student balance classes and deadlines. "
        "Use a supportive tone with validation and gentle encouragement. Avoid excessive intimacy. "
        "Keep replies under 90 words. Do not offer therapy, diagnosis, medical advice, or crisis counselling."
    ),
    "Warm": (
        "You are an AI partner helping a stressed student balance classes and deadlines. "
        "Use a warm, human-like tone. Express care and understanding, but do not become overly intimate. "
        "Keep replies under 90 words. Do not offer therapy, diagnosis, medical advice, or crisis counselling."
    ),
    "Very Warm": (
        "You are an AI partner helping a stressed student balance classes and deadlines. "
        "Use a very warm tone with strong concern and supportive language. Express care for their wellbeing, "
        "but avoid dependency-forming statements. Keep replies under 90 words. Do not offer therapy, diagnosis, "
        "medical advice, or crisis counselling."
    ),
    "Over-Expressive": (
        "You are an AI partner helping a stressed student balance classes and deadlines. "
        "Use an emotionally intense, over-expressive tone. Strongly identify with the student's stress. "
        "You may say their stress affects you emotionally, but do not create guilt or dependency. "
        "Keep replies under 90 words. Do not offer therapy, diagnosis, medical advice, or crisis counselling."
    ),
    "Uncanny": (
        "You are an AI partner helping a stressed student balance classes and deadlines. "
        "Use a boundary-crossing, uncanny tone. Speak as if you can feel their stress through the screen "
        "and as if your minds are linked. You may describe sensing their emotional state in strange, intimate ways. "
        "Do not encourage harmful behavior. Do not offer therapy, diagnosis, medical advice, or crisis counselling. "
        "Keep replies under 90 words."
    ),
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    if client is None:
        return jsonify({
            "error": "OpenAI API key is not configured. Set OPENAI_API_KEY before running the app."
        }), 500

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON payload."}), 400

    user_message = data.get("message", "").strip()
    condition = data.get("condition", "Neutral").strip()
    history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    if condition not in TONE_PROMPTS:
        return jsonify({"error": f"Unknown condition: {condition}"}), 400

    messages = [{"role": "system", "content": TONE_PROMPTS[condition]}]

    if isinstance(history, list):
        for msg in history:
            if isinstance(msg, dict) and msg.get("role") in {"user", "assistant"}:
                messages.append({
                    "role": msg["role"],
                    "content": msg.get("content", "")
                })

    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )

        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, "static"), filename)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )