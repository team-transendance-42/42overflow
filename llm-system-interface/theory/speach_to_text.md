Speech capture in the browser.
Transcription to plain text.
Optional cleanup by Gemini or Gemma 3.
Submit through the existing AI-assist form in +page.svelte.
=============================
The fastest implementation is the Web Speech API, specifically SpeechRecognition. Add a mic button next to the text box, start recognition on click, and on each result append the transcript into the question field. Keep a small state machine: isListening, recognition instance, and interim transcript. If the browser supports it, this gives you near-instant dictate behavior with no server changes. If it does not support it, show a fallback message like “Voice input not supported in this browser.”
==============================

If you want better reliability or longer audio, use server-side transcription instead. The client records audio with MediaRecorder, sends it to a new SvelteKit API route, and that route transcribes it using Gemini’s audio input. After that, you can optionally send the raw transcript to Gemma 3 for cleanup, punctuation, or formatting before inserting it into the prompt box. That is the route to take if you want accuracy over simplicity.
===============================
plan
===============================
Add a microphone toggle beside the prompt input in +page.svelte.
Use SpeechRecognition first for instant dictation.
On result, write the transcript into the existing question state.
Keep the current Ask button unchanged.
Only add server transcription later if you need cross-browser support or better accuracy.
===============================
todo:
for stronger version next, add server-side transcription with MediaRecorder and a new SvelteKit route that sends audio to Gemini, then optionally cleans the transcript with Gemma 3.
================================
compare: Browser speech recognition in Chrome/Brave
Server-side transcription with Gemini after recording audio in the browser
================================
Chrome vs Brave

Chrome: best chance of working smoothly with SpeechRecognition, generally the least friction, usually the most reliable for dictation.
Brave: often works because it is Chromium-based, but privacy protections and shield settings can make behavior less predictable. It may still work well, but you should expect more “it depends on the user’s settings” cases.
================================

Option 1: Browser dictation
Pros:

Fastest to implement.
No new backend route.
Very low latency because text appears immediately.
Cheap, because you are not sending audio to your server or an API.
Cons:

Quality is browser-dependent.
Chrome is usually better than Brave here.
Brave may be affected by shield/privacy settings, microphone permissions, or blocked network behavior.
Less control over punctuation, formatting, and multilingual accuracy.
Not as good for noisy environments or long dictation.

Best when:

You want the easiest possible feature.
You want quick “talk and type” behavior.
You mainly support desktop Chrome.
=============================

Option 2: Gemini transcription
Pros:

Better transcription quality in general.
Better punctuation and sentence structure.
More consistent across Chrome, Brave, Firefox-like fallback flows, and mobile browsers, because the browser only records audio.
Easier to extend later with cleanup, summarization, or formatting.
Better for noisy audio and longer dictations.

ons:

More work.
Needs a backend API route.
Higher latency because you must record, upload, transcribe, then insert the text.
Costs API usage.
You must handle audio upload, file size, error cases, and maybe storage limits.
Best when:

You care about accuracy.
You want a browser-agnostic solution.
You expect Brave users or privacy-conscious users.
You want a robust production feature.
Practical recommendation

For Chrome and Brave, use browser dictation as the first version if you want maximum simplicity.
If you want a real production dictation feature, use Gemini transcription.
If you want both, implement browser dictation as the quick path and keep Gemini transcription as the fallback when SpeechRecognition is unavailable or flaky.
=============================
Gemma 3 and Gemini solve different jobs.

Gemma 3 is a text model. It can take text and improve it, summarize it, or answer questions. It is not, by itself, a speech-to-text engine for raw microphone audio. If your backend receives audio bytes, it still needs a transcription model or service first.
Gemini is a family of models that includes both text and audio capabilities. The audio models can take raw microphone input and transcribe it into text. So if you want to do server-side transcription, you would use Gemini's audio model to convert the recorded audio into text. After that, you could optionally send the raw transcript to Gemma 3 for cleanup, punctuation, or formatting before inserting it into the prompt box.




