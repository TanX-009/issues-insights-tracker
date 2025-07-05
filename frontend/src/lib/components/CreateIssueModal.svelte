<script lang="ts">
  import { goto } from "$app/navigation";
  import type { TIssue } from "$lib/types/issue";
  import handleResponse from "$lib/utils/response";
  import Modal from "./Modal.svelte";

  let { onsuccess } = $props();

  let error = $state("");

  let title = $state("");
  let description = $state("");

  let modalEl: Modal;
  export const open = () => {
    modalEl.open();
  };

  async function createIssue() {
    const res = await fetch("/api/issues", {
      method: "POST",
      body: JSON.stringify({ title, description }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const body = await res.json();

    const status = handleResponse<TIssue>(
      body,
      () => {
        modalEl.close();
        onsuccess();
      },
      (err) => {
        error = err.detail;
      },
    );
    if (status === 401) goto("/logout");
  }
</script>

<Modal bind:this={modalEl} onclose={() => (error = "")}>
  {#snippet header()}
    <h2 class="text-lg font-semibold">Create New Issue</h2>
  {/snippet}

  <form
    class="p-4 bg-surfaceContainer rounded-lg space-y-4"
    onsubmit={createIssue}
  >
    <input
      type="text"
      class="w-full p-2 rounded"
      placeholder="Issue title"
      bind:value={title}
      required
    />

    <textarea
      class="w-full p-2 rounded"
      placeholder="Description"
      bind:value={description}
      required
    ></textarea>

    <div class="flex justify-end gap-2">
      <button class="px-4 py-2 rounded" type="submit"> Create </button>
    </div>
    {#if error}
      <error>{error}</error>
    {/if}
  </form>
</Modal>
