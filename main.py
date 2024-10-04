import json

from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
from typing import List
import shutil
import os
from tempfile import NamedTemporaryFile
from utils import CallEvaluator  # Assuming the previous code is in call_evaluator.py
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://yourdomain.com"],  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class Question(BaseModel):
    text: str

class EvaluationResult(BaseModel):
    transcription: str
    answers: dict

# Initialize the CallEvaluator
stt_model_path = r"/Users/vadirajkaranam/Downloads/vosk-model-en-in-0.5"
qa_model_name = "distilbert-base-cased-distilled-squad"
evaluator = CallEvaluator(stt_model_path, qa_model_name)


@app.get("/")
def send_resp():
    print("Hellow")
    return "Hello"
@app.post("/evaluate-call/", response_model=EvaluationResult)
async def evaluate_call(file: UploadFile = File(...), questions: str = Form(...)):
    # Save the uploaded file temporarily
    try:
        questions_list = json.loads(questions)  # Convert from JSON string to list
        questions = [Question(**question) for question in questions_list]
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format for questions"}
    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    try:
        # Extract questions from the form data
        question_texts = [q.text for q in questions]

        # Process the file and get results
        result = evaluator.evaluate_call(temp_file_path, question_texts)

        return EvaluationResult(
            transcription=result["transcription"],
            answers=result["answers"]
        )
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)