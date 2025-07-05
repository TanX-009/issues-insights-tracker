<script lang="ts">
  let { header, children, onclose = () => {} } = $props();

  let dialog: HTMLDialogElement; // HTMLDialogElement

  export const close = () => {
    dialog.close();
  };

  export const open = () => {
    dialog.showModal();
  };
</script>

<dialog
  bind:this={dialog}
  onclose={() => {
    onclose();
    dialog.close();
  }}
  onclick={(e) => {
    if (e.target === dialog) dialog.close();
  }}
  class="mx-auto p-3 w-full h-full bg-[#00000088] text-onSurface"
>
  <div class="w-full h-full flex justify-center items-center">
    <div
      class="p-3 max-h-full overflow-y-auto border-none bg-surfaceContainer rounded"
    >
      <div class="flex justify-between flex-wrap-reverse gap-7">
        {@render header?.()}
        <!-- svelte-ignore a11y_autofocus -->
        <button class="low px-2" autofocus onclick={() => dialog.close()}
          >Close</button
        >
      </div>
      {@render children?.()}
    </div>
  </div>
</dialog>
