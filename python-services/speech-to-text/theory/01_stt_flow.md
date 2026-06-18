
  1. User clicks mic button (src/routes/ai-assist/+page.svelte)
  - navigator.mediaDevices.getUserMedia({ audio: true }) — asks for mic
  permission
  - MediaRecorder starts, pushes chunks into audioChunks[]

  2. User stops recording
  - Chunks merged into a Blob (audio/wav)
  - sendToWhisper(blob) builds a FormData with file = recording.wav
  - fetch('/api/stt', { method: 'POST', body: formData })

  3. SvelteKit proxy (src/routes/api/stt/+server.ts)
  - Checks locals.user — rejects 401 if not logged in
  - Re-parses FormData (avoids Node.js stream forwarding bug)
  - Forwards to http://python-stt:8091/convert_audio with
  X-Internal-Secret and X-User-ID headers

  4. Python Whisper service (python-services/speech-to-text/main.py)
  - Receives file, rejects if > 10 MB
  - Saves to a temp .wav file
  - model.transcribe(tmp_path, language="en") — faster-whisper small
  model on CPU
  - Joins segments → returns { "text": "..." }
  - Deletes temp file in finally

  5. Back in the browser
  - Response JSON parsed, transcript inserted into the question input
  field
  - User edits if needed, then hits Ask