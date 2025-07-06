<script lang="ts">
  import { onMount } from "svelte";
  import { Chart, registerables } from "chart.js";
  import { goto } from "$app/navigation";
  import { browser } from "$app/environment";
  import Modal from "$lib/components/Modal.svelte";
  import type { TIssue } from "$lib/types/issue";
  import type { TStat } from "$lib/types/stat";
  import handleResponse from "$lib/utils/response";
  import type { TUser } from "$lib/types/user";
  import { truncateText } from "$lib/utils/string";
  import { env } from "$env/dynamic/public";
  import Urls from "$lib/api/urls";
  import Markdown from "svelte-exmarkdown";
  import { PUBLIC_API_URL, PUBLIC_SSE_URL } from "$env/static/public";
  import Sun from "$lib/components/icons/Sun.svelte";
  import Moon from "$lib/components/icons/Moon.svelte";

  Chart.register(...registerables);

  const { data } = $props<{ data: { user: TUser; token: string } }>();

  let theme: "dark" | "light" = $state("light");

  let eventSource: EventSource | null = null;
  let issues: TIssue[] = $state([]);
  let error = $state("");
  let chart: Chart | null = null;
  let canvasEl: HTMLCanvasElement | null = $state(null);

  let stats: TStat[] = $state([]);

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
        (err) => (error = err?.detail || "Unknown error"),
      );

      if (status === 401) goto("/logout");
    } catch (e) {
      error = e instanceof Error ? e.message : "Unknown error";
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch("/api/stats");
      if (!res.ok) {
        error = `Failed to fetch issues: ${res.status} ${res.statusText}`;
        return;
      }

      const response = await res.json();
      const status = handleResponse<TStat[]>(
        response,
        (res) => (stats = res),
        (err) => (error = err?.detail || "Unknown error"),
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
  let file_path: TIssue["file_path"] = $state("");

  let file: File | null = null;
  let fileEl: HTMLInputElement | null = $state(null);

  function applyTheme(t: "light" | "dark") {
    const root = document.documentElement;
    root.setAttribute("data-theme", t);
    theme = t;
  }

  function toggleTheme() {
    applyTheme(theme === "dark" ? "light" : "dark");
  }

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
    file_path = issue.file_path;
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
    file = null;
    file_path = "";
    if (fileEl) fileEl.value = "";

    modalError = "";
  };

  async function saveIssue(e: SubmitEvent) {
    e.preventDefault();

    if (modalMode === "CREATE") {
      const formData = new FormData();
      formData.append("title", title);
      formData.append("description", description);
      formData.append("severity", severity);
      formData.append("status", status);
      if (file) formData.append("file", file);

      const res = await fetch("/api/issues", {
        method: "POST",
        body: formData,
      });

      const body = await res.json();
      const code = handleResponse<TIssue>(
        body,
        () => {
          modalEl.close();
          fetchIssues();
        },
        (err) => (modalError = err?.detail || "Unknown error!"),
      );
      if (code === 401) goto("/logout");
    } else {
      const res = await fetch("/api/issues", {
        method: "PUT",
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
    const prefersDark = window.matchMedia?.(
      "(prefers-color-scheme: dark)",
    ).matches;
    applyTheme(prefersDark ? "dark" : "light");
  });

  onMount(() => {
    if (!browser) return;
    fetchIssues();

    if (data.user.role === "ADMIN") {
      fetchStats();
    }

    if (["REPORTER", "MAINTAINER", "ADMIN"].includes(data.user.role)) {
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
      {/if}
      <button
        class="low flex items-center justify-center gap-1 px-2.5 h-full"
        onclick={toggleTheme}
        aria-label={theme === "light" ? "Light" : "Dark"}
      >
        {#if theme === "light"}
          <Sun />
        {:else}
          <Moon />
        {/if}
      </button>
      {#if data.user.role === "ADMIN"}
        <a class="button low" href="/users">Users</a>
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

          {#if data.user.role === "ADMIN" && stats.length > 0}
            <div
              class="flex items-center justify-between flex-wrap gap-0 bg-primaryContainer w-full rounded overflow-hidden"
            >
              <h3
                class="text-xl font-bold px-2 py-1 flex items-center shadow text-primary"
              >
                Daily stats
              </h3>

              <div class="flex flex-wrap">
                {#each stats as stat (stat.id)}
                  <div
                    class={` px-2 py-1 flex justify-between items-center gap-4 shadow ${getStatusColor(stat.status)}`}
                  >
                    <div class="text-sm font-medium">
                      {stat.status.replace("_", " ")}
                    </div>
                    <div class="text-xl font-bold">{stat.count}</div>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
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
                      class={`inline-block px-2 py-1 rounded text-xs text-nowrap font-medium ${getStatusColor(issue.status)}`}
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
        {#if modalMode === "CREATE"}
          <label for="file">Attach File</label>
          <input
            bind:this={fileEl}
            id="file"
            class="w-full"
            type="file"
            accept="*/*"
            onchange={(e) => {
              const target = e.target as HTMLInputElement;
              if (target?.files?.length) {
                file = target.files[0];
              }
            }}
          />
        {:else if modalMode === "EDIT" && file_path}
          <div
            class="flex justify-between w-full bg-secondary text-onSecondary rounded overflow-hidden"
          >
            <span class="py-0.5 px-3 overflow-hidden"
              >{file_path.replace("uploads/", "")}</span
            >
            <a
              href={`${PUBLIC_SSE_URL}/${file_path}`}
              target="_blank"
              download
              class="py-0.5 px-3 bg-primaryContainer text-primary h-full"
            >
              Download
            </a>
          </div>
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
        <h3>Description markdown preview</h3>
        <Markdown md={description} />
      </div>
    </div>
  {/if}
</Modal>
