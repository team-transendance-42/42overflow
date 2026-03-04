<script lang="ts">
  export let src: string = '';       // image URL
  export let size: string = '50px';  // diameter
  export let alt: string = 'Avatar'; // alt text
</script>

<div class="avatar" style="width: {size}; height: {size};">
  {#if src}
    <img src={src} alt={alt} />
  {:else}
    <span>👤</span> <!-- placeholder icon -->
  {/if}
  <img src={src} alt={alt} on:error={(e) => e.currentTarget.style.display='none'} />
</div>

<style>
.avatar {
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-neutral-300);
  flex-shrink: 0; /* don’t shrink if used in a flex row */
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar span {
  font-size: calc(var(--font-size-medium) * 1.2);
}
</style>