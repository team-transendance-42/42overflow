<script lang=ts>
    import { goto } from '$app/navigation';

	let rawProps = $props() as { post: any };
    let post = $derived(rawProps.post);

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

		<!-- View Profile Button -->
		<button
			class="button postcard clickable absolute bottom-2 left-2"
			onclick={openProfile}
			aria-label="View {post.user.name}'s profile'"
		>
			<p class="author">
				Author: <em>{post.user.name}</em>
			</p>
		</button>
  	</div>
</div>
