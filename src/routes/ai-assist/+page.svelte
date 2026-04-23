<style>
    .container {
        --olive-text: #F4FFE8;
        --light-olive: #a8bc84;
        --panel-bg: #1b231b;
        --panel-border: rgba(244, 255, 232, 0.12);
        --soft-shadow: 0 0 10px var(--olive-text);
        --focus-glow: rgba(168, 188, 132, 0.22);
        --button-bg: #152015;
        --button-color: var(--olive-text);
        --button-border: rgba(244, 255, 232, 0.18);
        --dark-olive: rgba(168, 188, 132, 0.6);
        --button-radius: 14px;
        --button-disabled-opacity: 0.55;
        color: var(--olive-text);
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
    }

    h2,
    .info {
        color: var(--olive-text);
        text-shadow: var(--soft-shadow);
        text-align: center;
    }

    .info {
        margin: 1rem 0;
    }

    .answer-card {
        width: 100%;
        display: block;
        margin: 20px auto;
        max-width: 780px;
        background: var(--panel-bg);
        border: 1px solid var(--panel-border);
        padding: 1.25rem;
        text-align: left;
        line-height: 1.6;
        overflow-x: auto;
    }

	.answer-card, .form-input, .form-input-parent button, .toggle-button, .answer-card :global(pre) {
		border-radius: var(--button-radius);
		color: var(--olive-text);
	}

    .form-input-parent {
        width: 100%;
        max-width: 780px;
        margin: 20px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        padding: 0 1rem;
        box-sizing: border-box;
    }

    .form-input {
        flex: 1 1 auto;
        min-width: 0;
        display: block;
        background: var(--panel-bg);
        border: 1px solid var(--panel-border);
        padding: 1.25rem;
        color: var(--olive-text);
        line-height: 1.6;
        box-sizing: border-box;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .form-input:focus,
    .form-input:focus-visible {
        outline: none;
        border-color: var(--olive-text);
        box-shadow: 0 0 0 3px var(--focus-glow);
    }

    .form-input-parent button {
        flex: 0 0 auto;
        border: 1px solid var(--button-border);
        background: var(--button-bg);
        /*color: var(--button-color);*/
        padding: 1.25rem 1.5rem;
        cursor: pointer;
        white-space: nowrap;
        transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
    }

    .parent-llms {
        display: flex;
        gap: 1rem;
        justify-content: center;
    }

    .toggle-button {
        flex: 0 0 auto;
        border: 1px solid var(--panel-border);
        background: var(--button-bg);
        /*color: var(--light-olive);*/
        padding: 0.75rem 1.5rem;
        margin-top: 1rem;
        cursor: pointer;
        white-space: nowrap;
        font-size: 0.9em;
        transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
    }

    .toggle-button.active {
        color: white;
        border-color: white;
    }

    .form-input-parent button:disabled,
    .toggle-button:disabled {
        cursor: not-allowed;
        opacity: var(--button-disabled-opacity);
    }

    .answer-card :global(h1),
    .answer-card :global(h2),
    .answer-card :global(h3) {
        margin: 1rem 0 0.5rem;
        line-height: 1.2;
        color: var(--olive-text);
    }

    .answer-card :global(ul),
    .answer-card :global(ol) {
        margin: 0.75rem 0 0.75rem 1.25rem;
        padding-left: 1rem;
    }

    .answer-card :global(li) {
        margin: 0.35rem 0;
    }

    .answer-card :global(pre) {
        margin: 1rem 0;
        padding: 1rem;
        background: var(--button-bg);
        color: var(--olive-text);
        overflow-x: auto;
        white-space: pre;
    }

    .answer-card :global(code) {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.95em;
    }

    .answer-card :global(pre code) {
        padding: 0;
        background: transparent;
    }

    .answer-card :global(:not(pre) > code) {
        padding: 0.15rem 0.35rem;
        border-radius: 0.35rem;
        background: var(--dark-olive);
    }

    .answer-card :global(blockquote) {
        margin: 0.75rem 0;
        padding-left: 1rem;
        border-left: 3px solid var(--dark-olive);
    }

    .answer-card :global(a) {
        color: var(--light-olive);
    }

    .answer-card :global(hr) {
        border: 0;
        border-top: 1px solid var(--panel-border);
        margin: 1rem 0;
    }
</style>

<script lang="ts">
    // STATE
    let question = $state('');
    let answer = $state('');
    let loading = $state(false);
    let error = $state('');
    let activeStreamController = $state<AbortController | null>(null); //Each AbortController is created per-request and linked to exactly one fetch via its .signal
    let llmMode = $state<'gemini' | 'ollama'>('gemini');
    let history = $state<{ question: string; blocks: AnswerBlock[] }[]>([]);
    let dictating = $state(false);
    let mediaRecorder = $state<MediaRecorder | null>(null);
    let audioChunks: Blob[] = []; // Array of audio chunks for dictation

    // TYPES
    type InlineToken =
        | { type: 'text'; value: string }
        | { type: 'strong'; value: string }
        | { type: 'em'; value: string } // emphasize, like bold
        | { type: 'code'; value: string }
        | { type: 'link'; value: string; href: string };

    type AnswerBlock =
        | { type: 'paragraph'; tokens: InlineToken[] }
        | { type: 'heading'; level: 1 | 2 | 3; tokens: InlineToken[] }
        | { type: 'list'; ordered: boolean; items: InlineToken[][] }
        | { type: 'code'; lang: string; code: string };

    function createTextToken(value: string): InlineToken {
        return { type: 'text', value: value.replaceAll('**', '').replaceAll('`', '') };
    }


    /**
     * Parses inline markdown-like tokens from a string.
    *  1. `([^`]+)`         → Group 1: Inline code (text between backticks)
     *  2. **([^*]+)**       → Group 2: Bold (text between double asterisks)
     *  3. __([^_]+)__       → Group 3: Bold (text between double underscores)
     *  4. *([^*]+)*        → Group 4: Emphasis/italic (text between single asterisks)
     *  5. _([^_]+)_        → Group 5: Emphasis/italic (text between single underscores)
     *  6. [(.+?)]((.+?))   → Group 6: Link text, Group 7: Link URL (markdown links)
     *
     * Only one group will be filled per match, depending on which pattern matched.
     * The function uses these groups to create the correct InlineToken type for each match.
	 * the LLM responses come back as raw markdown text 
     */
    function parseInlineTokens(text: string): InlineToken[] {
        const tokens: InlineToken[] = [];
        // Pattern matches: code, bold, italic, and links (markdown style)
        const pattern = /`([^`]+)`|\*\*([^*]+)\*\*|__([^_]+)__|\*([^*]+)\*|_([^_]+)_|\[(.+?)\]\((.+?)\)/g;
        let lastIndex = 0;

        for (const match of text.matchAll(pattern)) { // arr of captured groups
            const index = match.index ?? 0;
            if (index > lastIndex) tokens.push(createTextToken(text.slice(lastIndex, index)));
            if (match[1]) tokens.push({ type: 'code', value: match[1] });
            else if (match[2] || match[3]) tokens.push({ type: 'strong', value: match[2] || match[3] });
            else if (match[4] || match[5]) tokens.push({ type: 'em', value: match[4] || match[5] });
            else if (match[6] && match[7]) tokens.push({ type: 'link', value: match[6], href: match[7] });
            lastIndex = index + match[0].length;
        }

        if (lastIndex < text.length) tokens.push(createTextToken(text.slice(lastIndex)));
        return tokens;
    }

    type ParserState = {
        blocks: AnswerBlock[];
        paragraph: string[];
        listItems: string[];
        listType: 'ul' | 'ol' | null;
        codeLines: string[];
        codeLang: string;
        inCodeBlock: boolean;
    };

    function initParserState(): ParserState {
        return {
            blocks: [],
            paragraph: [],
            listItems: [],
            listType: null,
            codeLines: [],
            codeLang: '',
            inCodeBlock: false
        };
    }

    /**
	 * takes the text, formats and stores in ParserState.AsnwerBlock[]
     *finalizes and stores the current block (paragraph, list, or code) and resets the relevant buffers in the parser state
     */
    function flushBlock(state: ParserState, type: 'paragraph' | 'list' | 'code') {
        if (type === 'paragraph') {
            if (!state.paragraph.length) return;
            state.blocks.push({
                type: 'paragraph',
                tokens: parseInlineTokens(state.paragraph.join(' ').replace(/\s+/g, ' ').trim()) //\s any whitespace char, +=1 or more
            });
            state.paragraph = [];
        } else if (type === 'list') {
            if (!state.listItems.length || !state.listType) return;
            state.blocks.push({
                type: 'list',
                ordered: state.listType === 'ol',
                items: state.listItems.map((item) => parseInlineTokens(item))
            });
            state.listItems = [];
            state.listType = null;
        } else if (type === 'code') {
            state.blocks.push({
                type: 'code',
                lang: state.codeLang.replace(/[^a-z0-9_-]/gi, ''),
                code: state.codeLines.join('\n')
            });
            state.codeLines = [];
            state.codeLang = '';
        }
    }

	/**
	 * Called for every line. If inside a code block: collects lines until closing ```, then flushes.
	 * Returns true if the line was consumed (we're in a code block), false to let handleRegularLine process it.
	 */
    function handleCodeState(line: string, trimmed: string, state: ParserState): boolean {
        if (!state.inCodeBlock) return false;
        if (trimmed.startsWith('```')) { // ``` marks end ond fo a code block
            state.inCodeBlock = false;
            flushBlock(state, 'code');
        } else {
            state.codeLines.push(line); // keep collecting code lines
        }
        return true;
    }

	/**
	 * Processes one non-code line and decides what kind of markdown block it belongs to
	 */
    function handleRegularLine(trimmed: string, state: ParserState) {
        if (trimmed.startsWith('```')) {
            flushBlock(state, 'paragraph'); // if we start a code block, flush p and li
            flushBlock(state, 'list');
            state.inCodeBlock = true;
            state.codeLang = trimmed.slice(3).trim();
            return;
        }

        if (!trimmed) {
            flushBlock(state, 'paragraph');
            flushBlock(state, 'list');
            return;
        }

        const headingMatch = trimmed.match(/^(#{1,3})\s+(.+)$/);
        if (headingMatch) {
            flushBlock(state, 'paragraph');
            flushBlock(state, 'list');
            state.blocks.push({
                type: 'heading',
                level: headingMatch[1].length as 1 | 2 | 3,
                tokens: parseInlineTokens(headingMatch[2])
            });
            return;
        }

        const unorderedMatch = trimmed.match(/^[-*•]\s+(.+)$/);
        if (unorderedMatch) {
            flushBlock(state, 'paragraph');
            if (state.listType === 'ol') flushBlock(state, 'list');
            state.listType = 'ul';
            state.listItems.push(unorderedMatch[1]);
            return;
        }

        const orderedMatch = trimmed.match(/^\d+\.\s+(.+)$/);
        if (orderedMatch) {
            flushBlock(state, 'paragraph');
            if (state.listType === 'ul') flushBlock(state, 'list'); // end and save ol block
            state.listType = 'ol';
            state.listItems.push(orderedMatch[1]);
            return;
        }

        state.paragraph.push(trimmed);
    }

	/**
	 * text.replaceAll('\r\n', '\n'): Converts Windows-style line endings (\r\n) to Unix-style (\n), so all newlines are consistent
	 * converts a completed markdown string into structured AnswerBlock[] for the template to render. Called once per finished response (and on partial answer for live preview via $derived)
	 */
    function renderAnswer(text: string): AnswerBlock[] {
        const lines = text.replaceAll('\r\n', '\n').trim().split('\n');
        const state = initParserState();

        for (const rawLine of lines) {
            const line = rawLine.trimEnd(); //need line (with only trailing whitespace removed) for cases where leading spaces matter (like code blocks: indentation (leading spaces) is important and should be preserved)
            const trimmed = line.trim();
            if (handleCodeState(line, trimmed, state)) continue;
            handleRegularLine(trimmed, state);
        }

        flushBlock(state, 'paragraph');
        flushBlock(state, 'list');
        if (state.inCodeBlock) flushBlock(state, 'code');
        return state.blocks;
    }

	/**
	 * reads the raw HTTP stream chunk by chunk, reassembles SSE events, extracts data: lines, and updates answer live as text arrives. Returns the full accumulated string when streaming ends
	 */
    async function parseSSEStream(response: Response): Promise<string> {
        if (!response.body) throw new Error('No response body');

        const reader = response.body.getReader();
        const decoder = new TextDecoder(); //Built-in object for decoding binary data (Uint8Array) into strings. { stream: true } allows incremental decoding (for streaming)
        let buffer = '';
        let fullText = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true }); // Decodes the current chunk (value) into a string, 
            const events = buffer.split('\n\n'); // SSE event separator: has all except the last
            buffer = events.pop() || ''; // keeps only the last event

            for (const event of events) {
                const lines = event.split('\n');
                const dataParts: string[] = [];

                for (const line of lines) {
                    if (line.startsWith('data:')) {
                        dataParts.push(line.slice(5).replace(/^ /, ''));// rmv single leading space
                    }
                }

                if (dataParts.length) {
                    let newText = dataParts.join('\n');
                    fullText += newText;
                    answer = fullText; // reactive state var, bound to the displayed output
                }
            }
        }

        return fullText;
    }

    /**
     * Skip code blocks in history — token-expensive and low context value.
     * Cap paragraphs and lists at 300 chars. Headings are always short.
     */
    function blockToText(block: AnswerBlock): string {
        const tokensToText = (tokens: InlineToken[]) =>
            tokens.map(t => ('value' in t ? t.value : '')).join('').trim();

        if (block.type === 'code')      return '';
        if (block.type === 'paragraph') return tokensToText(block.tokens).slice(0, 300);
        if (block.type === 'heading')   return tokensToText(block.tokens);
        if (block.type === 'list')      return block.items.map(tokensToText).join(' ').slice(0, 300);
        return '';
    }

	/**
	 * Builds a messages array — flattens chat history into user/assistant pairs, then appends the new prompt at the end
	 * POSTs it to the given endpoint as JSON
	 * Throws an error if the response is not OK
	 * Returns parseSSEStream(res) — reads the streamed response chunk by chunk (Server-Sent Events)
	* $state(...) — marks history as reactive state. Any time history changes, every place in the template that reads it re-renders automatically
	 */
    async function streamChat( endpoint: string, prompt: string, fallbackError: string,
            signal?: AbortSignal, historySnapshot: typeof history = [] ): Promise<string> {
        const messages = [
            ...historySnapshot.flatMap(entry => [
                { role: 'user', content: entry.question },
                { role: 'assistant', content: entry.blocks.map(blockToText).join(' ') }
            ]),
            { role: 'user', content: prompt } // last q
        ];

        const res = await fetch(endpoint, { // endpoint is the url
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages, prompt}),
            signal
        });

        if (!res.ok) {
            const txt = await res.text();
            throw new Error(txt || fallbackError);
        }

        return parseSSEStream(res);
    }

	/**
	 * AbortController is a browser built-in for cancelling async operations.
	 * const controller = new AbortController();
	   controller.signal — a read-only AbortSignal object
       controller.abort() — fires the cancel
	 */
    function stopStreaming() {
        if (!loading || !activeStreamController) return;
        activeStreamController.abort();
        activeStreamController = null;
        loading = false;
        // Save partial answer and question to history
        if (question.trim() || answer.trim()) {
            history = [{ question: question.trim(), blocks: renderAnswer(answer) }, ...history];
            question = '';
            answer = '';
        }
    }

    let renderedAnswer = $derived(renderAnswer(answer));
	const MAX_HISTORY = 10;

	/**
	 *  interface SubmitEvent
        defines the object used to represent an HTML form's HTMLFormElement.submit_event event
	  * Trims and validates the input
	  *	Aborts any in-progress stream if the user submits again
	  *	Picks the API endpoint based on llmMode (Gemini or Ollama)
	  *	Calls streamChat() with the prompt and last N history messages
	  *	On success, prepends the Q&A to history and clears the input
	  *	On abort, silently exits; on other errors, sets the error message
	 */
    async function askQuestion(event?: SubmitEvent) {
        event?.preventDefault(); // cancels page reload; The ?. means it's safe to call even if no event was passed (e.g., called programmatically).

        const prompt = question.trim();
        if (!prompt) return;

        if (loading && activeStreamController) { //If the user submits while a previous request is still streaming, it cancels that stream via AbortController.abort() and clears the reference
            activeStreamController.abort();
            activeStreamController = null;
        }

        loading = true;
        error = '';
        answer = '';

        const controller = new AbortController(); // each req gets a new controller
        activeStreamController = controller;

        try {
            const endpoint = llmMode === 'gemini' ? '/api/ai-assist' : '/api/ollama';
            const fallbackError = llmMode === 'gemini' ? 'Server error' : 'Ollama service unavailable';
            const historySnapshot = history.slice(0, MAX_HISTORY).reverse(); // give last max history of the slice
            const result = await streamChat(endpoint, prompt, fallbackError, controller.signal, historySnapshot); // actuall API call

            const completedAnswer = result.trim();
            if (completedAnswer) {
                history = [{ question: prompt, blocks: renderAnswer(completedAnswer) }, ...history]; // prepend to history to show most recent first
                question = '';
            }
        } catch (e) {
            if (e instanceof Error && e.name === 'AbortError') {
                return;
            }
            error = e instanceof Error ? e.message : 'Unknown error';
        } finally {
            if (activeStreamController === controller) { //Guards against a race condition where the user fires a second question before the first finishes.
                activeStreamController = null;
                loading = false;
            }
        }
    }

    async function toggleDictation() { // can use await inside
    if (dictating) {
        // If LLM is still processing, stop it and save partial answer to history first
        if (loading) stopStreaming();
        mediaRecorder?.stop(); //?. — safely calls .stop() only if mediaRecorder is not null
        dictating = false;
    } else {
        let stream: MediaStream; // type annotation, no val assigned
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true }); // Browser API — asks user for mic permission, returns an audio stream. await pauses until the user grants/denies.
        } catch {
            error = 'Microphone access denied.';
            return;
        }
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
	        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' }); //Blob = Binary Large Object — a browser built-in for raw binary data; type: 'audio/wav' tells the browser what MIME type this binary data is.
            await sendToWhisper(audioBlob); //puts the blob into a FormData and sends it via fetch
            stream.getTracks().forEach(track => track.stop());
            await askQuestion();
        };

        mediaRecorder.start();
        dictating = true;
    }
}

async function sendToWhisper(blob: Blob) {
    const formData = new FormData();
    formData.append('file', blob, 'recording.wav'); /*recording.wav is not a real file — it's just a filename hint sent inside the HTTP request so the Whisper backend knows what to call it;Created: only in memory, when formData.append(...) runs
	From: the audioBlob (the merged chunks from recording)
	Deleted: automatically by the garbage collector after the fetch request completes — it never touches disk
	Location: lives only in browser RAM, no file system path;The Whisper backend receives it as a multipart form upload and reads the bytes directly — it may or may not save it temporarily on its end. */

    try {
        const response = await fetch('/stt/convert_audio', { //The Whisper backend at main.py defines the /convert_audio endpoint. It expects a multipart form upload with a field named file — which is exactly what formData.append('file', blob, 'recording.wav') sends.
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        // This puts the text into your input field/state
        if (data.text) {
            console.log("Whisper result:", data.text);
            // take the string from Whisper and put it into the input box
            question = data.text.trim();
        }
    } catch (err) {
        error = "Could not reach Whisper backend.";
        console.error(err);
    }
}
</script>

<div class="container">
    {#snippet renderToken(token: InlineToken)}
        {#if token.type === 'text'}
            {token.value}
        {:else if token.type === 'strong'}
            <strong>{token.value}</strong>
        {:else if token.type === 'em'}
            <em>{token.value}</em>
        {:else if token.type === 'code'}
            <code>{token.value}</code>
        {:else if token.type === 'link'}
            <a href={token.href} target="_blank" rel="noreferrer noopener">{token.value}</a>
        {/if}
    {/snippet}

    <h2><b>Zombie Kittens</b> AI Assist 🐈‍⬛ </h2>
    <p class="info">You can ask 2 questions a minute and 20 a day</p>
    <hr>
    <div class="parent-llms">
        <button
            class="toggle-button"
            class:active={llmMode === 'gemini'}
            onclick={() => llmMode = 'gemini'}
            disabled={loading}
        >
            🔵 Gemini
        </button>
        <button
            class="toggle-button"
            class:active={llmMode === 'ollama'}
            onclick={() => llmMode = 'ollama'}
            disabled={loading}
        >
            🦙 Ollama
        </button>
    </div>
    <form class="form-input-parent" onsubmit={askQuestion}>
        <input
            class="form-input"
            type="text"
            bind:value={question}
            placeholder="Ask a question..."
        />
        <button type="button" onclick={toggleDictation} aria-pressed={dictating} disabled={loading && !dictating}>
            {dictating ? 'Stop Dictate' : 'Dictate'}
        </button>
        <button type="submit" disabled={loading || !question.trim()}>
            Ask
        </button>
        <button type="button" onclick={stopStreaming} disabled={!loading}>
            Stop
        </button>
    </form>
    {#if error}
        <div style="color:tomato;text-align:center;">{error}</div>
    {/if}
    {#if loading}
        <div style="text-align:center;">Loading...</div>
    {/if}
    {#if answer}
        <div class="answer-card">
            {#each renderedAnswer as block, index (index)}
                {#if block.type === 'paragraph'}
                    <p>
                        {#each block.tokens as token, tokenIndex (tokenIndex)}
                            {@render renderToken(token)}
                        {/each}
                    </p>
                {:else if block.type === 'heading'}
                    <svelte:element this={`h${block.level}`}>
                        {#each block.tokens as token, tokenIndex (tokenIndex)}
                            {@render renderToken(token)}
                        {/each}
                    </svelte:element>
                {:else if block.type === 'list'}
                    {#if block.ordered}
                        <ol>
                            {#each block.items as item, itemIndex (itemIndex)}
                                <li>
                                    {#each item as token, tokenIndex (tokenIndex)}
                                        {@render renderToken(token)}
                                    {/each}
                                </li>
                            {/each}
                        </ol>
                    {:else}
                        <ul>
                            {#each block.items as item, itemIndex (itemIndex)}
                                <li>
                                    {#each item as token, tokenIndex (tokenIndex)}
                                        {@render renderToken(token)}
                                    {/each}
                                </li>
                            {/each}
                        </ul>
                    {/if}
                {:else if block.type === 'code'}
                    <pre><code class={block.lang ? `language-${block.lang}` : undefined}>{block.code}</code></pre>
                {/if}
            {/each}
        </div>
    {/if}
    {#if history.length}
    <section class="answer-card">
        <h2>History</h2>
        {#each history.slice(0, MAX_HISTORY) as entry, entryIndex (entryIndex)}
            <article style="border-bottom: 1px solid var(--panel-border); margin-bottom: 1.5rem; padding-bottom: 1rem;">
                <h3>Q {history.length - entryIndex}: {entry.question}</h3>
                
                {#each entry.blocks as block, blockIndex (blockIndex)}
                    {#if block.type === 'paragraph'}
                        <p>
                            {#each block.tokens as token, tokenIndex (tokenIndex)}
                                {@render renderToken(token)}
                            {/each}
                        </p>
                    {:else if block.type === 'heading'}
                        <svelte:element this={`h${block.level}`}>
                            {#each block.tokens as token, tokenIndex (tokenIndex)}
                                {@render renderToken(token)}
                            {/each}
                        </svelte:element>
                    {:else if block.type === 'list'}
                        {#if block.ordered}
                            <ol>
                                {#each block.items as item, itemIndex (itemIndex)}
                                    <li>
                                        {#each item as token, tokenIndex (tokenIndex)}
                                            {@render renderToken(token)}
                                        {/each}
                                    </li>
                                {/each}
                            </ol>
                        {:else}
                            <ul>
                                {#each block.items as item, itemIndex (itemIndex)}
                                    <li>
                                        {#each item as token, tokenIndex (tokenIndex)}
                                            {@render renderToken(token)}
                                        {/each}
                                    </li>
                                {/each}
                            </ul>
                        {/if}
                    {:else if block.type === 'code'}
                        <pre><code class={block.lang ? `language-${block.lang}` : undefined}>{block.code}</code></pre>
                    {/if}
                {/each}
            </article>
        {/each}
    </section>
{/if}
</div>