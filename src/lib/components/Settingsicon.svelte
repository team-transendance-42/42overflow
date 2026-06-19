<script lang="ts">
  export let size: string = '30px'; 
  export let onClick = () => {};
</script>


<button class="settings-icon" style="width: {size}; height: {size};" onclick={onClick} aria-label="Settings">
  <span></span>
  <span></span>
  <span></span>
</button>

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
  background-color: black;
  margin: 2px 0;
  border-radius: 1px;
}
</style>
