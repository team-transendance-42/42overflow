<script lang="ts">
	import { page } from '$app/state';
	import { authClient } from '$lib/auth-client';

	export let user: any = null;

    let dropdownOpen = false;

	function isActive(path: string) {
        return (
            page.url.pathname === path ||
            page.url.pathname.startsWith(path + '/')
        );
    }

	function isOnProfilePage() {
		return page.url.pathname === '/profile';
	}

	async function handleLogout() {
		await authClient.signOut();
		window.location.reload();
	}
</script>

<header>
	<div class="left black-text">
   		<a href="/" >@42overflow</a>
	</div>

   <div class="right">
		{#if !user}
    		<a href="/settings" class="sidebar-link" class:active={isActive('/login')}>Log in</a>
		{:else}
			<div class="profile-row">
				<img
					src={user?.image ? user.image : '/default-avatar.png'}
					alt={user.name}
					class="header-avatar"
				/>

				<a href="/profile" class="sidebar-link" class:active={isOnProfilePage()}>
					{user.name}
				</a>

				<button
					class="dropdown-btn"
					class:active={dropdownOpen}
					on:click={() => (dropdownOpen = !dropdownOpen)}
				>
					{dropdownOpen ? '▾' : '▸'}
				</button>

				{#if dropdownOpen}
					<div class="dropdown-container">
						<a href="/settings" class="sidebar-link" class:active={isActive('/settings')}>Settings</a>
						<a href="/login" class="sidebar-link" on:click={handleLogout}>
							Log out
						</a>
					</div>
				{/if}
			</div>
		{/if}
	</div>
</header>
