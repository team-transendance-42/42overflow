<script lang="ts">
  import Avatar from '$lib/components/Avatar.svelte';

  export let data;
  const user = data.user;
  const profile = data.profile;

</script>

<div class="profile-page">
  <div class="avatar-section">
    <Avatar src={user?.image ?? ''} size="80px" />
  </div>


  <h1><strong>Name: </strong> {user?.first_name ?? 'No name set'} {user?.last_name ?? 'No name set'} </h1>

  <h1><strong>Username: </strong> {user?.name ?? 'No name set'}</h1>
 
  {#if profile?.username}
    <p class="username"><strong>Username: </strong> {profile.username}</p>
  {/if}

 <p class="email"><strong>Email:</strong> {user?.email}</p>

  {#if profile?.interests}
    <div class="section">
      <p><strong>Interests</strong>: {profile.interests}</p>
    </div>
  {/if}


    {#if profile?.followers?.length > 0}
    <div class="interests">
      <span class="label"><strong>Following:</strong></span>
      {#each profile.followers as f}
	    <div class="following-row">
	    <Avatar src={f.following.image ?? ''} size="36px" />
        <a href="/profile/{f.following.name}" class="following-link">
          {f.following.name}
        </a>
		</div>
      {/each}
	</div>
  {/if}


</div>

<style>

  .profile-page { 
	width: 100%; 
	max-width: 490px; 
	padding: 0; 
	text-align: 
	left; }

  .avatar-section { 
	margin: 1rem 0;  }


  .interests { 
	margin: 0.75rem 0; }

  .label { 
	font-size: 0.75rem; 
	color: var(--color-text-secondary); 
	text-transform: uppercase; 
	letter-spacing: 0.05em; }
  

  .following-row {	
	display: flex;
  	align-items: center;
  	gap: 0.5rem;
	margin: 0.4rem 0;
 }

  .following-link:hover {
    text-decoration: underline;}

  .following-link {
  	color: #a5c11a;
 }

  
</style>