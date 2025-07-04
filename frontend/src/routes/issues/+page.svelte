<script lang="ts">
  import type { TIssue } from "$lib/types/issue";

  export let data: {
    issues: TIssue[];
    error?: string;
  };
</script>

<h1>Issues</h1>

{#if data.error}
  <p class="text-red-600">⚠️ {data.error}</p>
{:else if data.issues.length === 0}
  <p>No issues found.</p>
{:else}
  <ul>
    {#each data.issues as issue (issue.id)}
      <li>{issue.title} — {issue.severity}</li>
    {/each}
  </ul>
{/if}
