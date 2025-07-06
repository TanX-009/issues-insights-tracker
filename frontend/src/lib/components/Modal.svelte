<script lang="ts">
  let { header, children, onclose = () => {} } = $props();

  let dialog: HTMLDialogElement; // HTMLDialogElement
  let container: HTMLDivElement; // HTMLDialogElement

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
    if (e.target === dialog || e.target === container) {
      onclose();
      dialog.close();
    }
  }}
  class="p-3 w-full h-full mx-auto bg-transparent backdrop:bg-[#00000088] text-onSurface"
>
  <div
    bind:this={container}
    class="w-full h-full flex justify-center items-center"
  >
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
