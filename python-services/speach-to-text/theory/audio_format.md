The browser records audio/webm (Chrome) or audio/ogg (Firefox). Never WAV. The original code ignored this entirely.

in svelte:
const mimeType = mediaRecorder.mimeType || 'audio/webm';
const audioBlob = new Blob(audioChunks, { type: mimeType });

const ext = blob.type.includes('ogg') ? '.ogg' : blob.type.includes('mp4') ? '.mp4' : '.webm';
formData.append('file', blob, `recording${ext}`);

in main.py:
suffix = os.path.splitext(file.filename or 'recording.webm')[1] or '.webm'
with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:

