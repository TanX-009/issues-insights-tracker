<script lang="ts">
  import { goto } from "$app/navigation";
  import type { TIssue } from "$lib/types/issue";
  import type { TUser } from "$lib/types/user";
  import handleResponse from "$lib/utils/response";
  import Modal from "./Modal.svelte";

  let { onsuccess, user }: { onsuccess: () => void; user: TUser } = $props();

  let error = $state("");

  let id: TIssue["id"] = $state(-0);
  let title: TIssue["title"] = $state("");
  let description: TIssue["description"] = $state("");
  let status: TIssue["status"] = $state("OPEN");
  let severity: TIssue["severity"] = $state("LOW");

  let deleting = $state(false);

  let modalEl: Modal;
  export const open = (issue: TIssue) => {
    title = issue.title;
    description = issue.description;
    status = issue.status;
    severity = issue.severity;
    id = issue.id;
    modalEl.open();
  };

  const severities: TIssue["severity"][] = [
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
  ];

  const statuses: TIssue["status"][] = [
    "OPEN",
    "IN_PROGRESS",
    "DONE",
    "TRIAGED",
  ];

  async function updateIssue(e: SubmitEvent) {
    e.preventDefault();

    const res = await fetch("/api/issues", {
      method: "PUT",
      body: JSON.stringify({
        title,
        description,
        severity,
        status,
        id: id,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const body = await res.json();

    const statusCode = handleResponse<TIssue>(
      body,
      () => {
        modalEl.close();
        onsuccess();
      },
      (err) => {
        error = err.detail;
      },
    );

    if (statusCode === 401) goto("/logout");
  }

  async function deleteIssue() {
    const res = await fetch("/api/issues", {
      method: "DELETE",
      body: JSON.stringify({ id }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const body = await res.json();

    const statusCode = handleResponse<TIssue>(
      body,
      () => {
        modalEl.close();
        onsuccess();
      },
      (err) => {
        error = err.detail;
      },
    );

    if (statusCode === 401) goto("/logout");
  }
</script>

<Modal
  bind:this={modalEl}
  onclose={() => {
    deleting = false;
    error = "";
  }}
>
  {#snippet header()}
    <h2 class="text-lg font-semibold">
      {#if deleting}
        Delete Issue
      {:else}
        Edit Issue
      {/if}
    </h2>
  {/snippet}

  {#if deleting}
    <form
      class="p-4 bg-surfaceContainer rounded-lg space-y-4"
      onsubmit={deleteIssue}
    >
      <h3>Do you really want to delete this issue?</h3>

      <div class="flex justify-center gap-3">
        <button class="px-4 py-2 rounded error" type="submit">Delete</button>
        <button class="px-4 py-2 rounded low" onclick={() => (deleting = false)}
          >Cancel</button
        >
      </div>
    </form>
  {:else}
    <form
      class="p-4 bg-surfaceContainer rounded-lg space-y-4"
      onsubmit={updateIssue}
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

      {#if user.role !== "REPORTER"}
        <div class="flex justify-between gap-2">
          <select id="severity" bind:value={severity} class="p-2 rounded w-1/2">
            {#each severities as s (s)}
              <option value={s}>{s}</option>
            {/each}
          </select>

          <select id="status" bind:value={status} class="p-2 rounded w-1/2">
            {#each statuses as s (s)}
              <option value={s}>{s.replaceAll("_", " ")}</option>
            {/each}
          </select>
        </div>
      {/if}

      <div class="flex justify-end gap-3">
        {#if user.role === "ADMIN"}
          <button
            class="px-4 py-2 rounded error"
            onclick={() => (deleting = true)}>Delete</button
          >
        {/if}
        <button class="px-4 py-2 rounded" type="submit">Save</button>
      </div>
    </form>
  {/if}
  {#if error}
    <div class="error">{error}</div>
  {/if}
</Modal>
