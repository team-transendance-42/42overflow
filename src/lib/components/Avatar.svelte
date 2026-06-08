<script lang="ts">
  export let src: string = '';
  export let size: string = '50px';
  export let alt: string = 'Avatar';
  let broken = false;

</script>

<div class="avatar" style="width: {size}; height: {size};">

{#if src && !broken}
  <img {src} {alt} on:error={() => broken = true} />
{:else}
  <img src="/default-avatar.png" alt="default avatar" />
{/if}
</div>

<style>
  .avatar {
    border-radius: 50%;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

  }

  .avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

</style>  