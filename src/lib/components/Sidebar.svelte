<script lang="ts">
  export let width = "140px";
  export let userRole: 'USER' | 'MODERATOR' | 'ADMIN' | null = null;

  $: canSeeUsersLink = userRole === 'MODERATOR' || userRole === 'ADMIN';
</script>


<aside class="sidebar" style="width: {width};">
	<slot />
	<div>
		<a href="/posts">View Posts</a>
		<a href="/post-question">Post Question</a>
		<a href="/ai-assist">AI Assist</a>
		{#if canSeeUsersLink}
			<a href="/users">Users</a>
		{/if}
	</div>
</aside>

<style>
.sidebar {
	background-color: var(--color-neutral-200);
	color: black;
	padding: 1.5rem;
	display: flex;
	flex-direction: column;
	gap: 1rem;
	font-weight: bold;
	font-size: 0.8rem;
	border-right: 2px solid var(--color-neutral-100);
}
</style>