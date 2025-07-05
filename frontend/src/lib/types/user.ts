interface TUser {
  id: number;
  email: string;
  role: "ADMIN" | "MAINTAINER" | "REPORTER";
}

export type { TUser };
