
  - Browser records audio via MediaRecorder → sends as multipart form to
  /api/stt
  - SvelteKit proxy (auth-gated, secret-protected) forwards to Python
  python-stt:8091
  - Whisper small model transcribes on CPU → returns JSON text
  - Frontend inserts transcript into the prompt box

  That's a functional, self-hosted, server-side dictation feature.
---------------------------------------
whisper models
---------------------------------------
Model            | Size   | VRAM (GPU) | RAM (CPU) | Speed    | Accuracy
-----------------|--------|------------|-----------|----------|------------------
tiny             | 39MB   | ~1GB       | ~1GB      | ~32x     | lowest
base             | 74MB   | ~1GB       | ~1GB      | ~16x     | low
small            | 244MB  | ~2GB       | ~2GB      | ~6x      | good
medium           | 769MB  | ~5GB       | ~5GB      | ~2x      | very good
large-v2         | 1.5GB  | ~10GB      | ~10GB     | 1x       | best
large-v3         | 1.5GB  | ~10GB      | ~10GB     | 1x       | best (newer)
distil-large-v3  | 756MB  | ~4GB       | ~4GB      | ~6x      | near-large quality

to chose one:
free -h
can try small or medium: depending if my laptop or campus computers
---------------------------------------
Backend in detail (main.py)
---------------------------------------
Model loading (once at startup):

model = WhisperModel("base", device="cpu", compute_type="int8")
"base" — ~140MB model, good balance of speed/accuracy
device="cpu" — runs on CPU, not GPU (GPU is reserved for Ollama/gemma4)
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