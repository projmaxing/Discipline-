// Static-asset Worker for HabitFlow Web.
// The app is a client-side SPA; every route is rendered in the browser,
// so the Worker only needs to serve the built assets (with SPA fallback).
export default {
  async fetch(request, env) {
    return env.ASSETS.fetch(request)
  },
}
