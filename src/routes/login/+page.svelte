<script lang="ts">
  import Input from '$lib/components/Input.svelte';
  import { authClient } from '$lib/auth-client';
  import { goto, invalidateAll } from '$app/navigation';

  let email = '';
  let password = '';
  let error = '';
  let loading = false;

  async function handleLogin() {
    error = '';
    loading = true;

    const { data, error: err } = await authClient.signIn.email({
      email,
      password,
    });

    loading = false;

    if (err) {
      error = err.message ?? 'Invalid email or password';
      return;
    }
	await invalidateAll();
    window.location.href = '/profile';
  }
</script>

<div class="log-in-page">
  <h1>42Overflow</h1>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <Input label="Email" name="email" placeholder="Enter email" bind:value={email} />
  <Input label="Password" name="password" placeholder="Enter password" type="password" bind:value={password} />

  <button class="button primary" type="button" on:click={handleLogin}>
    {loading ? 'Logging in...' : 'Log In'}
  </button>

  <p>Don't have an account? <a href="/signup"><strong>Sign up</strong></a></p>
</div>

<style>
  .log-in-page { width: 100%; max-width: 400px; padding: 0; text-align: left; }
  .error { color: var(--color-error-250); font-size: 0.875rem; }
</style>