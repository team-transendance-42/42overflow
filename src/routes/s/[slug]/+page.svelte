<script lang="ts">
	import {page} from '$app/stores';
	import type { ComponentProps } from 'svelte';
	import PostCard from '$lib/components/PostCard.svelte';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let { data } = $props();

	type Post = ComponentProps<typeof PostCard>['post'];
	
	let title = $state('');
	let content = $state('');
	let message = '';
	let error = '';

	let questions: Post[] = $state([]);
	let currentPage = $state(1);
	let limit = 5;
	let total = 0;

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		message = '';
		error = '';

		const res = await fetch(`/api/subjects/${$page.params.slug}/post`, {
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify({ title, content })
		});

		await loadSubject();
	}

	async function loadSubject() {
		const res = await fetch(`/api/subjects/${$page.params.slug}/post?page=${currentPage}&limit=${limit}`);
		const json = await res.json();

		if (!res.ok) {
			error = json.error || 'An error occurred while loading posts.';
			return;
		}

		questions = (json.data ?? []) as Post[];
		total = json.total;
		title = '';
		content = '';
	};

	function makePost() {
		goto(`/post-question?subject=${data.subject.name}`);
	}

	onMount(loadSubject);		

</script>

<!-- Posts -->
<div>
	<h1><strong>
		NEWEST QUESTIONS
	</strong></h1>

	{#each questions as post}
		<PostCard {post} />
	{/each}
</div>

<!-- Pagination -->
<div>
	<button onclick={() => {
		if (currentPage > 1) {
			currentPage--;
			loadSubject();
		}
	}}>
	Prev
	</button>

	<span> - Page {currentPage} -</span>

	<button onclick={() => {
		if (currentPage * limit < total) {
			currentPage++;
			loadSubject();
		}
	}}>
	Next
	</button>
</div>

<div>
	<button class="button primary" onclick={makePost}>Create Post</button>
</div>
