<script lang="ts">
  import { goto } from '$app/navigation'; 
  import Input from '$lib/components/Input.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import Button from '$lib/components/Button.svelte';

  let projectname = "";
  let body = "";
  let error = "";
  let submitting = false;

  async function submitQuestion() 
  {
    if (!projectname.trim() || !body.trim()) 
	{
      error = "Please fill in all fields.";
      return;
    }
	error = "";
	submitting = true;
	try {
		const res = await fetch('/api/posts', 
		{
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify
			({projectname, body})
		});

		if (res.ok) goto('/posts');
		else if (res.status === 401) 
		error = "You must be logged in to post a question.";
		else error = "Something went wrong, please try again.";
	}
	finally {submitting = false;
	}
  }
</script>

<div class="post-question">
  <h1>ASK A QUESTION</h1>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <Input
    label="Project Name"
    name="projectname"
    placeholder="Enter project name"
    bind:value={projectname}
  />

  <Textarea
    label="Question"
    name="body paragraph"
    placeholder="Write your question in detail here..."
    bind:value={body}
    rows={5}
  />

  <button class="button-primary" type="button" on:click={submitQuestion}>
    {submitting ? 'Submitting...' : 'Submit'}
  </button>

</div>

<style>
  .post-question {
    width: 100%;
    max-width: 700px;
    padding: 0rem;
    text-align: left;
  }
  .error {
    color: var(--color-error-250);
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
  }
</style>