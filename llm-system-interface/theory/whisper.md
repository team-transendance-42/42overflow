tep 1 — get mic access:


const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
Browser asks user permission. Returns a MediaStream object (raw mic data).

Step 2 — record:


mediaRecorder = new MediaRecorder(stream);
mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
mediaRecorder.start();
MediaRecorder collects audio into chunks. Every time data is available, it's pushed to audioChunks[].

Step 3 — stop and send:


mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    await sendToWhisper(audioBlob);         // transcribe
    stream.getTracks().forEach(t => t.stop()); // release mic
    await askQuestion();                    // send to LLM
};
When stopped: all chunks merged into one Blob, sent to Whisper, mic released, then question asked automatically.

Step 4 — HTTP to Whisper:


const formData = new FormData();
formData.append('file', blob, 'recording.wav');
fetch('http://localhost:8091/convert_audio', { method: 'POST', body: formData });
FormData is a browser API for sending files over HTTP (like an HTML form upload).

Backend in detail (main.py)
Model loading (once at startup):


model = WhisperModel("base", device="cpu", compute_type="int8")
"base" — ~140MB model, good balance of speed/accuracy
device="cpu" — runs on CPU, not GPU (GPU is reserved for Ollama/gemma3)
compute_type="int8" — 8-bit quantization: smaller, faster, slight quality loss
Model stays in RAM after first load — no reload cost per request.

Per request:


with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
    tmp.write(content)  # save blob to disk
Whisper needs a file path, not raw bytes — so the audio must be saved to disk first.


segments, _ = model.transcribe(tmp_path, language="en")
text = " ".join(segment.text for segment in segments).strip()
transcribe() returns a generator of segments (sentences/phrases). You join them all into one string.


finally:
    os.remove(tmp_path)  # always clean up
Temp file deleted even if transcription crashes.

Why faster-whisper instead of openai-whisper
openai-whisper	faster-whisper
Backend	PyTorch	CTranslate2
Speed	baseline	~4x faster
Memory	higher	lower (int8)
Output	result["text"]	segments generator
Same model weights, different inference engine. Better for CPU.

Port layout

:5173  — Svelte frontend
:8081  — Go LLM server (Ollama proxy)
:8091  — Python Whisper server
Whisper runs completely independently from the Go server — it's its own microservice.