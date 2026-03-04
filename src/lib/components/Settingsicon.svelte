<script lang="ts">
  export let size: string = '30px'; // icon size
</script>


<div class="settings-icon" style="width: {size}; height: {size};" on:click={onClick}>
  <span></span>
  <span></span>
  <span></span>
</div>

<style>
.settings-icon {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
  height: 100%;
}

.settings-icon span {
  display: block;
  height: 2px;
  background-color: var(--color-neutral-900);
  margin: 2px 0;
  border-radius: 1px;
}
</style>