<script lang="ts">
  import SubjectBox from '$lib/components/SubjectBox.svelte';
  import { page } from '$app/stores';
  import type { PageData } from './$types';

  export let data: PageData;

  function hrefFor(pageNum: number) {
    const params = new URLSearchParams($page.url.searchParams as any);
    params.set('page', String(pageNum));
    return `${$page.url.pathname}?${params.toString()}`;
  }
</script>

<div class="subjects-container">
  <h1>Subjects</h1>
  
  {#if data.subjects.length > 0}
    <div class="subject-grid">
      {#each data.subjects as subject (subject.id)}
        <SubjectBox subject={subject} isLoggedIn={data.isLoggedIn} />
      {/each}
    </div>

    <div class="pagination" aria-label="Pagination">
      {#if data.currentPage > 1}
        <a class="btn" href={hrefFor(data.currentPage - 1)}>Prev</a>
      {:else}
        <button class="btn" disabled aria-disabled="true">Prev</button>
      {/if}

      <span class="page-info"> - Page {data.currentPage} - </span>

      {#if data.currentPage < data.totalPages}
        <a class="btn" href={hrefFor(data.currentPage + 1)}>Next</a>
      {:else}
        <button class="btn" disabled aria-disabled="true">Next</button>
      {/if}
    </div>
  {:else}
    <p>No subjects found.</p>
  {/if}
</div>

<style>
  .subjects-container {
    padding: 1rem;
  }

  .subject-grid {
    display: grid;
	flex-direction: column;
    /* grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); */
    gap: 1.5rem;
    margin-top: 2rem;
  }

  .pagination {
    margin-top: 2rem;
    text-align: center;
  }

  .btn {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    margin: 0 0.5rem;
    background: transparent;
    border: none;
    color: inherit;
    font: inherit;
    cursor: pointer;
    text-decoration: none;
  }

  .btn[disabled], .btn[aria-disabled="true"] {
    opacity: 0.5;
    pointer-events: none;
    cursor: default;
  }

  .page-info {
    margin: 0 0.5rem;
    font-weight: 600;
  }
</style>