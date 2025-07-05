/**
 * Truncate a string to a specified length and add ellipsis if needed.
 * @param text - The text to truncate
 * @param maxLength - The maximum length before truncation
 * @returns Truncated string with "..." if needed
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trimEnd() + "...";
}
