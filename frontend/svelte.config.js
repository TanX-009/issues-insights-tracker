import adapter from "@sveltejs/adapter-node";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";
import { config } from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

// Determine mode: "development", "production", etc.
const mode = process.env.NODE_ENV || "development";

// Load corresponding .env file
config({
  path: path.resolve(
    path.dirname(fileURLToPath(import.meta.url)),
    `.env.${mode}`,
  ),
});

const dev = mode === "development";
const base = dev ? "" : process.env.BASE_PATH || "";

/** @type {import('@sveltejs/kit').Config} */
export default {
  preprocess: vitePreprocess(),
  kit: {
    paths: {
      base,
    },
    adapter: adapter({ out: "build" }),
  },
};
