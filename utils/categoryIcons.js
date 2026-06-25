export function getIconForCategory(categoryName) {
  const name = (categoryName || "").toLowerCase();
  if (name.includes("praia")) return "umbrella-outline";
  if (name.includes("lagoa")) return "water-outline";
  if (name.includes("cachoeira")) return "water";
  if (name.includes("trilha")) return "walk-outline";
  if (name.includes("cultural") || name.includes("hist")) return "business-outline";
  if (name.includes("religioso")) return "book-outline";
  if (name.includes("lazer")) return "game-controller-outline";
  if (name.includes("corporativo")) return "briefcase-outline";
  return "location-outline";
}
