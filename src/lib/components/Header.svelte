<!-- src/lib/components/header.svelte -->

<script>
	import Settingsicon from '$lib/components/Settingsicon.svelte';
</script>

<header>
	<div class="left">
   		<a href="/" >@42overflow</a>
	</div>

   <div class="right">
    	<a href="/log-in">Log-In | </a>
    	<a href="/profile" class="profile-link">
		Profile </a>
	
		<Settingsicon size="15px" on:click={() => alert('Settings clicked!')} /> 
	</div>
	
</header>


<style>
  header {
	display: flex;                 /* make left/right horizontal */
  	justify-content: space-between; /* push right to far side */
  	align-items: center;           /* vertically center both sides */
    background-color: var(--color-primary-400);
    color: var(--color-neutral-900);
    font-family: var(--font-family-base);
    font-size: var(--font-size-medium);
	font-weight: bold;
    padding: var(--space-sm) var(--space-lg);
   
  }

  /* Right side smaller */
header .right {
  font-size: 0.85rem; /* smaller font */
  font-weight: normal;
}

.profile-link {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem; /* small gap between text and icon */
  text-decoration: none;
  color: inherit;
}



</style>


