const Urls = {
  login: "/auth/login",

  issuesEvent: "/api/issues/events",

  getIssues: "/api/issues/",
  createIssue: "/api/issues/",
  updateIssue: "/api/issues/$$issue_id$$",
  deleteIssue: "/api/issues/$$issue_id$$",

  getUsers: "/users/",
  createUser: "/users/",
  updateUser: "/users/$$user_id$$",
  deleteUser: "/users/$$user_id$$",
} as const;

export default Urls;
