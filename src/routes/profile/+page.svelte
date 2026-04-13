<script lang="ts">
  import Avatar from '$lib/components/Avatar.svelte';

  export let data;

  const user = data.user;
  const profile = data.profile;
</script>

<div class="profile-page">
  <div class="avatar-section">
    <Avatar src={user?.image ?? ''} size="100px" />
  </div>

  <h1>Name: {user?.name ?? 'No name set'}</h1>
  <p class="email">Email: {user?.email}</p>

  {#if profile?.quote}
    <p class="quote">Favorite Quote: "{profile.quote}"</p>
  {/if}

  {#if profile?.interests}
    <div class="section">
      <p>Interests: {profile.interests}</p>
    </div>
  {/if}

  {#if profile?.login}
    <div class="section">
      <span class="label">Intra</span>
      <p>{profile.login}</p>
    </div>
  {/if}

</div>

<style>
  .profile-page { width: 100%; max-width: 490px; padding: 0; text-align: left; }
  .avatar-section { margin: 1rem 0; }
  h1 { margin: 0.5rem 0 0.25rem; }
  .email { color: var(--color-text-secondary); font-size: 0.875rem; margin: 0 0 1rem; }
  .quote { font-style: italic; color: var(--color-text-secondary); margin: 1rem 0; }
  .section { margin: 0.75rem 0; }
  .label { font-size: 0.75rem; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }
  .edit-btn {
    display: inline-block;
    margin-top: 1.5rem;
    font-size: 0.875rem;
    border: 0.5px solid var(--color-border-secondary);
    border-radius: var(--border-radius-md);
    text-decoration: none;
    color: var(--color-text-primary);
  }
</style>