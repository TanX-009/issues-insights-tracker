import type { TIssue } from "./issue";

interface TStat {
  id: number;
  status: TIssue["status"];
  date: string;
  count: number;
}

export type { TStat };
