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
    form {
        margin: 2em auto;
        text-align: center;
        /* max-width: 500px; */
    }
    .form-input {
        width: 60%;
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
            const res = await fetch('http://localhost:8081/api/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: question })
            });
            if (!res.ok) throw new Error('Server error');
            const data = await res.json();
            answer = data.response;
        } catch (e) {
            error = e.message;
        } finally {
            loading = false;
        }
    }
</script>

<div class="container">
    <h1>🐈‍⬛Zombie Kittens Know It All<span class="kitten">🧟</span></h1>
    <hr>
    <p style="text-align: center; font-size: 1.2em; margin-top: 1em;">
        Welcome to the AI Assist page! Here, you can ask our AI assistant anything about our project, and it will provide you with accurate and helpful information. Whether you have questions about the codebase, project structure, or any specific functionality, just type your query below and let our AI assistant do the rest!
    </p>
    <form on:submit|preventDefault={askQuestion} >
        <input class="form-input" type="text" bind:value={question} placeholder="Ask a question..."/>
        <button type="submit" disabled={loading || !question.trim()}>Ask</button>
    </form>
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

