import os
import uuid
import json
from typing import List, Dict
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

from cerebras.cloud.sdk import Cerebras, AuthenticationError
from config import Settings

# --- 1. Cerebras Client and FastAPI App Initialization ---
try:
    settings = Settings()
    client = Cerebras(api_key=settings.CEREBRAS_API_KEY)
    print("Testing connection to Cerebras API on startup...")
    client.chat.completions.create(model="llama-3.3-70b", messages=[{"role":"user", "content":"test"}], max_completion_tokens=2)
    print("Cerebras client initialized successfully.")
except AuthenticationError as e:
    print(f"FATAL: AuthenticationError. Your API Key is invalid. Error: {e}")
    client = None
except Exception as e:
    print(f"FATAL: Failed to initialize Cerebras client. Server cannot start. Error: {e}")
    client = None

app = FastAPI(
    title="Smart Doc Checker Agent",
    description="API for finding contradictions in documents.",
    version="1.0.0",
)

# --- 2. In-Memory Storage ---
uploaded_files: Dict[str, str] = {}
analysis_reports: Dict[str, 'AnalysisReport'] = {}
usage_counter = {"docs_checked": 0, "reports_generated": 0}

# --- 3. Define Structured Output Models ---
class Contradiction(BaseModel):
    document_1: str = Field(description="The filename of the first document with conflicting text.")
    document_2: str = Field(description="The filename of the second document with conflicting text.")
    conflicting_text_1: str = Field(description="The specific text from the first document.")
    conflicting_text_2: str = Field(description="The specific text from the second document.")
    explanation: str = Field(description="A clear explanation of why these texts are contradictory.")
    suggestion: str = Field(description="A suggested clarification to resolve the conflict.")

class AnalysisReport(BaseModel):
    summary: str = Field(description="A brief summary of the findings.")
    contradictions: List[Contradiction] = Field(description="A list of all contradictions found.")

# --- 4. Mock Flexprice Integration ---
def mock_bill_per_document(doc_count: int):
    print(f"FLEXPRICE_BILLING: Billed for {doc_count} documents.")
    usage_counter["docs_checked"] += doc_count
    return True

def mock_bill_per_report():
    print("FLEXPRICE_BILLING: Billed for 1 report generated.")
    usage_counter["reports_generated"] += 1
    return True

# --- 5. Core AI Logic (Updated with JSON Cleaning) ---
async def analyze_documents_for_contradictions(file_contents: Dict[str, str]) -> AnalysisReport:
    if not client:
        raise HTTPException(status_code=503, detail="AI service is not available due to initialization failure.")

    context = ""
    for filename, content in file_contents.items():
        context += f"--- DOCUMENT: {filename} ---\n{content}\n\n"

    json_schema = AnalysisReport.model_json_schema()
    prompt = f"""
    You are a meticulous Smart Doc Checker Agent. Your task is to analyze the following documents and identify all contradictions.
    Carefully compare the rules, policies, dates, numbers, and instructions across all provided documents.

    Here are the documents:
    {context}

    Based on your analysis, you MUST respond with ONLY a valid JSON object that conforms to the following JSON Schema. Do not include any other text, greetings, or explanations outside of the JSON structure.

    JSON Schema:
    {json.dumps(json_schema, indent=2)}
    """

    try:
        print("Sending analysis request to Cerebras API...")
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b",
            max_completion_tokens=4096,
            temperature=0.1
        )
        response_text = response.choices[0].message.content
        print("Received response from API.")

        # --- NEW: JSON CLEANING LOGIC ---
        # Find the first '{' and the last '}' to extract the JSON object
        # This handles cases where the AI wraps the JSON in backticks or other text.
        start_index = response_text.find('{')
        end_index = response_text.rfind('}')
        if start_index != -1 and end_index != -1:
            clean_json_text = response_text[start_index : end_index + 1]
        else:
            clean_json_text = response_text # Fallback if no braces are found
        
        print("Attempting to parse cleaned JSON...")
        report_data = json.loads(clean_json_text)
        report = AnalysisReport(**report_data)
        return report

    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from AI response. Details: {e}")
        # Log the raw and cleaned text for debugging
        print(f"Raw AI Response was: {response_text}")
        print(f"Cleaned Text was: {clean_json_text}")
        raise HTTPException(status_code=500, detail="AI returned an invalid JSON format.")
    except Exception as e:
        print(f"Error during AI execution: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the AI response: {e}")


# --- 6. API Endpoints (Unchanged) ---
@app.get("/")
def read_root():
    return {"status": "Smart Doc Checker API is running!"}

@app.post("/api/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    global uploaded_files
    uploaded_files.clear()
    if not (2 <= len(files) <= 3):
        raise HTTPException(status_code=400, detail="Please upload 2 or 3 documents.")
    for file in files:
        contents = await file.read()
        uploaded_files[file.filename] = contents.decode('utf-8')
    mock_bill_per_document(len(files))
    return {"message": "Upload successful.", "filenames": list(uploaded_files.keys()), "usage": usage_counter}

@app.post("/api/analyze", response_model=AnalysisReport)
async def analyze_uploaded_documents():
    if not uploaded_files:
        raise HTTPException(status_code=400, detail="No documents uploaded.")
    mock_bill_per_report()
    report = await analyze_documents_for_contradictions(uploaded_files)
    report_id = str(uuid.uuid4())
    analysis_reports[report_id] = report
    return report

@app.get("/api/usage")
def get_usage_stats():
    return usage_counter

@app.post("/api/webhook/notify-update")
async def pathway_update_webhook(data: Dict):
    print(f"Received update from Pathway: {data}")
    return {"status": "Webhook received."}

