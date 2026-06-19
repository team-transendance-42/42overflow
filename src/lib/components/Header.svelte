<script lang="ts">
	import Settingsicon from '$lib/components/Settingsicon.svelte';
	export let user = null;
</script>

<header>
	<div class="left black-text">
   		<a href="/" >@42overflow</a>
	</div>

   <div class="right black-text">

		{#if !user}
    	<a href="/login">Log-In | </a>
		{/if}
		<a href="/profile">Profile  </a>
		<a href="/settings" class="settings-link">
		<Settingsicon size="15px" />  </a>

		<p> Welcome{user ? `, ${user.name}` : ''} </p>

	</div>
	
</header>

<style>
  header {
	display: flex;                
  	justify-content: space-between; 
  	align-items: center;         
    background-color: var(--color-primary-400);
    color: var(--color-neutral-900);
    font-size: var(--font-size-medium);
	font-weight: bold;
    padding: var(--space-sm) var(--space-lg);
	border-bottom: 2px solid var(--color-neutral-100);
  }

  header .right {
	font-size: 0.85rem; 
	font-weight: normal;
  }

  .settings-link {
    display: inline-flex;
    align-items: center;
    color: inherit;
	vertical-align: middle; 
  	margin-bottom: 2px; 
	font-weight: bold;
	
  }
</style>
