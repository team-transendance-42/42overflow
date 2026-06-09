<script lang="ts">
  export let src: string = '';
  export let alt: string = 'Avatar';
  let broken = false;
</script>

<div class="avatar">
  {#if src && !broken}
    <img {src} {alt} on:error={() => broken = true} />
  {:else}
    <img src="/default-avatar.png" alt="default avatar" />
  {/if}
</div>
