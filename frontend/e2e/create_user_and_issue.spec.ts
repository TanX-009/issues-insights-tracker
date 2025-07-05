import { test, expect } from "@playwright/test";

test("Admin creates a user, user creates issue, admin triages", async ({
  page,
}) => {
  // Login as admin
  await page.goto("/login");
  await page.getByPlaceholder("Email").fill("admin@email.com");
  await page.getByPlaceholder("Password").fill("admin");
  await page.getByRole("button", { name: "Login" }).click();
  await expect(page).toHaveURL("/");

  // Go to users page
  await page.getByRole("link", { name: "Users" }).click();
  await expect(page).toHaveURL("/users");

  // Delete test user if already exists
  const userRow = page.locator("td", { hasText: "test@email.com" });
  const userRows = await userRow.count();
  console.log(userRows);
  if (userRows) {
    const deleteButton = userRow.getByRole("button", { name: "Delete" });
    await deleteButton.click(); // open delete confirmation modal
    await page.getByRole("button", { name: "Delete" }).click(); // confirm delete
    await expect(userRow).toHaveCount(userRows - 1); // ensure it's gone
  }

  // Add new user
  await page.getByRole("button", { name: "Add User" }).click();
  await page.getByPlaceholder("Email").fill("test@email.com");
  await page.getByPlaceholder("Password").fill("test");
  await page.getByRole("combobox").selectOption("REPORTER");
  await page.getByRole("button", { name: "Add", exact: true }).click();
  await expect(page).toHaveURL("/users");

  // Go back to dashboard
  await page.getByRole("link", { name: "Dashboard" }).click();
  await expect(page).toHaveURL("/");

  // Logout as admin
  await page.getByRole("link", { name: "Logout" }).click();
  await expect(page).toHaveURL("/login");

  // Login as test user
  await page.getByPlaceholder("Email").fill("test@email.com");
  await page.getByPlaceholder("Password").fill("test");
  await page.getByRole("button", { name: "Login" }).click();

  // Create a new issue
  await page.getByRole("button", { name: "New Issue" }).click();
  await page.getByPlaceholder("Title").fill("Sample Bug Report");
  await page
    .getByPlaceholder("Description")
    .fill("Steps to reproduce bug X...");
  await page.getByRole("button", { name: "Create" }).click();

  // Confirm issue was created
  await expect(
    page.locator("td", { hasText: "Sample Bug Report" }),
  ).toContainText("Sample Bug Report");

  // Logout test user
  await page.getByRole("link", { name: "Logout" }).click();
  await expect(page).toHaveURL("/login");

  // Login again as admin
  await page.getByPlaceholder("Email").fill("admin@email.com");
  await page.getByPlaceholder("Password").fill("admin");
  await page.getByRole("button", { name: "Login" }).click();

  // Edit newly created issue
  const issueRow = page.locator("td", { hasText: "Sample Bug Report" });
  await issueRow.click();

  // Change severity and status
  await page.getByRole("combobox", { name: "LOW" }).selectOption("HIGH");
  await page
    .getByRole("combobox", { name: "OPEN" })
    .selectOption("IN_PROGRESS");
  await page.getByRole("button", { name: "Save" }).click();

  // Reopen modal to verify
  await issueRow.click();
  await expect(page.getByRole("combobox", { name: "HIGH" })).toBeVisible();
  await expect(
    page.getByRole("combobox", { name: "IN_PROGRESS" }),
  ).toBeVisible();
});
