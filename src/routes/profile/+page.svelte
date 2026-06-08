<script lang="ts">
  import Avatar from '$lib/components/Avatar.svelte';

  export let data;
  const user = data.user;
  //const profile = data.profile;

  let firstname = data.user?.name?.split(' ')[0] ?? '';
  let lastname = data.user?.name?.split(' ')[1] ?? '';
  let email = data.user?.email ?? '';
  let interests = data.profile?.interests ?? '';
  let intraprofile = data.profile?.login ?? '';
  let campus = data.profile?.campus ?? '';
  let previewUrl = data.user?.image ?? '';
  let error = '';
  let success = false;
  let loading = false;

  let fileInput: HTMLInputElement;

  function handleFileChange(e: Event) {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (file) previewUrl = URL.createObjectURL(file);

  }

  function removeAvatar() {
  previewUrl = '';
  if (fileInput) fileInput.value = ''; // reset the input
}

  async function handleUpdate() {
    error = '';
    success = false;
    loading = true;

    const { error: err } = await authClient.updateUser({
      name: `${firstname} ${lastname}`.trim(),
      image: previewUrl || '',
    });

    loading = false;

    if (err) {
      error = err.message ?? 'Could not update profile';
      return;
    }

    success = true;
  }
</script>

<div class="profile-page">
  <div class="avatar-section">
    <Avatar src={user?.image ?? ''} size="80px" />
  </div>


  <h1><strong>Name: </strong> {user?.first_name ?? 'No name set'} {user?.last_name ?? 'No name set'} </h1>
 
  {#if user?.name}
    <p class="username"><strong>Username: </strong> {user.name}</p>
  {/if}

 <p class="email"><strong>Email:</strong> {user?.email}</p>

  {#if user?.interests}
    <div class="section">
      <p><strong>Interests</strong>: {user.interests}</p>
    </div>
  {/if}


    {#if user?.followers?.length > 0}
    <div class="interests">
      <span class="label"><strong>Following:</strong></span>
      {#each user.followers as f}
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
  	color: var(--color-primary-dark-400);
 }

  
</style>