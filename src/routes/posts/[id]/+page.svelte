<script lang="ts">
	import { goto } from '$app/navigation';
	import CommentCard from '$lib/components/CommentCard.svelte';
	import CreateComment from '$lib/components/CreateComment.svelte';

	// Define types for post and comments
	type Comment = {
		id: number;
		content: string;
		image?: string | null;
		likes: number;
		created_at: Date | string;
		user: { name: string; id: string; };
		children?: Comment[];
	};
	type Post = {
		id: number;
		title: string;
		content: string;
		user: { name: string; };
		comments?: Comment[];
	};

	// Get data from props with inline type
	interface PageData {
		post: Post | null;
	}

	let { data } = $props() as any as { data: PageData };
	let post = $derived(data.post);
	let comments = $derived<Comment[] | null>(data.post?.comments ?? []);

	let postId = $derived(post?.id ?? 0);

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

		<!-- Create Comment under Post -->
		<CreateComment {postId} />

		<!-- Show all Comments -->
		{#each comments as comment}
			<CommentCard {comment} />
		{/each}
	{/if}
</div>
