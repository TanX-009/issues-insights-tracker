<script lang="ts">
  import { onMount } from "svelte";
  import { Chart, registerables } from "chart.js";
  import { goto } from "$app/navigation";
  import { browser } from "$app/environment";
  import Modal from "$lib/components/Modal.svelte";
  import type { TIssue } from "$lib/types/issue";
  import handleResponse from "$lib/utils/response";
  import type { TUser } from "$lib/types/user";
  import { truncateText } from "$lib/utils/string";
  import { env } from "$env/dynamic/public";
  import Urls from "$lib/api/urls";
  import Markdown from "svelte-exmarkdown";

  Chart.register(...registerables);

  const { data } = $props<{ data: { user: TUser; token: string } }>();

  let eventSource: EventSource | null = null;
  let issues: TIssue[] = $state([]);
  let error = $state("");
  let chart: Chart | null = null;
  let canvasEl: HTMLCanvasElement | null = $state(null);

  const severityOrder: TIssue["severity"][] = [
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

  const fetchIssues = async () => {
    try {
      const res = await fetch("/api/issues");
      if (!res.ok) {
        error = `Failed to fetch issues: ${res.status} ${res.statusText}`;
        return;
      }

      const response = await res.json();
      const status = handleResponse<TIssue[]>(
        response,
        (res) => (issues = res),
        (err) => (error = err.detail),
      );

      if (status === 401) goto("/logout");
    } catch (e) {
      error = e instanceof Error ? e.message : "Unknown error";
    }
  };

  const groupOpenIssuesBySeverity = (issues: TIssue[]) => {
    const grouped: Record<string, number> = {
      LOW: 0,
      MEDIUM: 0,
      HIGH: 0,
      CRITICAL: 0,
    };
    issues.forEach((issue) => {
      grouped[issue.severity]++;
    });
    return severityOrder.map((s) => grouped[s]);
  };

  const getSeverityColor = (severity: TIssue["severity"]) =>
    ({
      LOW: "text-blue-500",
      MEDIUM: "text-yellow-500",
      HIGH: "text-orange-500",
      CRITICAL: "text-red-500",
    })[severity] ?? "text-gray-700";

  const getStatusColor = (status: TIssue["status"]) =>
    ({
      OPEN: "bg-green-100 text-green-800",
      TRIAGED: "bg-yellow-100 text-yellow-800",
      IN_PROGRESS: "bg-blue-100 text-blue-800",
      DONE: "bg-gray-200 text-gray-700",
    })[status] ?? "bg-gray-100 text-gray-600";

  const sortIssues = (a: TIssue, b: TIssue) =>
    severityOrder.indexOf(b.severity) - severityOrder.indexOf(a.severity);

  // Modal state
  let modalEl: Modal;
  let modalMode: "CREATE" | "EDIT" | "DELETE" = $state("CREATE");
  let modalError = $state("");

  let id: TIssue["id"] = $state(0);
  let title: TIssue["title"] = $state("");
  let description: TIssue["description"] = $state("");
  let severity: TIssue["severity"] = $state("LOW");
  let status: TIssue["status"] = $state("OPEN");

  const openCreateModal = () => {
    modalMode = "CREATE";
    id = 0;
    title = "";
    description = "";
    severity = severity;
    status = "OPEN";
    modalEl.open();
  };

  const openEditModal = (issue: TIssue) => {
    modalMode = "EDIT";
    id = issue.id;
    title = issue.title;
    description = issue.description;
    severity = issue.severity;
    status = issue.status;
    modalEl.open();
  };

  const openDeleteModal = () => {
    modalMode = "DELETE";
    modalEl.open();
  };

  const onCloseModal = () => {
    id = 0;
    title = "";
    description = "";
    severity = "LOW";
    status = "OPEN";

    modalError = "";
  };

  async function saveIssue(e: SubmitEvent) {
    e.preventDefault();
    const res = await fetch("/api/issues", {
      method: id !== 0 ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, title, description, severity, status }),
    });
    const body = await res.json();
    const code = handleResponse<TIssue>(
      body,
      () => {
        modalEl.close();
        fetchIssues();
      },
      (err) => (modalError = err.detail),
    );
    if (code === 401) goto("/logout");
  }

  async function deleteIssue(e: SubmitEvent) {
    e.preventDefault();
    const res = await fetch("/api/issues", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    const body = await res.json();
    const code = handleResponse<TIssue>(
      body,
      () => {
        modalEl.close();
        fetchIssues();
      },
      (err) => (modalError = err.detail),
    );
    if (code === 401) goto("/logout");
  }

  onMount(() => {
    if (!browser) return;
    fetchIssues();

    if (["MAINTAINER", "ADMIN"].includes(data.user.role)) {
      if (data.token) {
        eventSource = new EventSource(
          `${env.PUBLIC_SSE_URL}${Urls.issuesEvent}?token=${data.token}`,
        );

        eventSource.onmessage = (event) => {
          const message = event.data;
          console.log("SSE:", message);
          fetchIssues(); // refresh issue list and chart
        };

        eventSource.onerror = (err) => {
          console.error("SSE error:", err);
          eventSource?.close();
        };
      }
    }

    return () => {
      chart?.destroy();
      eventSource?.close();
    };
  });

  $effect(() => {
    if (!canvasEl || issues.length === 0) return;

    const data = groupOpenIssuesBySeverity(issues);

    if (chart) {
      chart.data.datasets[0].data = data;
      chart.update();
    } else {
      chart = new Chart(canvasEl, {
        type: "bar",
        data: {
          labels: severityOrder,
          datasets: [
            {
              label: "Open Issues",
              data,
              backgroundColor: ["#2b7fff", "#f0b100", "#ff6900", "#fb2c36"],
              borderRadius: 6,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, ticks: { stepSize: 1, precision: 0 } },
          },
        },
      });
    }
  });
</script>

<svelte:head>
  <title>Dashboard - Issue Tracker</title>
</svelte:head>

<div class="p-3 md:p-5 space-y-8">
  <div class="flex justify-between flex-wrap">
    <h1 class="text-3xl font-bold text-primary">Issues & Insights Tracker</h1>
    <div class="flex gap-3 flex-wrap items-center">
      {#if data.user}
        <div class="p-0 flex gap-0">
          <span
            class="bg-secondaryContainer text-secondary rounded-l px-3 py-1.5"
          >
            {data.user.role}
          </span>
          <span
            class="bg-surfaceContainerHigh text-secondary rounded-r px-3 py-1.5"
            >{data.user.email}</span
          >
        </div>
        {#if data.user.role === "ADMIN"}
          <a class="button low" href="/users">Users</a>
        {/if}
      {/if}
      <a class="button med" href="/logout">Logout</a>
    </div>
  </div>

  {#if error}
    <div class="error">
      {error}
    </div>
  {:else}
    <div class="flex justify-between items-center mb-0">
      <h2 class="text-xl font-semibold">Open Issues by Severity</h2>
      <button onclick={openCreateModal}>New Issue</button>
    </div>
    <div
      class="rounded-xl p-3 md:p-5 min:w-fit w-full mx-auto flex flex-col 2xl:flex-row justify-center items-center 2xl:items-start gap-8"
    >
      {#if issues.length > 0}
        <div
          class="flex flex-row flex-wrap justify-between gap-6 max-w-[600px] w-full h-fit 2xl:sticky top-10"
        >
          <div class="p-6 w-full rounded bg-surfaceContainer">
            <canvas bind:this={canvasEl} class="w-full h-full"></canvas>
          </div>

          <div class="py-1 px-3 w-full flex justify-center gap-3 flex-wrap">
            {#each severityOrder as severity, index (index)}
              <div>
                <span class="font-semibold {getSeverityColor(severity)}">
                  {severity}
                </span>
                <span class="px-2 py-1 rounded-md text-l">
                  {groupOpenIssuesBySeverity(issues)[
                    severityOrder.indexOf(severity)
                  ]}
                </span>
              </div>
            {/each}
            <div>
              <span class="font-semibold text-tertiary"> TOTAL </span>
              <span class="px-2 py-1 rounded-md text-l">
                {issues.length}
              </span>
            </div>
          </div>
        </div>

        <div
          class="h-fit max-w-fit w-full bg-surfaceContainer rounded overflow-hidden overflow-x-auto"
        >
          <table class="w-full text-sm text-left">
            <thead
              class="bg-primaryContainer text-primary uppercase tracking-wide"
            >
              <tr>
                <th class="px-4 py-2">ID</th>
                <th class="px-4 py-2">Title</th>
                {#if data.user.role !== "REPORTER"}
                  <th class="px-4 py-2">User</th>
                  <th class="px-4 py-2">Role</th>
                {/if}
                <th class="px-4 py-2">Severity</th>
                <th class="px-4 py-2">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <!-- FIX: Create a shallow copy before sorting to avoid mutating state directly -->
              {#each [...issues].sort(sortIssues) as issue (issue.id)}
                <tr
                  class="hover:bg-surfaceContainerHigh cursor-pointer"
                  onclick={() => {
                    openEditModal(issue);
                  }}
                >
                  <td class="px-4 py-2">{issue.id}</td>
                  <td class="px-4 py-2">{truncateText(issue.title, 20)}</td>
                  {#if data.user.role !== "REPORTER"}
                    <th class="px-4 py-2"
                      >{truncateText(
                        issue.reporter ? issue.reporter.email : "Deleted user",
                        20,
                      )}</th
                    >
                    <th class="px-4 py-2"
                      >{issue.reporter ? issue.reporter.role : "NULL"}</th
                    >
                  {/if}
                  <td
                    class="px-4 py-2 font-semibold {getSeverityColor(
                      issue.severity,
                    )}"
                  >
                    {issue.severity}
                  </td>
                  <td class="px-4 py-2">
                    <span
                      class={`inline-block px-2 py-1 rounded text-xs font-medium ${getStatusColor(issue.status)}`}
                    >
                      {issue.status.replace("_", " ")}
                    </span>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {:else}
        <p class="p-3 w-full text-center text-primary">No issues!</p>
      {/if}
    </div>
  {/if}
</div>

<!-- Modal -->
<Modal bind:this={modalEl} onclose={onCloseModal}>
  {#snippet header()}
    <h2 class="text-lg font-semibold">
      {modalMode === "CREATE"
        ? "Create Issue"
        : modalMode === "EDIT"
          ? "Edit Issue"
          : "Delete Issue"}
    </h2>
    {#if modalError}<div class="error">{modalError}</div>{/if}
  {/snippet}

  {#if modalMode === "DELETE"}
    <form
      onsubmit={deleteIssue}
      class="space-y-4 p-4 bg-surfaceContainer rounded"
    >
      <p>Are you sure you want to delete <strong>{title}</strong>?</p>
      <div class="flex justify-end gap-2">
        <button class="err" type="submit">Delete</button>
        <button class="low" type="button" onclick={() => modalEl.close()}
          >Cancel</button
        >
      </div>
    </form>
  {:else}
    <div class="flex flex-col lg:flex-row relative">
      <form
        onsubmit={saveIssue}
        class="space-y-4 max-w-xl w-full h-fit p-4 sticky top-0 bg-surfaceContainer rounded"
      >
        <label for="title">Title</label>
        <input
          id="title"
          class="w-full"
          type="text"
          placeholder="Title"
          bind:value={title}
          required
        />
        <label for="description">Description</label>
        <textarea
          id="description"
          class="w-full mb-0"
          placeholder="Description"
          bind:value={description}
          required
        ></textarea>
        {#if data.user.role !== "REPORTER"}
          {#if modalMode === "EDIT"}
            <label for="severity">Severity</label>
            <select
              id="severity"
              class="w-full p-2 rounded"
              bind:value={severity}
            >
              {#each severityOrder as s, index (index)}<option value={s}
                  >{s}</option
                >{/each}
            </select>
            <label for="status">Status</label>
            <select id="status" class="w-full p-2 rounded" bind:value={status}>
              {#each statuses as s (s)}<option value={s}
                  >{s.replace("_", " ")}</option
                >{/each}
            </select>
          {/if}
        {/if}
        <div class="flex justify-end gap-2">
          {#if data.user.role === "ADMIN" && modalMode !== "CREATE"}
            <button class="err" onclick={openDeleteModal}>Delete</button>
          {/if}
          <button class="" type="submit">
            {modalMode === "EDIT" ? "Save" : "Create"}
          </button>
        </div>
      </form>
      <div class="prose prose-neutral dark:prose-invert max-w-xl w-full">
        <Markdown md={description} />
      </div>
    </div>
  {/if}
</Modal>
