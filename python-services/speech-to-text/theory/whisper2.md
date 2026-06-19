roughly whisper models: base and small diff:
============================================
base — fine for clear speech, single speaker, English, quiet background. Struggles with accents, fast speech, technical terms.
small — handles accents better, more robust to noise, better with uncommon vocabulary and non-native speakers.
============================================

python main.py
    │
    ├── loads Whisper model into RAM
    ├── creates FastAPI app with CORS middleware
    └── starts uvicorn on port 8091
              │
              └── incoming POST /convert_audio
                        │
                        ├── reads audio bytes from request
                        ├── writes to temp .wav file
                        ├── runs Whisper transcription (CPU)
                        ├── joins text segments
                        ├── deletes temp file
                        └── returns {"text": "..."} as JSON

===============================================

allow_credentials=True tells the browser: "you are allowed to send cookies and auth headers cross-origin."

What it controls
By default, browsers strip credentials from cross-origin requests for security. This flag lifts that restriction.

"Credentials" means any of these:

Cookies (session tokens, JWT in a cookie)
Authorization headers (Authorization: Bearer <token>)
TLS client certificates
===============================================
TODO:
When allow_credentials=True, you cannot use allow_origins=["*"]. The browser will refuse it as a security violation. You must list exact origins:

# This will BREAK with allow_credentials=True
allow_origins=["*"]

# This is correct — explicit origins only
allow_origins=["http://localhost:5173"]
todo in prod: allow_origins=["http://localhost:5173", "https://ourdomain.com"]
