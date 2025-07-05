<script lang="ts">
  import { onMount } from "svelte";
  import type { TUser } from "$lib/types/user";
  import handleResponse from "$lib/utils/response";
  import Modal from "$lib/components/Modal.svelte";
  import { goto } from "$app/navigation";

  let users: TUser[] = $state([]);
  let error = $state("");
  let modalError = $state("");

  let modalEl: Modal;
  let modalMode: "ADD" | "EDIT" | "DELETE" = $state("ADD");

  let id: TUser["id"] = $state(0);
  let email: TUser["email"] = $state("");
  let role: TUser["role"] = $state("REPORTER");
  let password: string = $state("");

  const roles: TUser["role"][] = ["REPORTER", "MAINTAINER", "ADMIN"];

  function openAddModal() {
    id = 0;
    email = "";
    role = "REPORTER";
    modalMode = "ADD";
    modalEl.open();
  }

  function openEditModal(user: TUser) {
    id = user.id;
    email = user.email;
    role = user.role;
    modalMode = "EDIT";
    modalEl.open();
  }

  function openDeleteModal(user: TUser) {
    id = user.id;
    email = user.email;
    modalMode = "DELETE";
    modalEl.open();
  }

  async function fetchUsers() {
    const res = await fetch("/api/users");
    const body = await res.json();

    handleResponse<TUser[]>(
      body,
      (data) => (users = data),
      (err) => (error = err.detail),
    );
  }

  async function saveUser(e: SubmitEvent) {
    e.preventDefault();
    const res = await fetch("/api/users", {
      method: id ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, email, role, password }),
    });
    const body = await res.json();

    const status = handleResponse<TUser>(
      body,
      () => {
        modalEl.close();
        fetchUsers();
      },
      (err) => (modalError = err.detail),
    );

    if (status === 401) goto("/logout");
  }

  async function deleteUser(e: SubmitEvent) {
    e.preventDefault();
    const res = await fetch("/api/users", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    const body = await res.json();

    const status = handleResponse<TUser>(
      body,
      () => {
        modalEl.close();
        fetchUsers();
      },
      (err) => (modalError = err.detail),
    );

    if (status === 401) goto("/logout");
  }

  onMount(fetchUsers);
</script>

<svelte:head>
  <title>Users</title>
</svelte:head>

<!-- Component -->
<div class="p-6 space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-bold text-primary">Users</h1>
    <button class="button med" onclick={openAddModal}>Add User</button>
  </div>

  {#if error}
    <div class="error">{error}</div>
  {:else}
    <div class="overflow-x-auto bg-surfaceContainer rounded">
      <table class="min-w-full text-sm text-left">
        <thead
          class="bg-primaryContainer text-primary uppercase tracking-wider"
        >
          <tr>
            <th class="px-4 py-2">ID</th>
            <th class="px-4 py-2">Email</th>
            <th class="px-4 py-2">Role</th>
            <th class="px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y">
          {#each users as user (user.id)}
            <tr class="hover:bg-surfaceContainerHigh">
              <td class="px-4 py-2">{user.id}</td>
              <td class="px-4 py-2">{user.email}</td>
              <td class="px-4 py-2">{user.role}</td>
              <td class="px-4 py-2 flex gap-2">
                <button class="low" onclick={() => openEditModal(user)}
                  >Edit</button
                >
                <button class="err" onclick={() => openDeleteModal(user)}
                  >Delete</button
                >
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    {#if users.length === 0}
      <p class="text-center text-secondary">No users found.</p>
    {/if}
  {/if}
</div>

<!-- Modal -->
<Modal bind:this={modalEl} onclose={() => ((modalError = ""), (password = ""))}>
  {#snippet header()}
    <h2 class="text-lg font-semibold">
      {modalMode === "ADD"
        ? "Add User"
        : modalMode === "EDIT"
          ? "Edit User"
          : "Delete User"}
    </h2>

    {#if modalError}
      <div class="error">{modalError}</div>
    {/if}
  {/snippet}

  {#if modalMode === "DELETE"}
    <form
      onsubmit={deleteUser}
      class="p-4 space-y-4 bg-surfaceContainer rounded"
    >
      <p>Are you sure you want to delete <strong>{email}</strong>?</p>
      <div class="flex justify-end gap-2">
        <button type="submit" class="err">Delete</button>
        <button type="button" class="low" onclick={() => modalEl.close()}
          >Cancel</button
        >
      </div>
    </form>
  {:else}
    <form onsubmit={saveUser} class="p-4 space-y-4 bg-surfaceContainer rounded">
      <input
        type="email"
        placeholder="Email"
        bind:value={email}
        class="w-full p-2 rounded"
        required
      />

      <input
        type="password"
        placeholder="Password"
        bind:value={password}
        class="w-full p-2 rounded"
        required
      />

      <select bind:value={role} class="w-full p-2 rounded">
        {#each roles as r (r)}
          <option value={r}>{r}</option>
        {/each}
      </select>

      <div class="flex justify-end gap-2">
        <button type="submit" class="px-4 py-2 rounded primary">
          {modalMode === "EDIT" ? "Update" : "Add"}
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded low"
          onclick={() => modalEl.close()}
        >
          Cancel
        </button>
      </div>
    </form>
  {/if}
</Modal>
