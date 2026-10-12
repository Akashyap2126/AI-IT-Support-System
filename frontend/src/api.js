
const API_BASE_URL = "http://127.0.0.1:5000";

let refreshPromise = null;

async function refreshAccessToken() {
  const refreshToken = localStorage.getItem("refresh_token");

  if (!refreshToken) {
    throw new Error("No refresh token available");
  }

  if (!refreshPromise) {
    refreshPromise = (async () => {
      const response = await fetch(
        `${API_BASE_URL}/api/auth/refresh`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${refreshToken}`,
          },
        }
      );

      const data = await response.json();

      if (
        !response.ok ||
        !data.access_token ||
        !data.refresh_token
      ) {
        throw new Error(
          data.message || "Session refresh failed"
        );
      }

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      return data.access_token;
    })();
  }

  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

export async function apiFetch(path, options = {}) {
  const {
    token: customToken,
    ...requestOptions
  } = options;

  const makeRequest = (token) => {
    const headers = new Headers(requestOptions.headers || {});

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    } else {
      headers.delete("Authorization");
    }

    return fetch(`${API_BASE_URL}${path}`, {
      ...requestOptions,
      headers,
    });
  };

  // Logout must use the refresh token and must not
  // trigger another refresh if it receives a 401.
  const isLogout = path === "/api/auth/logout";

  if (isLogout) {
    return makeRequest(customToken || null);
  }

  let accessToken = customToken ||
    localStorage.getItem("access_token");

  let response = await makeRequest(accessToken);

  if (
    response.status !== 401 ||
    path === "/api/auth/refresh"
  ) {
    return response;
  }

  try {
    accessToken = await refreshAccessToken();
    response = await makeRequest(accessToken);
    return response;
  } catch (error) {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");

    throw new Error(
      "Your session has expired. Please sign in again."
    );
  }
}
