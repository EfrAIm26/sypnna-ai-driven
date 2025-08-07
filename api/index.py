import os
import tempfile
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import yt_dlp
from moviepy.editor import *
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("/api/generate")
async def generate_from_video(request: VideoRequest):
    temp_audio_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            temp_audio_path = temp_audio.name
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': temp_audio_path,
            'noplaylist': True,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([request.url])

        with open(temp_audio_path, "rb") as audio_file:
            transcript_response = openai.Audio.transcribe(model="openai/whisper-1", file=audio_file)
        
        transcription = transcript_response['text']
        return {"transcription": transcription}
    except Exception as e:
        print(f"!!!!!!!!!!!!!! ERROR EN EL BACKEND !!!!!!!!!!!!!!\nERROR: {e}")
        raise HTTPException(status_code=500, detail="Error processing video")
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)