
  What problem it solves

  The current path requires: mic → upload to SvelteKit → forward to
  Python container → Whisper transcribes → return text. If any of these
  break (server down, container not running, network hiccup at Codam,
  mic buffer too small) the user gets an empty error or silence.

  SpeechRecognition is a browser-native API (built into
  Chrome/Brave/Edge — the Chromium family) that does transcription
  locally in the browser, with no server. It gives interim results as
  you speak, so text appears live. It's what Google uses for voice
  search.