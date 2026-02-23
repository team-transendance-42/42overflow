<script lang="ts">
	import '$lib/styles/tokens.css';
	import { page } from '$app/state';
	import { locales, localizeHref } from '$lib/paraglide/runtime';
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import Footer from '$lib/components/Footer.svelte';
	import Header from '$lib/components/Header.svelte';
	import Navbar from '$lib/components/Navbar.svelte';

	let { children } = $props();
	
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<Header />
<Navbar />

<main>
{@render children()}

</main>


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
      min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  :global(main) {
    flex: 1;
  }

</style>

