<div class="postbox">
  <slot></slot>
</div>

<style>
.postbox {
  width: 100%;
  min-height: 150px;   /* controls rectangle height */
  background-color: var(--color-neutral-100);
  border: 1px solid var(--color-neutral-500);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  margin-bottom: var(--space-lg);
}
</style>