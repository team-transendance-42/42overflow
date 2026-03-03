<script lang="ts">
	import '$lib/styles/tokens.css';
	import { page } from '$app/state';
	import { locales, localizeHref } from '$lib/paraglide/runtime';
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import Footer from '$lib/components/Footer.svelte';
	import Header from '$lib/components/Header.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	let { children } = $props();
	
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<Header />

<div class="content">
	<Sidebar />

	<main>
		{@render children()}
	</main>
</div>

<Footer />


<div style="display:none">
	{#each locales as locale}
		<a href={localizeHref(page.url.pathname, { locale })}>
			{locale}
		</a>
	{/each}
</div>

<style>

:global(body) {
  margin: 0;
  background-color: var(--color-neutral-500);
  color: var(--color-neutral-900);
  font-family: var(--font-family-base);
   
  }

  .content {
		display: grid;
		grid-template-columns: 150px 1fr;
		min-height: calc(100vh -  /* header + nav height */ 120px);
	}

	main {
		padding: 2rem;
	}

 
</style>

