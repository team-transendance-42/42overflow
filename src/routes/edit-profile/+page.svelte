<script lang="ts">
  import Button from '$lib/components/Button.svelte';
  import Input from '$lib/components/Input.svelte';
  import Avatar from '$lib/components/Avatar.svelte';
  import { authClient } from '$lib/auth-client';

  export let data;

  let firstname = data.user?.first_name ?? '';
  let lastname = data.user?.last_name ?? '';
  let email = data.user?.email ?? '';
  let interests = data.user?.interests ?? '';
  let username = data.user?.name ?? '';
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

  const formData = new FormData();
  formData.append('interests', interests);
  formData.append('username', username);
  formData.append('firstname', firstname);
  formData.append('lastname', lastname);
  if (fileInput?.files?.[0]) {
    formData.append('avatarimage', fileInput.files[0]);
  }

  const res = await fetch('?/update', {
    method: 'POST',
    body: formData,
  });

  const text = await res.text();
  try {
    const json = JSON.parse(text);
    if (json?.data?.imageUrl) previewUrl = json.data.imageUrl;
  } catch {}

  loading = false;

  if (!res.ok) {
    error = 'Could not update profile';
    return;
  }

  success = true;
}

</script>

<form method="POST" action="?/update" use:enhance enctype="multipart/form-data">
<div class="profile-page">
  <h1><strong>PROFILE PAGE</strong></h1>

  {#if error}
    <p class="error">{error}</p>
  {/if}
  {#if success}
    <p class="success">Profile updated!</p>
  {/if}

  <div class="avatar-wrapper">
    <Avatar src={previewUrl} size="80px" />
    <label class="upload-btn">
      <strong>Upload avatar</strong>
      <input type="file" name="avatarimage" accept="image/*" bind:this={fileInput} on:change={handleFileChange} />
    </label>
    {#if previewUrl}
      <button type="button" class="remove-btn" on:click={removeAvatar}>
        <strong>Remove avatar</strong>
      </button>
    {/if}
  </div>

  <div class="name-row">
    <Input label="First Name" name="firstname" placeholder="First" bind:value={firstname} />
    <Input label="Last Name" name="lastname" placeholder="Last" bind:value={lastname} />
  </div>
  <Input label="User name" name="username" placeholder="User name" bind:value={username} />

  <Input label="E-mail" name="email" placeholder="E-mail" bind:value={email} disabled  />

  <Input label="Interests" name="interests" placeholder="Interests" bind:value={interests} />

  <Button label={loading ? 'Saving...' : 'Update'} type="button" onClick={handleUpdate} />
</div>
</form>

<style>
  .avatar-wrapper { margin: 0.5rem 0; display: flex; flex-direction: column; gap: 0.5rem; }
  .profile-page { width: 100%; max-width: 490px; padding: 0; text-align: left; }
  .name-row { display: flex; gap: 1rem; }
  .name-row :global(.input-wrapper) { flex: 1; }
  .error { color: red; font-size: 0.875rem; }
  .success { color: green; font-size: 0.875rem; }

  .upload-btn {
  cursor: pointer;
  font-size: 0.875rem;
  border: 0.5px solid var(--color-border-secondary);
  border-radius: var(--border-radius-md);
  display: inline-block;
}

.upload-btn input {
  display: none;
}

.remove-btn  {
  cursor: pointer;
  font-size: 0.875rem;
  border: 0.5px solid var(--color-border-secondary);
  border-radius: var(--border-radius-md);
  display: flex;
}

.remove-btn input {
  display: none;
}

.file-hint {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

</style>