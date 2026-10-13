const BASE = import.meta.env.VITE_API_BASE ?? "";

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(BASE + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error("Can't reach the server. Check your connection and try again.");
  }

  if (!response.ok) {
    let message = "Something went wrong. Try again.";
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
      else if (response.status === 422) message = "That link doesn't look right. Check it and try again.";
    } catch {
      /* keep the generic message */
    }
    throw new Error(message);
  }
  return response.json();
}

export const analyzeLink = (url) =>
  request("/api/analyze", { method: "POST", body: JSON.stringify({ url }) });

export const createJob = (payload) =>
  request("/api/jobs", { method: "POST", body: JSON.stringify(payload) });

export const getJob = (id) => request(`/api/jobs/${id}`);

export const fileUrl = (path) => BASE + path;
