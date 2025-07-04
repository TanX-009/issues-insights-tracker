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
      goto("/issues");
    } else {
      const body = await res.json();
      message = body?.error?.detail || "Invalid credentials";
    }
  }
</script>

<form on:submit|preventDefault={login} class="space-y-4">
  <input bind:value={email} placeholder="Email" />
  <input type="password" bind:value={password} placeholder="Password" />
  {#if message}<p class="text-red-500">{message}</p>{/if}
  <button type="submit">Login</button>
</form>
