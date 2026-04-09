<script lang="ts">
  import Input from '$lib/components/Input.svelte';
  import Button from '$lib/components/Button.svelte';
  import { authClient } from '$lib/auth-client';
  import { goto } from '$app/navigation';

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

    goto('/profile');
  }
</script>

<div class="log-in-page">
  <h1>42Overflow</h1>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <Input label="Email" name="email" placeholder="Enter email" bind:value={email} />
  <Input label="Password" name="password" placeholder="Enter password" bind:value={password} />

  <Button label={loading ? 'Logging in...' : 'Log In'} type="button" onClick={handleLogin} />

  <p>Don't have an account? <a href="/signup">Sign up</a></p>
</div>

<style>
  .log-in-page { width: 100%; max-width: 400px; padding: 0; text-align: left; }
  .error { color: red; font-size: 0.875rem; }
</style>