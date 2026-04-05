<style>
    .container {
        background: #001a00;
        color: white;
        min-height: 100vh;
        min-width: 100vw;
        width: 100%;
        display: flex;
        flex-direction: column;
    }
    h1 {
        color: #F4FFE8;
        text-shadow: 0 0 12px #F4FFE8, 0 0 8px #F4FFE8;
        font-size: 2.8em;
        margin-top: 32px;
        text-align: center;
    }
    .info {
        color: #F4FFE8;
        text-align: center;
        margin: 1rem 0;
        text-shadow: 0 0 12px #F4FFE8, 0 0 8px #F4FFE8;
    }
    /* footer {
        width: 100%;
        background: #222;
        color: #F4FFE8;
        text-align: center;
        padding: .5em 0;
        position: fixed;
        left: 0;
        bottom: 0;
        font-size: 1em;
        letter-spacing: 0.05em;
    } */

    .answer-card {
        width: 100%;
        display: inline-block;
        margin: 20px auto;
        max-width: 780px;
        background: #1b231b;
        border: 1px solid rgba(244, 255, 232, 0.12);
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
        margin: 0;
        background: #1b231b;
        border: 1px solid rgba(244, 255, 232, 0.12);
        border-radius: 14px;
        padding: 1.25rem 1.25rem;
        color: #f4ffe8;
        line-height: 1.6;
        box-sizing: border-box;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .form-input:focus,
    .form-input:focus-visible {
        outline: none;
        border-color: rgba(168, 188, 132, 0.9);
        box-shadow: 0 0 0 3px rgba(168, 188, 132, 0.22);
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

    .answer-card :global(h1) {
        font-size: 1.5rem;
    }

    .answer-card :global(h2) {
        font-size: 1.25rem;
    }

    .answer-card :global(h3) {
        font-size: 1.1rem;
    }

    .answer-card :global(p) {
        margin: 0.75rem 0;
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
    let question = $state('');
    let answer = $state('');
    let loading = $state(false);
    let error = $state('');
    /**
     *  $state(...) In Svelte 5, $state makes the variable reactive rune/function. When history changes, the UI that depends on it updates automatically. <{ question: string; blocks: AnswerBlock[] }[]> 
This is a TypeScript generic type annotation for the state value. It says history must be an array of objects.
Each object has: question: string; blocks: AnswerBlock[] So history is not a single object. It is a list of chat entries.
= [] The initial value is an empty array. So at startup, there is no saved conversation history yet.
equal to: type HistoryEntry = {
  question: string;
  blocks: AnswerBlock[];
};

let history = $state<HistoryEntry[]>([]);
     */
    let history = $state<{ question: string; blocks: AnswerBlock[] }[]>([]);

    // | can be exactly one of those object shapes.
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

    function parseInlineTokens(text: string) {
        const tokens: InlineToken[] = [];
        const pattern = /`([^`]+)`|\*\*([^*]+)\*\*|__([^_]+)__|\*([^*]+)\*|_([^_]+)_|\[(.+?)\]\((.+?)\)/g;

        let lastIndex = 0;
        for (const match of text.matchAll(pattern)) {
            const index = match.index ?? 0;

            if (index > lastIndex) {
                tokens.push(createTextToken(text.slice(lastIndex, index)));
            }

            if (match[1]) {
                tokens.push({ type: 'code', value: match[1] });
            } else if (match[2]) {
                tokens.push({ type: 'strong', value: match[2] });
            } else if (match[3]) {
                tokens.push({ type: 'strong', value: match[3] });
            } else if (match[4]) {
                tokens.push({ type: 'em', value: match[4] });
            } else if (match[5]) {
                tokens.push({ type: 'em', value: match[5] });
            } else if (match[6] && match[7]) {
                tokens.push({ type: 'link', value: match[6], href: match[7] });
            }

            lastIndex = index + match[0].length;
        }

        if (lastIndex < text.length) {
            tokens.push(createTextToken(text.slice(lastIndex)));
        }

        return tokens;
    }

    function renderAnswer(text: string): AnswerBlock[] {
        const lines = text.replaceAll('\r\n', '\n').trim().split('\n');
        const blocks: AnswerBlock[] = [];
        let paragraph: string[] = [];
        let listItems: string[] = [];
        let listType: 'ul' | 'ol' | null = null;
        let codeLines: string[] = [];
        let codeLang = '';
        let inCodeBlock = false;

        const flushParagraph = () => {
            if (!paragraph.length) return;
            blocks.push({ type: 'paragraph', tokens: parseInlineTokens(paragraph.join(' ').replace(/\s+/g, ' ').trim()) });
            paragraph = [];
        };

        const flushList = () => {
            if (!listItems.length || !listType) return;
            blocks.push({
                type: 'list',
                ordered: listType === 'ol',
                items: listItems.map((item) => parseInlineTokens(item))
            });
            listItems = [];
            listType = null;
        };

        const flushCode = () => {
            blocks.push({ type: 'code', lang: codeLang.replace(/[^a-z0-9_-]/gi, ''), code: codeLines.join('\n') });
            codeLines = [];
            codeLang = '';
        };

        for (const rawLine of lines) {
            const line = rawLine.trimEnd();
            const trimmed = line.trim();

            if (inCodeBlock) {
                if (trimmed.startsWith('```')) {
                    inCodeBlock = false;
                    flushCode();
                } else {
                    codeLines.push(line);
                }
                continue;
            }

            if (trimmed.startsWith('```')) {
                flushParagraph();
                flushList();
                inCodeBlock = true;
                codeLang = trimmed.slice(3).trim();
                continue;
            }

            if (!trimmed) {
                flushParagraph();
                flushList();
                continue;
            }

            const headingMatch = trimmed.match(/^(#{1,3})\s+(.+)$/);
            if (headingMatch) {
                flushParagraph();
                flushList();
                const level = headingMatch[1].length;
                blocks.push({ type: 'heading', level: level as 1 | 2 | 3, tokens: parseInlineTokens(headingMatch[2]) });
                continue;
            }

            const unorderedMatch = trimmed.match(/^[-*•]\s+(.+)$/);
            if (unorderedMatch) {
                flushParagraph();
                if (listType === 'ol') flushList();
                listType = 'ul';
                listItems.push(unorderedMatch[1]);
                continue;
            }

            const orderedMatch = trimmed.match(/^\d+\.\s+(.+)$/);
            if (orderedMatch) {
                flushParagraph();
                if (listType === 'ul') flushList();
                listType = 'ol';
                listItems.push(orderedMatch[1]);
                continue;
            }

            paragraph.push(trimmed);
        }

        flushParagraph();
        flushList();
        if (inCodeBlock) flushCode();

        return blocks;
    }

    let renderedAnswer = $derived(renderAnswer(answer));

    async function askQuestion(event?: SubmitEvent) {
        event?.preventDefault();

        const prompt = question.trim();
        if (!prompt || loading) return;

        loading = true;
        error = '';
        answer = '';
        question = '';

    try {
        const res = await fetch('/api/ai-assist', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });
        // console.log('status:', res.status);
        // console.log('content-type:', res.headers.get('content-type'));

        if (!res.ok) {
            const txt = await res.text();
            throw new Error(txt || 'Server error');
        }

        if (!res.body) {
            throw new Error('No response body');
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            const events = buffer.split('\n\n');
            buffer = events.pop() || '';

            for (const event of events) {
                const lines = event.split('\n');
                const dataParts: string[] = [];
                let isEndEvent = false;

                for (const line of lines) {
                    if (line.startsWith('event:') && line.slice(6).trim() === 'end') {
                        isEndEvent = true;
                    } else if (line.startsWith('data:')) {
                        dataParts.push(line.slice(5).trimStart());
                    }
                }

                if (dataParts.length) {
                    // Join data lines within the same SSE event with newlines,
                    // but do not force a newline between separate events.
                    answer += dataParts.join('\n');
                }

                if (isEndEvent) {
                    break;
                }
            }
        }

        const completedAnswer = answer.trim();
        if (completedAnswer) {
            history = [...history, { question: prompt, blocks: renderAnswer(completedAnswer) }];
        }
    } catch (e) {
        error = e instanceof Error ? e.message : 'Unknown error';
    } finally {
        loading = false;
    }
}

</script>

<div class="container">
    <h1>
        Welcome to <b>Zombie Kittens</b> AI Assist page 🐈‍⬛ 
    </h1>
    <p class="info"> You can ask 2 questions a minute and 20 per day</p>
    <hr>
     <form class="form-input-parent" onsubmit={askQuestion}>
        <input
            class="form-input"
            type="text"
            bind:value={question}
            placeholder="Ask a question..."
        />
        <button type="submit" disabled={loading || !question.trim()}>
            Ask
        </button>
     </form>
    {#if loading}
        <div style="text-align:center;">Loading...</div>
    {/if}
    {#if answer}
        <div class="answer-card">
            {#each renderedAnswer as block, index (index)}
                {#if block.type === 'paragraph'}
                    <p>
                        {#each block.tokens as token, tokenIndex (tokenIndex)}
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
                        {/each}
                    </p>
                {:else if block.type === 'heading'}
                    <svelte:element this={`h${block.level}`}>
                        {#each block.tokens as token, tokenIndex (tokenIndex)}
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
                        {/each}
                    </svelte:element>
                {:else if block.type === 'list'}
                    {#if block.ordered}
                        <ol>
                            {#each block.items as item, itemIndex (itemIndex)}
                                <li>
                                    {#each item as token, tokenIndex (tokenIndex)}
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
                                    {/each}
                                </li>
                            {/each}
                        </ol>
                    {:else}
                        <ul>
                            {#each block.items as item, itemIndex (itemIndex)}
                                <li>
                                    {#each item as token, tokenIndex (tokenIndex)}
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
                <article>
                    <h3>Q {entryIndex + 1}: {entry.question}</h3>
                    {#each entry.blocks as block, blockIndex (blockIndex)}
                        {#if block.type === 'paragraph'}
                            <p>
                                {#each block.tokens as token, tokenIndex (tokenIndex)}
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
                                {/each}
                            </p>
                        {:else if block.type === 'heading'}
                            <svelte:element this={`h${block.level}`}>
                                {#each block.tokens as token, tokenIndex (tokenIndex)}
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
                                {/each}
                            </svelte:element>
                        {:else if block.type === 'list'}
                            {#if block.ordered}
                                <ol>
                                    {#each block.items as item, itemIndex (itemIndex)}
                                        <li>
                                            {#each item as token, tokenIndex (tokenIndex)}
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
                                            {/each}
                                        </li>
                                    {/each}
                                </ol>
                            {:else}
                                <ul>
                                    {#each block.items as item, itemIndex (itemIndex)}
                                        <li>
                                            {#each item as token, tokenIndex (tokenIndex)}
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
    {#if error}
        <div style="color:red;text-align:center;">{error}</div>
    {/if}
</div>
    <!-- <footer class="footer">
        <span class="footer">🐈‍⬛</span> <b>Zombie Kittens</b> are always watching... &copy; {new Date().getFullYear()}<span class="kitten">🧟‍</span>
    </footer> -->

