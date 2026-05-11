<script lang="ts">
  export let text = "";
  export let category = "default";
  export let removable = false;
  export let onRemove = null;
</script>

<span class="tag {category}">
  {text}

  {#if removable}
    <button class="remove" on:click={onRemove}>×</button>
  {/if}
</span>

<style>
.tag {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  font-size: 0.8rem;
  border: 1px solid var(--color-primary-dark-300);
  background: var(--color-neutral-200);
}

.tag.memory {
  background: var(--color-neutral-200);
  border-color:ar(--color-neutral-100);
}

.tag.webserv {
  background: var(--color-neutral-200);
  border-color: var(--color-neutral-150);
}

.remove {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
}
</style>