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
    footer {
        width: 100%;
        background: #222;
        color: #F4FFE8;
        text-align: center;
        padding: 1em 0;
        position: fixed;
        left: 0;
        bottom: 0;
        font-size: 1em;
        letter-spacing: 0.05em;
    }

    .form-input {
        width: 80%;
        /* max-width: 400px; */
        padding: 0.5em;
        font-size: 1em;
        border: none;
        border-radius: 4px;
        margin-right: 0.5em;
        color: black;
    }

</style>
<script>
    let question = $state('');
    let answer = $state('');
    let loading = $state(false);
    let error = $state('');

    async function askQuestion() {
        loading = true;
        error = '';
        answer = '';

    try {
        const res = await fetch('/api/ai-assist', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: question })
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

            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    if (answer && !answer.endsWith(' ') && !answer.startsWith(' ') && !/^[.,!?;:)]/.test(line.slice(6))) {
                        answer += ' ';
                    }
                    answer += line.slice(6);
                } else if (line.startsWith('event: end')) {
                    break;
                }
            }
        }
    } catch (e) {
        error = e instanceof Error ? e.message : 'Unknown error';
    } finally {
        loading = false;
    }
}

</script>

<div class="container">
    <h1>🐈‍⬛Zombie Kittens Know It All<span class="kitten">🧟</span></h1>
    <hr>
    <p style="text-align: center; font-size: 1.2em; margin-top: 1em;">
        Welcome to the AI Assist page! Here, if really stuck you can ask a question and hope the <b>Zombie Kittens</b> will share their infinite wisdom with you. The catch is that you have a limit of 3 questions a day.
    </p>

     <div>
        <input
            class="form-input"
            type="text"
            bind:value={question}
            placeholder="Ask a question..."
        />
        <button type="button" on:click={askQuestion} disabled={loading || !question.trim()}>
            Ask
        </button>
     </div>
    {#if loading}
        <div style="text-align:center;">Loading...</div>
    {/if}
    {#if answer}
        <div style="margin:1em auto;text-align:center;max-width:600px;background:#222;padding:1em;border-radius:8px;">{answer}</div>
    {/if}
    {#if error}
        <div style="color:red;text-align:center;">{error}</div>
    {/if}
</div>
    <footer class="footer">
        <span class="footer">🐈‍⬛</span> <b>Zombie Kittens</b> are always watching... &copy; {new Date().getFullYear()}<span class="kitten">🧟‍</span>
    </footer>

