const Urls = {
  login: "/auth/login",
  getIssues: "/api/issues",
  createIssue: "/api/issues",
  updateIssue: "/api/issues/$$issue_id$$",
  deleteIssue: "/api/issues/$$issue_id$$",
} as const;

export default Urls;
