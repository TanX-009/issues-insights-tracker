<script lang="ts">
  import { onMount } from "svelte";
  import { Chart, registerables } from "chart.js";
  import { goto } from "$app/navigation";
  import { browser } from "$app/environment";
  import type { TIssue } from "$lib/types/issue";
  import handleResponse from "$lib/utils/response";
  import type { TUser } from "$lib/types/user";
  import CreateIssueModal from "$lib/components/CreateIssueModal.svelte";
  import { truncateText } from "$lib/utils/string";
  import IssueModal from "$lib/components/IssueModal.svelte";

  Chart.register(...registerables);

  const { data } = $props<{
    data: {
      user: TUser;
    };
  }>();

  let issues: TIssue[] = $state([]);
  let error = $state("");

  let issueModalEl: IssueModal | null = $state(null);
  let createIssueModalEl: CreateIssueModal | null = $state(null);

  let chart: Chart | null = null;
  let canvasEl: HTMLCanvasElement | null = $state(null);

  const severityOrder: TIssue["severity"][] = [
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
  ];

  const fetchIssues = async () => {
    try {
      const res = await fetch("/api/issues");

      if (!res.ok) {
        return {
          issues: [],
          error: `Failed to fetch issues: ${res.status} ${res.statusText}`,
        };
      }

      const response = await res.json();

      const status = handleResponse<TIssue[]>(
        response,
        (res) => {
          issues = res;
        },
        (err) => {
          error = err.detail;
        },
      );
      if (status === 401) goto("/logout");
    } catch (e) {
      error = e instanceof Error ? e.message : "Unknown error occurred";
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
      if (issue.status === "OPEN") {
        grouped[issue.severity] = (grouped[issue.severity] || 0) + 1;
      }
    });

    return severityOrder.map((severity) => grouped[severity] || 0);
  };

  const renderChart = () => {
    const counts = groupOpenIssuesBySeverity(issues);

    if (canvasEl) {
      if (chart) {
        chart.destroy();
      }
      chart = new Chart(canvasEl, {
        type: "bar",
        data: {
          labels: severityOrder,
          datasets: [
            {
              label: "Open Issues",
              data: counts,
              backgroundColor: ["#2b7fff", "#f0b100", "#ff6900", "#fb2c36"],
              borderRadius: 6,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1, precision: 0 },
            },
          },
        },
      });
    }
  };

  const getSeverityColor = (severity: TIssue["severity"]) => {
    return (
      {
        LOW: "text-blue-500",
        MEDIUM: "text-yellow-500",
        HIGH: "text-orange-500",
        CRITICAL: "text-red-500",
      }[severity] ?? "text-gray-700"
    );
  };

  const getStatusColor = (status: TIssue["status"]) => {
    return (
      {
        OPEN: "bg-green-100 text-green-800",
        TRIAGED: "bg-yellow-100 text-yellow-800",
        IN_PROGRESS: "bg-blue-100 text-blue-800",
        DONE: "bg-gray-200 text-gray-700",
      }[status] ?? "bg-gray-100 text-gray-600"
    );
  };

  function sortIssues(a: TIssue, b: TIssue) {
    return (
      severityOrder.indexOf(b.severity) - severityOrder.indexOf(a.severity)
    );
  }

  function onIssueOpen(issue: TIssue) {
    issueModalEl?.open(issue);
  }

  onMount(() => {
    if (!browser) return;

    fetchIssues();

    // const interval = setInterval(async () => {
    //   await invalidate("page");
    // }, 10000);

    return () => {
      // clearInterval(interval);
      chart?.destroy();
    };
  });

  $effect(() => {
    if (canvasEl && issues.length > 0 && !chart) {
      renderChart();
    }
  });

  $effect(() => {
    if (chart && issues) {
      const updated = groupOpenIssuesBySeverity(issues);
      chart.data.datasets[0].data = updated;
      chart.update();
    }
  });
</script>

<svelte:head>
  <title>Dashboard - Issue Tracker</title>
</svelte:head>

<CreateIssueModal bind:this={createIssueModalEl} onsuccess={fetchIssues} />

<IssueModal bind:this={issueModalEl} onsuccess={fetchIssues} user={data.user} />

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
    <error>
      {error}
    </error>
  {:else}
    <div class="flex justify-between items-center mb-0">
      <h2 class="text-xl font-semibold">Open Issues by Severity</h2>
      <button onclick={() => createIssueModalEl?.open()}>New Issue</button>
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
                    onIssueOpen(issue);
                  }}
                >
                  <td class="px-4 py-2">{issue.id}</td>
                  <td class="px-4 py-2">{truncateText(issue.title, 20)}</td>
                  {#if data.user.role !== "REPORTER"}
                    <th class="px-4 py-2"
                      >{truncateText(issue.reporter.email, 20)}</th
                    >
                    <th class="px-4 py-2">{issue.reporter.role}</th>
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
