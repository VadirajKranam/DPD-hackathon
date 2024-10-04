import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
from vosk import Model, KaldiRecognizer
import json
import wave
import os
from indicnlp.tokenize import sentence_tokenize
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
from googletrans import Translator

class CallEvaluator:
    def __init__(self, stt_model_path, qa_model_name):
        self.stt_model = self.setup_stt(stt_model_path)
        self.qa_pipeline = self.setup_qa_pipeline(qa_model_name)
        self.normalizer = IndicNormalizerFactory().get_normalizer("kn")
        self.translator = Translator()

    @staticmethod
    def setup_stt(model_path):
        return Model(model_path)

    @staticmethod
    def setup_qa_pipeline(model_name):
        return pipeline("question-answering", model=model_name, tokenizer=model_name)

    def transcribe_audio(self, audio_file):
        file_extension = os.path.splitext(audio_file)[1].lower()
        
        if file_extension == '.wav':
            return self.transcribe_wav(audio_file)
        elif file_extension == '.mp3':
            return self.transcribe_mp3(audio_file)
        else:
            raise ValueError("Unsupported file format. Please use WAV or MP3.")

    def transcribe_wav(self, audio_file):
        with wave.open(audio_file, "rb") as wf:
            rec = KaldiRecognizer(self.stt_model, wf.getframerate())
            transcription = []
            
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    transcription.append(result['text'])
        
        return ' '.join(transcription)

    def transcribe_mp3(self, audio_file):
        print(f"Warning: MP3 transcription is not fully implemented. File: {audio_file}")
        return "MP3 transcription placeholder"

    def preprocess_text(self, text):
        normalized_text = self.normalizer.normalize(text)
        sentences = sentence_tokenize.sentence_split(normalized_text, lang='kn')
        return ' '.join(sentences)

    def translate_to_english(self, text):
        return self.translator.translate(text, src='kn', dest='en').text

    def translate_to_kannada(self, text):
        return self.translator.translate(text, src='en', dest='kn').text

    def answer_questions(self, context, questions):
        answers = {}
        english_context = self.translate_to_english(context)
        
        for question in questions:
            qa_result = self.qa_pipeline(question=question, context=english_context)
            
            # Convert to binary answer based on confidence score
            binary_answer = "Yes" if qa_result['score'] >= 0.4 else "No"
            
            kannada_answer = self.translate_to_kannada(binary_answer)
            
            answers[question] = {
                'kannada_answer': kannada_answer,
                'english_answer': binary_answer,
                'confidence': qa_result['score']
            }
        return answers

    def evaluate_call(self, audio_file, questions):
        transcription = self.transcribe_audio(audio_file)
        cleaned_text = self.preprocess_text(transcription)
        answers = self.answer_questions(cleaned_text, questions)
        
        return {
            "transcription": transcription,
            "answers": answers
        }

def main():
    stt_model_path = r"/Users/vadirajkaranam/Downloads/vosk-model-en-in-0.5"  # Replace with the path to the Kannada Vosk model
    qa_model_name = "distilbert-base-cased-distilled-squad"  # English QA model
    audio_file = "/Users/vadirajkaranam/Downloads/e63aaadf-0e96-49e6-aa21-79a4c4ca2b25.mp3"  # Can be either MP3 or WAV
    
    questions = [
        "Did the advisor open the call professionally?",
        "Did the advisor follow the proper identification process?",
        "Did the advisor clearly state the purpose of the call?",
        "Did the advisor ask relevant fact-finding questions?",
        "Did the advisor effectively use historical notes or system information?",
        "Was the borrower's name correctly identified and used?"
    ]
    
    evaluator = CallEvaluator(stt_model_path, qa_model_name)
    result = evaluator.evaluate_call(audio_file, questions)
    
    print("Transcription (Kannada):", result["transcription"])
    print("\nTranslated Transcription (English):", evaluator.translate_to_english(result["transcription"]))
    print("\nAnswers to questions:")
    for question, answer in result["answers"].items():
        print(f"Q: {question}")
        print(f"A (English): {answer['english_answer']}")
        print(f"A (Kannada): {answer['kannada_answer']}")
        print(f"Confidence: {answer['confidence']:.2f}")
        print()

if __name__ == "__main__":
    main()