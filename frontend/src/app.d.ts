// See https://svelte.dev/docs/kit/types#app.d.ts

import type { TUser } from "$lib/types/user";

// for information about these interfaces
declare global {
  namespace App {
    // interface Error {}
    interface Locals {
      token?: string;
      user?: {
        id: string;
        email: string;
        role: TUser["role"];
      };
    }
    // interface PageData {}
    // interface PageState {}
    // interface Platform {}
  }
}

export {};
