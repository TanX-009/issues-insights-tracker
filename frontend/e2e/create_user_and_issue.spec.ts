import { test, expect } from "@playwright/test";

test("Admin creates a user, user creates issue, admin triages", async ({
  page,
}) => {
  // Login as admin
  await page.goto("/logout");
  await page.goto("/login");
  await page.getByPlaceholder("Email").fill("admin@email.com");
  await page.getByPlaceholder("Password").fill("admin");
  await page.getByRole("button", { name: "Login" }).click();
  await expect(page).toHaveURL("/");

  // Go to users page
  await page.getByRole("link", { name: "Users" }).click();
  await expect(page).toHaveURL("/users");

  // Delete test user if already exists
  const userRow = page.locator("tr", { hasText: "test@email.com" });
  if ((await userRow.count()) > 0) {
    const deleteButton = userRow.getByRole("button", { name: "Delete" });
    await deleteButton.click(); // open delete confirmation modal
    const dialog = page.locator("dialog");
    await dialog.getByRole("button", { name: "Delete" }).click(); // confirm delete
  }
  // await expect(userRow).toHaveCount(userRows - 1); // ensure it's gone

  // Add new user
  await page.getByRole("button", { name: "Add User" }).click();
  await page.getByPlaceholder("Email").fill("test@email.com");
  await page.getByPlaceholder("Password").fill("test");
  await page.getByLabel("role").selectOption("MAINTAINER");
  await page.getByRole("button", { name: "Add", exact: true }).click();
  await expect(page).toHaveURL("/users");

  // Go back to dashboard
  await page.getByRole("link", { name: "Dashboard" }).click();
  await expect(page).toHaveURL("/");

  // delete the previously created issues
  const issueRows = page.locator("tr", { hasText: "Sample Bug Report" });
  const count = await issueRows.count();

  for (let i = 0; i < count; i++) {
    await issueRows.nth(i).click(); // Click the i-th row
    await page.locator("button", { hasText: "Delete" }).click(); // Open delete confirm
    await page.locator("button", { hasText: "Delete" }).click(); // Confirm delete
  }

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
  const issueRow = page.locator("tr").filter({ hasText: "Sample Bug Report" });
  await issueRow.click();

  // Change severity and status
  await page.getByLabel("severity").selectOption("HIGH");
  await page.getByLabel("status").selectOption("IN_PROGRESS");
  await page.getByRole("button", { name: "Save" }).click();

  // verify updated severity and status
  const report = page.locator("tr", { hasText: "Sample Bug Report" });
  await expect(report).toContainText("HIGH");
  // await expect(report).toContainText("IN_PROGRESS");
});
