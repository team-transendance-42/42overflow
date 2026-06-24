<script lang="ts">
	import { page } from '$app/state';
	import { authClient } from '$lib/auth-client';
	import { goto } from '$app/navigation';

	export let user: any = null;

    let dropdownOpen = false;

	function isActive(path: string) {
        return (
            page.url.pathname === path ||
            page.url.pathname.startsWith(path + '/')
        );
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

				<a href="/profile" class="sidebar-link" class:active={isActive('/profile')}>
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

<style>

	.dropdown-container {
		position: absolute;
		top: 100%;
		right: 0;
		background: var(--color-primary-400);
		border: 1px solid #ccc;
		border-radius: var(--radius-md);
		min-width: 150px;
		z-index: 1000;
	}

	header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		background-color: var(--color-primary-400);
		color: var(--color-neutral-900);
		font-size: var(--font-size-medium);
		font-weight: bold;
		padding: var(--space-sm) var(--space-lg);
		border-bottom: 2px solid var(--color-neutral-100);
	}

	header .right {
		color: rgb(0, 0, 0, 0.5);
		display: block;
	}

	header .right a {
		text-decoration: none;
		color: inherit;
		margin-right: var(--space-sm);
	}

	header .right a.active {
		text-decoration: none;
		color: black;
		margin-right: var(--space-sm);
	}

	.profile-row {
		display: flex;
		align-items: center;
		position: relative;
	}

	.settings-link {
		display: inline-flex;
		align-items: center;
		color: inherit;
		vertical-align: middle;
		margin-bottom: 2px;
		font-weight: bold;
	}

	.header-avatar {
		width: 30px;
		height: 30px;
		border-radius: 50%;
		margin-left: var(--space-sm);
		margin-right: var(--space-sm);
	}
</style>
