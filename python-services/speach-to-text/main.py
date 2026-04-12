import whisper # Whisper speech-to-text library.

# Load the Whisper model (downloads on first run)
model = whisper.load_model("base")

# Example: transcribe an audio file (replace 'audio.wav' with your file)
# result = model.transcribe("audio.wav")
# print(result["text"])


from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn # ASGI server to run FastAPI.
import tempfile # module to create temporary files.

app = FastAPI()

# curl -X POST -F "file=@python-services/speach-to-text/test.wav" http://localhost:8090/convert_audio
@app.post("/convert_audio") # transcribe audio file to text
async def convert_audio(file: UploadFile = File(...)):
	# Save uploaded file to a temp file
	with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
		tmp.write(await file.read())
		tmp_path = tmp.name
	# Transcribe
	result = model.transcribe(tmp_path)
	return JSONResponse({"text": result["text"]})

if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=False)
