<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import Input from '$lib/components/Input.svelte';
	import Textarea from '$lib/components/Textarea.svelte';

	let { data } = $props() as any as { data: { subjectList: { id: number; name: string }[] } };
	let subjectList = data.subjectList;

	let projectname = "";
	let body = "";
	let error = $state(''); // For reactive error messages
	let submitting = false;

	let subject = page.url.searchParams.get('subject') || "";

	async function submitQuestion() 
	{
		if (!projectname.trim() || !subject.trim() || !body.trim()) {
			if (!projectname.trim()) {
				error = "Project name is required.";
			} else if (!subject.trim()) {
				error = "Subject is required.";
			} else {
				error = "Question body is required.";
			}
			return;
		}

		error = "";
		submitting = true;

		let subjectId = subjectList.find(s => s.name === subject)?.id;
		if (!subjectId) {
			error = "Selected subject is invalid.";
			submitting = false;
			return;
		}

		try {
			const res = await fetch('/api/posts/create', 
			{
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify
				({projectname, subjectId, body})
			});

			if (res.ok) {
				goto('/posts');
			} else if (res.status === 401) {
				error = "You must be logged in to post a question.";
			} else {
				const data = await res.json();
				error = data?.message || "An error occurred while submitting your question.";
			}
		} finally {
			submitting = false;
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

	<div class="dropdown-group">
		<label for="subject-selector">Subject</label>
		<select
			class="black-text"
			name="subject"
			bind:value={subject}
		>
			<option value="" disabled>Select a subject</option>
			{#each subjectList as subjectOption}
				<option value={subjectOption.name}>{subjectOption.name}</option>
			{/each}
		</select>
	</div>

	<Textarea
		label="Question"
		name="body paragraph"
		placeholder="Write your question in detail here..."
		bind:value={body}
		rows={5}
	/>

	<button class="button primary" type="button" onclick={submitQuestion}>
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