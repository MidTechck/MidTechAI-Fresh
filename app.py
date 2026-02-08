from flask import Flask, request, jsonify, render_template
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import json
import pyttsx3
import speech_recognition as sr
import os
from gtts import gTTS

app = Flask(__name__)

# --- Load Flan-T5 Model ---
model_name = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# --- Memory file ---
MEMORY_FILE = "knowledge.json"

# Initialize memory
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
else:
    memory = {}

# --- Voice Engine ---
engine = pyttsx3.init()
engine.setProperty('rate', 170)   # speaking speed
engine.setProperty('voice', 'english+f3')  # female voice, adjust if needed

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

# --- Generate AI Response ---
def generate_response(prompt, user_id="default"):
    # Remember user context
    user_context = memory.get(user_id, "")
    full_prompt = f"User: {prompt}\nContext: {user_context}\nAssistant:"
    
    inputs = tokenizer(full_prompt, return_tensors="pt").input_ids
    outputs = model.generate(inputs, max_length=500)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Update memory
    memory[user_id] = user_context + "\nUser: " + prompt + "\nAssistant: " + response
    save_memory()
    
    return response

# --- Convert Text to Speech ---
def speak_text(text, filename="response.mp3"):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    return filename

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    prompt = data.get("prompt", "")
    user_id = data.get("user_id", "default")
    
    # Generate response
    response = generate_response(prompt, user_id)
    
    # Convert to voice
    audio_file = speak_text(response)
    
    return jsonify({"response": response, "audio_file": audio_file})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
