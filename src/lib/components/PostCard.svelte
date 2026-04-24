<script lang=ts>
	import Postbox from '$lib/components/Postbox.svelte';
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
	<Postbox>
		<h2><strong>Project Name:</strong> {post.title}</h2>
		<p class="content"><strong>Question: </strong> {post.content}</p>

		<!-- View Profile Button -->
		<button
			class="bg-sky-500 hover:bg-sky-700"
			onclick={openProfile}
			aria-label="View {post.user.name}'s profile'"
		>
			{#if post.user?.name}
				<p class="author">
					Posted by: {post.user.name}
				</p>
			{/if}
		</button>
  	</Postbox>
</div>
