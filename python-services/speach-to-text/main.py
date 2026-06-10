# import whisper
from faster_whisper import WhisperModel # A library wrapping OpenAI's Whisper AI model for speech-to-text
import uvicorn # An ASGI (Asynchronous Server Gateway Interface) web server — equivalent to Node's http module or Go's net/http server. It's what actually listens on a port and handles HTTP connections. You run uvicorn.run(app) like http.ListenAndServe(...) in Go
import tempfile # Standard library for creating temporary files/directories, same concept as tmpfile() in C or File.createTempFile() in Java. You use it when you need scratch space on disk that gets cleaned up automatically.
import os
from fastapi import FastAPI, File, UploadFile # FastAPI is a web framework like Express.js (Node) or Gin (Go). FastAPI is the app instance, File and UploadFile are types for handling multipart file uploads in route handlers.
from fastapi.responses import JSONResponse # lets you return a JSON HTTP response explicitly — like res.json({...}) in Express or json.NewEncoder(w).Encode(...) in Go.
from fastapi.middleware.cors import CORSMiddleware # Middleware that adds CORS headers to responses, so a browser frontend on a different origin can call this API. Same concept as CORS middleware in Express (cors npm package)

app = FastAPI() # calls the constructor

# --- CORS (Cross-Origin Resource Sharing) ---
# Browsers block "cross-origin" requests by default for security.
# STT is only reachable via the SvelteKit proxy (src/routes/stt/convert_audio/+server.ts),
# which checks auth before forwarding here — CORS is a secondary safety net.
# For production replace with your real domain, e.g.:
#   allow_origins=["https://42overflow.com", "https://www.42overflow.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True, # you are allowed to send cookies and auth headers cross-origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- THEORY: Whisper Model Loading ---
# 'base' is a good balance between speed and accuracy. 
# On the first run, this script will download about 140MB of model weights.
# It stays in RAM once loaded so transcription is faster.
#model = WhisperModel("base", device="cpu", compute_type="int8")
model = WhisperModel("small", device="cpu", compute_type="int8")

# --- FUNCTION: convert_audio ---
# This is an "Asynchronous Endpoint." It handles the file upload from the browser.
# 1. It receives the raw bytes of the audio file.
# 2. It saves them to a temporary file (Whisper needs a file path, not a raw stream).
# 3. It transcribes the audio using the CPU/GPU.
# 4. It returns the text as a JSON object.
@app.post("/convert_audio") # The @ is a decorator — Python's way of wrapping a function with extra behavior. This one registers the next function as the handler for POST /convert_audio; Equivalent in Go Gin: app.POST("/convert_audio", convertAudio)
async def convert_audio(file: UploadFile = File(...)): # coroutine function (like async function in JS); While waiting, the server isn't blocked and can serve other requests
    # Create a temporary file that won't be deleted automatically until we are done
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:  # like Java's try-with-resources
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            return JSONResponse({"error": "file too large"}, status_code=413)

        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Whisper.transcribe automatically uses ffmpeg to 
        # convert whatever the browser sent into a format it understands.
        # Adding 'fp16=False' ensures it works smoothly on CPUs.

        # faster-whisper: returns (segments_generator, info) instead of a dict
        segments, _ = model.transcribe(tmp_path, language="en")
        text = " ".join(segment.text for segment in segments).strip() # for segment in segments = a generator expression (lazy loop), like a stream in Java. Iterates over each segment object; .strip() = trims whitespace from both ends. Like .trim() in Java/JS.
        return JSONResponse({"text": text})
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    
    finally:
        # --- THEORY: Cleanup ---
        # We must manually delete the temp file after transcription to prevent 
        # filling up the server's hard drive with old audio recordings.
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

# --- FUNCTION: Main Entry Point ---
# This starts the Uvicorn server.
# host "0.0.0.0" means it listens on all network interfaces (important for Docker).
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8091, reload=False)