from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path
import openai
from dotenv import dotenv_values
from mangum import Mangum


config = dotenv_values(".env")
openai.api_key = config['OPENAI_API_KEY']

app = FastAPI()
handler = Mangum(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Hello, I am here."}
    
@app.get("/check/")
def check_endpoint():
    return {"status": "Endpoint is working!"}

@app.post("/post-message/")
def post_message(text: str):
    return {"message": text}




@app.post("/upload/")
async def upload_mp3(file: UploadFile = UploadFile(...)):

    if not file.filename or not isinstance(file.filename, str):
        raise HTTPException(status_code=400, detail="Invalid or missing filename.")


    # Check if the file is an MP3
    if file.filename.split('.')[-1].lower() != "mp3":
        raise HTTPException(status_code=400, detail="Invalid file format. Only MP3 is accepted.")
    
    # Save the file temporarily
    temp_file = Path("/tmp/" + file.filename)
    with temp_file.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Check file size
    if temp_file.stat().st_size > 25 * 1024 * 1024:  # 25 MB
            temp_file.unlink()  # delete the temp file
            raise HTTPException(status_code=400, detail="File size exceeds 25MB.")

    # Process the file and get details (placeholder for now)
    details = process_mp3(temp_file)

    # Delete the temp file after processing
    temp_file.unlink()

    return PlainTextResponse(details)

def process_mp3(file_path: Path) -> str:
    result = openai.Audio.transcribe(
        model='whisper-1',
        file=open(file_path, 'rb'),
        response_format="srt"
    )   


    return result
