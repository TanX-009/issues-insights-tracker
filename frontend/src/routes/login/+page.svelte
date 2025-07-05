<script lang="ts">
  import { goto } from "$app/navigation";
  let email = "";
  let password = "";
  let message = "";

  async function login() {
    message = "";
    const res = await fetch("/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (res.ok) {
      goto("/");
    } else {
      const body = await res.json();
      message = body?.error?.detail || "Invalid credentials";
    }
  }
</script>

<div class="flex flex-col justify-center items-start h-lvh">
  <form
    on:submit|preventDefault={login}
    class="p-5 w-fit max-w-3xl mx-auto rounded flex flex-col gap-5 justify-center items-center bg-surfaceContainer"
  >
    <h1 class="text-2xl">Login</h1>
    <input bind:value={email} placeholder="Email" />
    <input type="password" bind:value={password} placeholder="Password" />
    {#if message}<error>{message}</error>{/if}
    <button type="submit">Login</button>
  </form>
</div>
