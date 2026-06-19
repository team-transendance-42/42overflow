<script lang=ts>
    import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import EditPost from './EditPost.svelte';

	let rawProps = $props() as { post: any };
    let post = $derived(rawProps.post);
	let isOwn = $derived.by(() => page.data.user?.id === post.user.id);

    function openPostPage() {
        goto(`/posts/${post.id}`);
    }

	function openProfile(event: Event) {
		// Prevent clicking 'openPostPage' button
        event.stopPropagation();
        goto(`/profile/${post.user.name}`);
    }
</script>

<div
    class="invisible-button"
    role="button"
    tabindex="0"
    onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { openPostPage(); } }}
    onclick={openPostPage}
>
	<div class="postbox clickable white-text relative">
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
					onclick={deletePost}
					aria-label="Delete post"
				>
					Delete
				</button>
			{/if}
		</div>
  	</div>
</div>
