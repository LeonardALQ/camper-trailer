// Prefix a site path such as '/models/steps.json' with the base path, so the same link works at the site root
// in a local build and under /camper-trailer/ on GitHub Pages.
export const withBase = (path: string): string => `${import.meta.env.BASE_URL.replace(/\/$/, '')}${path}`;
