<script>
  export let width = "140px";
</script>


<aside class="sidebar" 
style="width: {width};">
  <slot />
  <div class="top-links">
    <a href="/questions">Questions</a>
    <a href="/post-question">Post Question</a>
    <a href="/ai-assist">AI Assist</a>
  </div>
</aside>


<style>
  .sidebar {
    background-color: var(--color-neutral-200);
    color: black;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
	font-weight: bold;
	font-size: 0.8rem; /* <-- smaller font */
  }
</style>


