<script lang="ts">
  import { goto } from "$app/navigation";
  import { base } from "$app/paths";
  let email = "";
  let password = "";
  let message = "";

  async function login() {
    message = "";
    try {
      const res = await fetch(base + "/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (res.ok) {
        goto(base + "/");
      } else {
        const body = await res.json();
        message = body?.error?.detail || "Invalid credentials";
      }
    } catch (e) {
      message = e instanceof Error ? e.message : "Unknown error";
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
    {#if message}<div class="error">{message}</div>{/if}
    <button type="submit">Login</button>
  </form>
</div>
