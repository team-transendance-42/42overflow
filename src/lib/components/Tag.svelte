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
  border: 1px solid #ccc;
  background: #f3f3f3;
}


.tag.memory {
  background: #e3f2fd;
  border-color: #64b5f6;
}

.tag.webserv {
  background: #e8f5e9;
  border-color: #81c784;
}

.remove {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
}
</style>