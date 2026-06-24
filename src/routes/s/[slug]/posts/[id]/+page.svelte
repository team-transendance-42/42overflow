<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import CommentCard from '$lib/components/CommentCard.svelte';
	import EditPost from '$lib/components/EditPost.svelte';
	import CreateComment from '$lib/components/CreateComment.svelte';

	let { data } = $props() as any as { data: any };
	let post = data.post;
	let comments = $state<Comment[]>([]);
	let isOwn = $derived.by(() => page.data.user?.id === post?.user.id);

	onMount(() => {
		if (!post?.id) return;

		comments = data.post?.comments ?? [];

		const source = new EventSource(
			`/api/posts/${post.id}/comments/stream`
		);

		source.onmessage = (event) => {
			const data = JSON.parse(event.data);

			if (data.type === 'comment-create') {
				comments = [...comments, data.comment];
				return;
			}

			if (data.type === 'comment-update') {
				comments = comments.map(c =>
					c.id === data.comment.id ? data.comment : c
				);
				return;
			}

			if (data.type === 'like-update') {
				comments = comments.map(c =>
					c.id === data.commentId
						? { ...c, likeCount: data.likeCount, userLiked: data.userLiked }
						: c
				);
				return;
			}
		};

		return () => source.close();
	});

	async function deletePost() {
		if (!confirm('Are you sure you want to delete this post?')) {
			return;
		}
		const response = await fetch(`/api/posts/${post.id}/delete`, {
			method: 'POST',
		});

		if (!response.ok) {
			const errorData = await response.json();
			console.error('Failed to delete post:', errorData);
			alert('Failed to delete post: ' + (errorData.message || 'Unknown error'));
			return;
		}

		console.log(`Delete post with ID: ${post.id}`);
		// Refresh the page or remove the post from the UI
		window.location.reload();
	}

	let postId = $derived(post?.id ?? 0);

	function openProfile() {
        goto(`/profile/${post?.user.name}`);
    }
</script>

<div class=posts-page>
	<!-- Post with Comments -->
	{#if post}
		<div class="postbox white-text relative">

			<!-- Clickable area (nav to post page) -->
			{#if post.isEdited}
				<div class="break-all line-clamp-1"><em>[Edited]</em></div>
			{/if}
			<div class="break-all line-clamp-1"><strong>Project:</strong> {post.title}</div>
			<div class="break-all line-clamp-2"><strong>Question:</strong> {post.content}</div>

			<!-- Buttons -->
			<div class="comment-actions">

				<!-- View Profile Button -->
				{#if post.deleted_at == null}
					<button
						class="button postcard clickable"
						onclick={openProfile}
						aria-label="View {post.user.name}'s profile'"
					>
						<p class="author">
							Author: <em>{post.user.name}</em>
						</p>
					</button>
				{:else}
					<div class="button postcard">
						<p class="author">
							<em>[anonymous]</em>
						</p>
					</div>
				{/if}

				<!-- Edit Post -->
				{#if isOwn && post.deleted_at == null}
					<EditPost {postId} {post} />
				{/if}

				<!-- Delete Post -->
				{#if isOwn && post.deleted_at == null}
					<button
						class="button postcard delete clickable"
						onclick={(event) => {
							event.stopPropagation();
							deletePost();
						}}
						aria-label="Delete post"
					>
						Delete
					</button>
				{/if}
			</div>
		</div>

		<!-- Create Comment under Post -->
		<CreateComment {postId} />

		<!-- Show all Comments -->
		{#each comments as comment (comment.id)}
			<CommentCard {comment} />
		{/each}
	{/if}
</div>
