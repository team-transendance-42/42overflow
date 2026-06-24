<script lang="ts">
    import { page } from '$app/state';

    export let width = "140px";
    export let userRole: 'USER' | 'MODERATOR' | 'ADMIN' | null = null;
	export let memberships: { subject: { name: string; slug: string } }[] = [];

    let dropdownOpen = false;

    $: canSeeUsersLink =
        userRole === 'MODERATOR' || userRole === 'ADMIN';

    function isActive(path: string) {
        return (
            page.url.pathname === path ||
            page.url.pathname.startsWith(path + '/')
        );
    }
</script>


<aside class="sidebar" style="width: {width};">
	<slot />
	<div class="top-links">
		<a href="/posts" class="sidebar-link" class:active={isActive('/posts')}>Posts</a>

		<div class="subjects-row">
			<a href="/subjects" class="sidebar-link" class:active={isActive('/subjects')}>Subjects</a>
			<button
				class="dropdown-btn"
				class:active={dropdownOpen}
				on:click={() => (dropdownOpen = !dropdownOpen)}
			>
				{dropdownOpen ? '▾' : '▸'}
				<i class="fa fa-caret-down"></i>
			</button>
		</div>
		<div class="dropdown-container" style="display: {dropdownOpen ? 'block' : 'none'}">
			{#each memberships as membership}
				<a href={`/s/${membership.subject.slug}`}
					class="sidebar-link"
					class:active={isActive(`/s/${membership.subject.slug}`)}>
					{membership.subject.name}
				</a>
			{/each}
		</div>

		<a href="/post-question" class="sidebar-link" class:active={isActive('/post-question')}>Post Question</a>
		<a href="/ai-assist" class="sidebar-link" class:active={isActive('/ai-assist')}>AI Assist</a>
		{#if canSeeUsersLink}
			<a href="/users" class="sidebar-link" class:active={isActive('/users')}>Users</a>
		{/if}
	</div>
</aside>
