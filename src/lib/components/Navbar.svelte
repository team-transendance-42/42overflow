<!-- src/lib/components/navbar.svelte -->

<navbar>

  <div class="left">
    <a href="/questions">Questions | </a>
	  <a href="/post-question">Post Question</a>
  </div>

  <div class="right">
    <a href="/log-in">Log-In | </a>
    <a href="/settings">Settings</a>
  </div>

</navbar>



<style>
navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-xxs) var(--space-lg);
  background-color: var(--color-neutral-100);
  color: var(--color-neutral-900);
  font-weight: bold;
 
  
  border-bottom: 1px solid var(--color-neutral-900); /* standard 1px border */
  border-top: 1px solid var(--color-neutral-900);    /* top border */

}
</style>