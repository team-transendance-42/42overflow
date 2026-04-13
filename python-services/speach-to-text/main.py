import whisper
import uvicorn
import tempfile
import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- THEORY: CORS (Cross-Origin Resource Sharing) ---
# Browsers block "cross-origin" requests by default for security. 
# Since your frontend (port 5173) is different from this backend (port 8090),
# the browser will block the 'fetch' call unless this middleware explicitly 
# tells the browser "I trust this origin."
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins. For production, use ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"], # Allows POST, GET, etc.
    allow_headers=["*"], # Allows all custom headers
)

# --- THEORY: Whisper Model Loading ---
# 'base' is a good balance between speed and accuracy. 
# On the first run, this script will download about 140MB of model weights.
# It stays in RAM once loaded so transcription is faster.
model = whisper.load_model("base")

# --- FUNCTION: convert_audio ---
# This is an "Asynchronous Endpoint." It handles the file upload from the browser.
# 1. It receives the raw bytes of the audio file.
# 2. It saves them to a temporary file (Whisper needs a file path, not a raw stream).
# 3. It transcribes the audio using the CPU/GPU.
# 4. It returns the text as a JSON object.
@app.post("/convert_audio")
async def convert_audio(file: UploadFile = File(...)):
    # Create a temporary file that won't be deleted automatically until we are done
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # THEORY: Whisper.transcribe automatically uses ffmpeg to 
        # convert whatever the browser sent into a format it understands.
        # Adding 'fp16=False' ensures it works smoothly on CPUs.
        result = model.transcribe(tmp_path, fp16=False, language="en") 
		# result = model.transcribe(
		# 	tmp_path, 
		# 	fp16=False, 
		# 	language="en",
		# 	temperature=0,      # Makes the output less "creative" and more literal
		# 	no_speech_threshold=0.6 # Ignores chunks that are likely just background hiss
		# )
        return JSONResponse({"text": result["text"].strip()})
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    
    finally:
        # --- THEORY: Cleanup ---
        # We must manually delete the temp file after transcription to prevent 
        # filling up the server's hard drive with old audio recordings.
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- FUNCTION: Main Entry Point ---
# This starts the Uvicorn server.
# host "0.0.0.0" means it listens on all network interfaces (important for Docker).
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=False)

@app.get("/healthz")
async def health_check():
    # This tells Docker (and the other machines) that Whisper is ready
    return {"status": "ok"}