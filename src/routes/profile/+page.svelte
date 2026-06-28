<script lang="ts">
	import Avatar from '$lib/components/Avatar.svelte';

	export let data;
	const user = data.user;
</script>

<div class="profile-page">
	<div class="avatar-section">
		<Avatar src={user?.image ?? ''}/>
	</div>

	<h1><strong>Name: </strong> {user?.first_name ?? '<first name>'} {user?.last_name ?? '<last name>'} </h1>

	{#if user?.name}
		<p class="username"><strong>Username: </strong> {user.name}</p>
	{/if}

	<p class="email"><strong>Email:</strong> {user?.email}</p>

	{#if user?.interests}
		<div class="section">
			<p>
				<strong>Interests</strong>
				:{user.interests}
			</p>
		</div>
	{/if}


	{#if user?.followers?.length > 0}
		<div class="interests">
			<span class="label">
				<strong>Following:</strong>
			</span>

			{#each user.followers as f}
				<div class="following-row">
					<img
						src={f?.image ? f.image : '/default-avatar.png'}
						alt={f.name}
						class="following-avatar"
					/>
					<a href="/profile/{f.following.name}" class="following-link">
						{f.following.name}
					</a>
				</div>
			{/each}
		</div>
	{/if}
</div>
