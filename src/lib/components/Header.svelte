<script lang="ts">
	import Settingsicon from '$lib/components/Settingsicon.svelte';
	export let user: { name?: string | null, email?: string } | null = null;
</script>

<header>
	<div class="left">
   		<a href="/" >@42overflow</a>
	</div>

	

   <div class="right">

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
    font-family: var(--font-family-base);
    font-size: var(--font-size-medium);
	font-weight: bold;
    padding: var(--space-sm) var(--space-lg);
   
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


