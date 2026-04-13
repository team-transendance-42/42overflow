<script lang="ts">
  import Avatar from '$lib/components/Avatar.svelte';
  import { enhance } from '$app/forms';

  export let data;

  const { profile, user, isFollowing, followerCount, followingCount, isOnline, isOwnProfile } = data;
</script>

<div class="profile-page">
  <div class="avatar-row">
    <div class="avatar-wrap">
      <Avatar src={user?.image ?? ''} size="100px" />
      <span class="status-dot {isOnline ? 'online' : 'offline'}"></span>
    </div>

    <div class="info">
      <h1>{user?.name ?? 'No name set'}</h1>
      <p class="online-text">{isOnline ? 'Online' : 'Offline'}</p>
      <div class="counts">
        <span><strong>{followerCount}</strong> followers</span>
        <span><strong>{followingCount}</strong> following</span>
      </div>
    </div>
  </div>

  {#if !isOwnProfile}
    <form method="POST" action="?/follow" use:enhance>
      <button type="submit" class="follow-btn {isFollowing ? 'following' : ''}">
        {isFollowing ? 'Unfollow' : 'Follow'}
      </button>
    </form>
  {:else}
    <a href="/edit-profile" class="edit-btn">Edit profile</a>
  {/if}

  {#if profile?.quote}
    <p class="quote">"{profile.quote}"</p>
  {/if}

  {#if profile?.interests}
    <div class="section">
      <span class="label">Interests</span>
      <p>{profile.interests}</p>
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
  .avatar-row { display: flex; gap: 1rem; align-items: center; margin: 1rem 0; }
  .avatar-wrap { position: relative; display: inline-block; }
  .status-dot {
    position: absolute;
    bottom: 4px;
    right: 4px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    border: 2px solid white;
  }
  .status-dot.online { background: #22c55e; }
  .status-dot.offline { background: #888; }
  .info { display: flex; flex-direction: column; gap: 4px; }
  h1 { margin: 0; }
  .online-text { font-size: 0.8rem; color: var(--color-text-secondary); margin: 0; }
  .counts { display: flex; gap: 1rem; font-size: 0.875rem; color: var(--color-text-secondary); }
  .email { color: var(--color-text-secondary); font-size: 0.875rem; margin: 0 0 1rem; }
  .quote { font-style: italic; color: var(--color-text-secondary); margin: 1rem 0; }
  .section { margin: 0.75rem 0; }
  .label { font-size: 0.75rem; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }
  .follow-btn {
    padding: 6px 20px;
    border-radius: var(--border-radius-md);
    border: 0.5px solid var(--color-border-secondary);
    background: black;
    color: white;
    cursor: pointer;
    font-size: 0.875rem;
    margin-bottom: 1rem;
  }
  .follow-btn.following {
    background: transparent;
    color: var(--color-text-primary);
  }
  .edit-btn {
    display: inline-block;
    margin-bottom: 1rem;
    font-size: 0.875rem;
    padding: 6px 14px;
    border: 0.5px solid var(--color-border-secondary);
    border-radius: var(--border-radius-md);
    text-decoration: none;
    color: var(--color-text-primary);
  }
</style>