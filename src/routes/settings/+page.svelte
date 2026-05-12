<script lang="ts">
  import { authClient } from '$lib/auth-client';
  import { goto } from '$app/navigation';

  async function handleLogout() {
    await authClient.signOut();
    goto('/login');
  }

</script>


<div class="settings-page">
  <h1><strong>SETTINGS</strong></h1>


  <p> Preferences</p>
  
<div class="editprofile">
   		<a href="edit-profile">Edit Profile </a>
	</div>

</div>


<button on:click={handleLogout}>Log out</button>

<style>
  .settings-page {
    width: 100%;
    max-width: 800px;
    padding: 0rem;
    text-align: left;
  }
</style>

