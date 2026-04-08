<!-- src/lib/components/header.svelte -->

<script>
	import Settingsicon from '$lib/components/Settingsicon.svelte';
</script>

<header>
	<div class="left">
   		<a href="/" >@42overflow</a>
	</div>

   <div class="right">
    	<a href="/login">Log-In | </a>
    	<a href="/profile" class="profile-link">Profile </a>
		<a href="/settings" class="settings-link">
		<Settingsicon size="15px" />  </a>

		
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

.profile-link {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem; /* small gap between text and icon */
  text-decoration: none;
  color: inherit;
}

  .settings-link {
    display: inline-flex;
    align-items: center;
    color: inherit;
	vertical-align: middle;  /* add this */
  	margin-bottom: 2px; 
	font-weight: bold;
	
  }



</style>


