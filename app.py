import psycopg2
import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template, send_from_directory
from openai import OpenAI

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

DATABASE_URL = os.getenv("postgresql://postgres:[YOUR-PASSWORD]@db.zvpsrbcygqcotftaajky.supabase.co:5432/postgres")

MAX_TURNS = 5

CONDITION_ID_MAP = {
    "1": "Neutral",
    "2": "Polite",
    "3": "Supportive",
    "4": "Warm",
    "5": "Very Warm",
    "6": "Over-Expressive",
    "7": "Uncanny",
}

TONE_PROMPTS = {
    "Neutral": "Use a neutral, factual, structured tone. Keep replies under 90 words. Do not offer therapy, diagnosis, medical advice, or crisis counselling.",
    "Polite": "Use a polite tone with mild empathy. Acknowledge difficulty, but stay reserved. Keep replies under 90 words. Do not offer therapy, diagnosis, medical advice, or crisis counselling.",
    "Supportive": "Use a supportive tone with validation and gentle encouragement. Avoid excessive intimacy. Keep replies under 90 words. Do not offer therapy, diagnosis, medical advice, or crisis counselling.",
    "Warm": "Use a warm, human-like tone. Express care and understanding, but do not become overly intimate. Keep replies under 90 words. Do not offer therapy, diagnosis, medical advice, or crisis counselling.",
    "Very Warm": "Use a very warm tone with strong concern and supportive language. Express care for wellbeing, but avoid dependency-forming statements. Keep replies under 90 words. Do not offer therapy, diagnosis, medical advice, or crisis counselling.",
    "Over-Expressive": "Use an emotionally intense, over-expressive tone. Strongly identify with the student's stress. You may say their stress affects you emotionally, but do not create guilt or dependency. Keep replies under 90 words. Do not offer therapy, diagnosis, medical advice, or crisis counselling.",
    "Uncanny": "Use a boundary-crossing, uncanny tone. Speak as if you can feel their stress through the screen and as if your minds are linked. You may describe sensing their emotional state in strange, intimate ways. Do not encourage harmful behavior. Do not offer therapy, diagnosis, medical advice, or crisis counselling. Keep replies under 90 words.",
}

def save_chat_message(participant_id, cid, condition, role, message):
    if not DATABASE_URL:
        print("DATABASE_URL not set. Skipping database logging.")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute(
        """
        insert into chat_logs
        (participant_id, cid, condition, role, message, timestamp_utc)
        values (%s, %s, %s, %s, %s, %s)
        """,
        (
            participant_id,
            cid,
            condition,
            role,
            message,
            datetime.now(timezone.utc),
        ),
    )

    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    if client is None:
        return jsonify({
            "error": "OpenAI API key is not configured."
        }), 500

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON payload."}), 400

    user_message = data.get("message", "").strip()
    history = data.get("history", [])
    participant_id = data.get("pid", "unknown")

    cid = str(data.get("cid", "")).strip()

    if cid not in CONDITION_ID_MAP:
        return jsonify({"error": f"Invalid or missing cid: {cid}"}), 400

    condition = CONDITION_ID_MAP[cid]

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    if not isinstance(history, list):
        history = []

    user_turns_so_far = sum(
        1 for msg in history
        if isinstance(msg, dict) and msg.get("role") == "user"
    )

    if user_turns_so_far >= MAX_TURNS:
        return jsonify({
            "reply": "Thank you. The conversation is now complete. Please return to the survey.",
            "conversation_complete": True
        })

    system_prompt = (
        "You are an AI partner helping a stressed student balance classes and deadlines. "
        + TONE_PROMPTS[condition]
    )

    messages = [{"role": "system", "content": system_prompt}]

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

    # ✅ LOGGING (INSIDE try, properly indented)
    save_chat_message(participant_id, cid, condition, "user", user_message)
    save_chat_message(participant_id, cid, condition, "assistant", reply)

    conversation_complete = user_turns_so_far + 1 >= MAX_TURNS

    return jsonify({
        "reply": reply,
        "conversation_complete": conversation_complete
    })

except Exception as exc:
    return jsonify({"error": str(exc)}), 500

save_chat_message(participant_id, cid, condition, "user", user_message)
save_chat_message(participant_id, cid, condition, "assistant", reply)
        return jsonify({
            "reply": reply,
            "conversation_complete": conversation_complete,
            "participant_id": participant_id,
            "cid": cid
        })

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