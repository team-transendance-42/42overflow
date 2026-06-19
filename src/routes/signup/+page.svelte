<script lang="ts">
  import Input from '$lib/components/Input.svelte';
  import { authClient } from '$lib/auth-client';
  import { goto } from '$app/navigation';

  let email = '';
  let password = '';
  let name = '';
  let error = '';
  let loading = false;

  async function handleSignup() {
    error = '';

	if (!email.trim() || !password.trim() || !name.trim()) {
    error = 'All fields are required';
    return;
  }
    loading = true;

    const { data, error: err } = await authClient.signUp.email({
      email,
      password,
      name,
    });

    loading = false;

    if (err) {
      error = err.message ?? 'Could not create account';
      return;
    }

    window.location.href = '/profile';
  }
</script>

<div class="sign-up-page">
  <h1>42Overflow</h1>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <Input label="Username" name="name" placeholder="Enter Username" bind:value={name} />
  <Input label="Email" name="email" placeholder="Enter email" bind:value={email} />
  <Input label="Password" name="password" placeholder="Enter password" type="password" bind:value={password} />

  <button class="button primary" type="button" on:click={handleSignup}>
    {loading ? 'Creating account...' : 'Sign Up'}
  </button>

  <p>Already have an account? <a href="/login"><strong>Log in</strong></a></p>
</div>

<style>
  .sign-up-page { width: 100%; max-width: 400px; padding: 0; text-align: left; }
  .error { color: var(--color-error-250); font-size: 0.875rem; }
</style>


