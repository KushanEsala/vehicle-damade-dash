export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function mutationMessage(path: string, method: string): string {
  if (path.includes("/finalize")) return "Assessment finalized and report created.";
  if (path === "/api/analyses" && method === "POST") return "Damage analysis completed.";
  if (path.includes("/change-password")) return "Password updated successfully.";
  if (method === "DELETE") return "Record deleted successfully.";
  if (method === "PATCH" || method === "PUT") return "Changes saved successfully.";
  return "Record saved successfully.";
}

function notify(detail: {type: "success" | "error"; message: string}) {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("apex:toast", {detail}));
  }
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method || "GET").toUpperCase();
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      ...(init.body instanceof FormData ? {} : {"Content-Type": "application/json"}),
      ...init.headers,
    },
  });
  if (response.status === 204) return undefined as T;
  const data = await response.json().catch(() => ({}));
  const isLoginSessionCheck =
    typeof window !== "undefined" && path === "/api/auth/session" && window.location.pathname === "/login";
  if (response.status === 401 && path !== "/api/auth/login" && !isLoginSessionCheck && typeof window !== "undefined") {
    sessionStorage.setItem("auth_notice", "Your session expired. Sign in again to continue.");
    window.location.replace("/login");
    throw new Error("Your session expired. Sign in again to continue.");
  }
  if (!response.ok) {
    const message = data.detail || "The request could not be completed.";
    if (!path.startsWith("/api/auth/")) notify({type: "error", message});
    throw new Error(message);
  }
  if (method !== "GET" && !path.endsWith("/login") && !path.endsWith("/logout")) {
    notify({type: "success", message: mutationMessage(path, method)});
  }
  return data as T;
}

export type User = {
  id: number; username: string; email: string; role: "admin" | "operator" | "customer";
  customer_id: number | null; must_change_password: boolean;
};
