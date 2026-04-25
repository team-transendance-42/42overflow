<script lang="ts">
	import type { ComponentProps } from 'svelte';
    import { goto } from '$app/navigation';
	import CommentCard from '$lib/components/CommentCard.svelte';
	import CreateComment from '$lib/components/CreateComment.svelte';
	import CreateComment2 from '$lib/components/CreateComment2.svelte';

	type Comment = ComponentProps<typeof CommentCard>['comment'];

	let { data } = $props<{ data: any }>();
	let post = $derived(data.post);
	let comments = $derived<Comment[] | null>(data.post?.comments ?? []);

	function openProfile() {
        goto(`/profile/${post?.user.name}`);
    }
</script>

<!-- Post with Comments -->
<div>
	{#if post}
		<div class=postbox>
			<h2><strong>Project Name:</strong> {post.title}</h2>
			<p class="content"><strong>Question: </strong> {post.content}</p>

			<!-- View Profile Button -->
			<button
				class="bg-sky-500 hover:bg-sky-700"
				onclick={openProfile}
				aria-label="View {post.user.name}'s profile'"
			>
				<p class="author">
					Posted by: {post.user.name}
				</p>
			</button>
		</div>

		<CreateComment2 />

		{#each comments as comment}
			<CommentCard {comment} />
		{/each}
	{/if}
</div>
