<script lang=ts>
    import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import EditPost from './EditPost.svelte';

	let rawProps = $props() as { post: any, hasPermission: boolean };
    let post = $derived(rawProps.post);
	let postId = $derived(post.id);
	let isOwn = $derived.by(() => page.data.user?.id === post.user.id);
	let hasPermission = $derived(rawProps.hasPermission);

    function openPostPage() {
        goto(`/s/${post.subject.slug}/posts/${post.id}`);
    }

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

	function openProfile(event: Event) {
		// Prevent clicking 'openPostPage' button
        event.stopPropagation();
        goto(`/profile/${post.user.name}`);
    }
</script>

<div class="postbox clickable white-text relative">
    <!-- Clickable area (nav to post page) -->
    <div
        class="invisible-button clickable"
        role="button"
        tabindex="0"
        onclick={openPostPage}
        onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { openPostPage(); } }}
    >
		{#if post.isEdited}
			<div class="break-all line-clamp-1"><em>[Edited]</em></div>
		{/if}
        <div class="break-all line-clamp-1"><strong>Project:</strong> {post.title}</div>
        <div class="break-all line-clamp-2"><strong>Question:</strong> {post.content}</div>
    </div>

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
        {#if (isOwn || hasPermission) && post.deleted_at == null}
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
