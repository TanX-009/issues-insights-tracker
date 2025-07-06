import type { TUser } from "./user";

interface TIssue {
  title: string;
  description: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  id: number;
  status: "OPEN" | "TRIAGED" | "IN_PROGRESS" | "DONE";
  file_path: string | null;
  reporter: TUser | null;
}

export type { TIssue };
