<style>
    .container {
        --olive-text: #F4FFE8;
        --panel-bg: #1b231b;
        --panel-border: rgba(244, 255, 232, 0.12);
        --soft-shadow: 0 0 12px #F4FFE8, 0 0 8px #F4FFE8;
        --focus-border: rgba(168, 188, 132, 0.9);
        --focus-glow: rgba(168, 188, 132, 0.22);
        color: white;
        display: flex;
        flex-direction: column;
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
        display: inline-block;
        margin: 20px auto;
        max-width: 780px;
        background: var(--panel-bg);
        border: 1px solid var(--panel-border);
        border-radius: 14px;
        padding: 1.25rem 1.25rem;
        text-align: left;
        line-height: 1.6;
        overflow-x: auto;
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
        border-radius: 14px;
        padding: 1.25rem 1.25rem;
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
        border: 1px solid rgba(244, 255, 232, 0.18);
        border-radius: 14px;
        background: #152015;
        color: #f4ffe8;
        padding: 1.25rem 1.5rem;
        cursor: pointer;
        white-space: nowrap;
    }

	.parent-llms {
		display: flex;
		gap: 1rem;
		justify-content: center;
	}

    .toggle-button {
        flex: 0 0 auto;
        border: 1px solid rgba(244, 255, 232, 0.18);
        border-radius: 14px;
        color: #a8bc84;
        padding: .75rem 1.5rem;
		margin-top: 1rem;
        cursor: pointer;
        white-space: nowrap;
        font-size: 0.9em;
        transition: background-color 0.2s ease;
    }

    .toggle-button.active {
        color: #f4ffe8;
        border-color: rgba(168, 188, 132, 0.6);
    }

    .form-input-parent button:disabled {
        cursor: not-allowed;
        opacity: 0.55;
    }

    .answer-card :global(h1),
    .answer-card :global(h2),
    .answer-card :global(h3) {
        margin: 1rem 0 0.5rem;
        line-height: 1.2;
        color: #f4ffe8;
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
        border-radius: 12px;
        background: #0d120d;
        color: #e6f4dc;
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
        background: rgba(244, 255, 232, 0.12);
    }

    .answer-card :global(blockquote) {
        margin: 0.75rem 0;
        padding-left: 1rem;
        border-left: 3px solid rgba(244, 255, 232, 0.25);
        color: #d8e4d2;
    }

    .answer-card :global(a) {
        color: #98f5c5;
    }

    .answer-card :global(hr) {
        border: 0;
        border-top: 1px solid rgba(244, 255, 232, 0.16);
        margin: 1rem 0;
    }

    .answer-card :global(strong) {
        color: #ffffff;
    }

    .answer-card :global(em) {
        color: #dbe9d2;
    }
</style>

<script lang="ts">
    // STATE
    let question = $state('');
    let answer = $state('');
    let loading = $state(false);
    let error = $state('');
    let activeStreamController = $state<AbortController | null>(null);
    let llmMode = $state<'gemini' | 'ollama'>('gemini');
    let history = $state<{ question: string; blocks: AnswerBlock[] }[]>([]);
    let dictating = $state(false);
    let recognition: any = null;
    let interimTranscript = '';
    // let isQueued = $state(false);
    let queueTimer: ReturnType<typeof setTimeout> | null = null;
    let mediaRecorder = $state<MediaRecorder | null>(null);
    let audioChunks: Blob[] = [];

    // TYPES
    type InlineToken =
        | { type: 'text'; value: string }
        | { type: 'strong'; value: string }
        | { type: 'em'; value: string }
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

    function parseInlineTokens(text: string): InlineToken[] {
        const tokens: InlineToken[] = [];
        const pattern = /`([^`]+)`|\*\*([^*]+)\*\*|__([^_]+)__|\*([^*]+)\*|_([^_]+)_|\[(.+?)\]\((.+?)\)/g;
        let lastIndex = 0;

        for (const match of text.matchAll(pattern)) {
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

    function createParserState(): ParserState {
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
     * Generic flushBlock function to flush a block by type.
     * @param state ParserState
     * @param type 'paragraph' | 'list' | 'code'
     */
    function flushBlock(state: ParserState, type: 'paragraph' | 'list' | 'code') {
        if (type === 'paragraph') {
            if (!state.paragraph.length) return;
            state.blocks.push({
                type: 'paragraph',
                tokens: parseInlineTokens(state.paragraph.join(' ').replace(/\s+/g, ' ').trim())
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

    function handleCodeState(line: string, trimmed: string, state: ParserState): boolean {
        if (!state.inCodeBlock) return false;
        if (trimmed.startsWith('```')) {
            state.inCodeBlock = false;
            flushBlock(state, 'code');
        } else {
            state.codeLines.push(line);
        }
        return true;
    }

    function handleRegularLine(trimmed: string, state: ParserState) {
        if (trimmed.startsWith('```')) {
            flushBlock(state, 'paragraph');
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
            if (state.listType === 'ul') flushBlock(state, 'list');
            state.listType = 'ol';
            state.listItems.push(orderedMatch[1]);
            return;
        }

        state.paragraph.push(trimmed);
    }

    function renderAnswer(text: string): AnswerBlock[] {
        const lines = text.replaceAll('\r\n', '\n').trim().split('\n');
        const state = createParserState();

        for (const rawLine of lines) {
            const line = rawLine.trimEnd();
            const trimmed = line.trim();
            if (handleCodeState(line, trimmed, state)) continue;
            handleRegularLine(trimmed, state);
        }

        flushBlock(state, 'paragraph');
        flushBlock(state, 'list');
        if (state.inCodeBlock) flushBlock(state, 'code');
        return state.blocks;
    }

    async function parseSSEStream(response: Response): Promise<string> {
        if (!response.body) throw new Error('No response body');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullText = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            // isQueued = false;
            // if (queueTimer) clearTimeout(queueTimer);

            buffer += decoder.decode(value, { stream: true });
            const events = buffer.split('\n\n');
            buffer = events.pop() || '';

            for (const event of events) {
                const lines = event.split('\n');
                const dataParts: string[] = [];

                for (const line of lines) {
                    if (line.startsWith('data:')) {
                        dataParts.push(line.slice(5).replace(/^ /, ''));
                    }
                }

                if (dataParts.length) {
                    let newText = dataParts.join('\n');
                    fullText += newText;
                    answer = fullText;
                }
            }
        }

        return fullText;
    }

    const MAX_HISTORY = 10;

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

    async function callLLM(
            endpoint: string,
            prompt: string,
            fallbackError: string,
            signal?: AbortSignal,
            historySnapshot: typeof history = []
        ): Promise<string> {
        const messages = [
            ...historySnapshot.flatMap(entry => [
                { role: 'user', content: entry.question },
                { role: 'assistant', content: entry.blocks.map(blockToText).join(' ') }
            ]),
            { role: 'user', content: prompt }
        ];

        const res = await fetch(endpoint, {
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

    function stopStreaming() {
        if (!loading || !activeStreamController) return;
        activeStreamController.abort();
        activeStreamController = null;
        loading = false;
        // Save partial answer and question to history if not empty: todo: doesnt work
        if (question.trim() || answer.trim()) {
            history = [{ question: question.trim(), blocks: renderAnswer(answer) }, ...history];
            question = '';
            answer = '';
        }
    }

    // DERIVED
    let renderedAnswer = $derived(renderAnswer(answer));

    async function askQuestion(event?: SubmitEvent) {
        event?.preventDefault();

        const prompt = question.trim();
        if (!prompt) return;

        if (loading && activeStreamController) {
            activeStreamController.abort();
            activeStreamController = null;
        }

        loading = true;
        // isQueued = false;
        error = '';
        answer = '';

        // queueTimer = setTimeout(() => {
        //     if (loading && !answer) isQueued = true;
        // }, 3000);
    
        const controller = new AbortController();
        activeStreamController = controller;

        try {
            const endpoint = llmMode === 'gemini' ? '/api/ai-assist' : '/api/ollama';
            const fallbackError = llmMode === 'gemini' ? 'Server error' : 'Ollama service unavailable';
            const historySnapshot = history.slice(-MAX_HISTORY);
            const result = await callLLM(endpoint, prompt, fallbackError, controller.signal, historySnapshot);

            const completedAnswer = result.trim();
            if (completedAnswer) {
                // history = [...history, { question: prompt, blocks: renderAnswer(completedAnswer) }];
                history = [{ question: prompt, blocks: renderAnswer(completedAnswer) }, ...history]; // prepend to history to show most recent first
                question = '';
            }
        } catch (e) {
            if (e instanceof Error && e.name === 'AbortError') {
                return;
            }
            error = e instanceof Error ? e.message : 'Unknown error';
        } finally {
            if (activeStreamController === controller) {
                activeStreamController = null;
                // isQueued = false;
                loading = false;
            }
        }
    }

    async function toggleDictation() {
    if (dictating) {
        // Stop recording
        mediaRecorder?.stop();
        dictating = false;
    } else {
        // Start recording
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true }); //Asks for mic permission (locally).
        mediaRecorder = new MediaRecorder(stream); //Captures raw audio chunks while you speak.
        audioChunks = [];

        mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await sendToWhisper(audioBlob);
            stream.getTracks().forEach(track => track.stop());
            await askQuestion();
        };

        mediaRecorder.start();
        dictating = true;
    }
}

async function sendToWhisper(blob: Blob) {
    const formData = new FormData();
    formData.append('file', blob, 'recording.wav');

    try {
        const response = await fetch('http://localhost:8091/convert_audio', {
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
        <button type="button" onclick={toggleDictation} aria-pressed={dictating}>
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
    <!-- {#if isQueued}
        <div style="color: #a8bc84; text-align:center; font-style: italic;">
            🐢 CPU is busy. You are in line...
        </div>
    {/if} -->
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
        {#each history as entry, entryIndex (entryIndex)}
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