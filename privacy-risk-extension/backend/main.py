from fastapi import FastAPI
from chunking import chunk_text
from pydantic import BaseModel
import requests
from fastapi.middleware.cors import CORSMiddleware
import json
import re
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

# ---------------------------
# CORS (Allow extension access)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"


# ---------------------------
# Request Model
# ---------------------------
class PolicyRequest(BaseModel):
    text: str


# ---------------------------
# Prompt Builder
# ---------------------------
def build_prompt(clause_text):
    return f"""
You are a privacy compliance analyst.

Return STRICT JSON only:

{{
  "mentions_biometric_data": true/false,
  "mentions_location_tracking": true/false,
  "mentions_camera_or_microphone": true/false,
  "data_retention_policy_present": true/false,
  "retention_duration_specified": true/false,
  "risk_reason": "brief explanation"
}}

Clause:
\"\"\"{clause_text}\"\"\"
"""


# ---------------------------
# Keyword Filtering (Huge Speed Boost)
# ---------------------------
KEYWORDS = [
    "biometric", "face", "fingerprint",
    "location", "gps", "tracking",
    "camera", "microphone",
    "retain", "retention", "store", "delete"
]


def filter_relevant_paragraphs(text):
    paragraphs = text.split("\n")
    relevant = []

    for p in paragraphs:
        if any(word in p.lower() for word in KEYWORDS):
            relevant.append(p)

    return "\n".join(relevant)


# ---------------------------
# Ollama Query (Safe + Robust)
# ---------------------------
def query_ollama(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "qwen2.5:3b",  # Faster than 7B
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        data = response.json()

        # Handle Ollama returning error JSON
        if "response" not in data:
            print("Ollama error:", data)
            return {}

        raw_output = data["response"]

        # Extract JSON safely (LLMs sometimes add extra text)
        json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            print("⚠️ No JSON found in:", raw_output)
            return {}

    except Exception as e:
        print("Ollama request failed:", e)
        return {}


# ---------------------------
# Aggregation Logic
# ---------------------------
def aggregate_results(results):
    aggregated = {
        "mentions_biometric_data": False,
        "mentions_location_tracking": False,
        "mentions_camera_or_microphone": False,
        "data_retention_policy_present": False,
        "retention_duration_specified": False,
        "risk_reason": []
    }

    for r in results:
        if not isinstance(r, dict):
            continue

        aggregated["mentions_biometric_data"] |= r.get("mentions_biometric_data", False)
        aggregated["mentions_location_tracking"] |= r.get("mentions_location_tracking", False)
        aggregated["mentions_camera_or_microphone"] |= r.get("mentions_camera_or_microphone", False)
        aggregated["data_retention_policy_present"] |= r.get("data_retention_policy_present", False)
        aggregated["retention_duration_specified"] |= r.get("retention_duration_specified", False)

        if r.get("risk_reason"):
            aggregated["risk_reason"].append(r["risk_reason"])

    aggregated["risk_reason"] = " ".join(aggregated["risk_reason"])

    return aggregated


# ---------------------------
# Chunk Processor (Thread Safe)
# ---------------------------
def process_chunk(chunk):
    try:
        prompt = build_prompt(chunk)
        return query_ollama(prompt)
    except Exception as e:
        print("Chunk failed:", e)
        return {}


# ---------------------------
# Analyze Endpoint
# ---------------------------
@app.post("/analyze")
async def analyze(request: dict):
    text = request.get("text", "")
    if not text:
        return {"error": "No text provided"}

    print("Filtering text...")
    filtered_text = filter_relevant_paragraphs(text)

    if not filtered_text.strip():
        return {
            "analysis": {
                "mentions_biometric_data": False,
                "mentions_location_tracking": False,
                "mentions_camera_or_microphone": False,
                "data_retention_policy_present": False,
                "retention_duration_specified": False,
                "risk_reason": "No relevant clauses found."
            }
        }

    chunks = chunk_text(filtered_text)
    print(f"Processing {len(chunks)} chunks")

    # CPU-safe worker count
    max_workers = min(2, len(chunks))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        all_results = list(executor.map(process_chunk, chunks[:10]))

    final_result = aggregate_results(all_results)

    return {"analysis": final_result}


# ---------------------------
# Test Endpoint
# ---------------------------
@app.post("/test")
async def test():
    return {"status": "ok"}
