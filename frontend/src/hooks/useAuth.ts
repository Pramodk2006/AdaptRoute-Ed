/**
 * useAuth hook — wraps auth store with API calls for login/register/logout.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import type { TokenResponse, User } from "@/lib/types";

interface LoginPayload { email: string; password: string; }
interface RegisterPayload { email: string; username: string; password: string; }

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, isAuthenticated, setAuth, setUser, logout: storeLogout } = useAuthStore();

  // ── Fetch current user (on mount if authenticated) ──────────────────────────
  const { isLoading: isLoadingUser } = useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      try {
        const { data } = await api.get<User>("/auth/me");
        setUser(data);
        return data;
      } catch (err) {
        storeLogout();
        throw err;
      }
    },
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 10,
    retry: false,
  });

  // ── Register mutation ────────────────────────────────────────────────────────
  const registerMutation = useMutation({
    mutationFn: async (payload: RegisterPayload) => {
      const { data } = await api.post<User>("/auth/register", payload);
      return data;
    },
    onSuccess: () => {
      storeLogout();
      queryClient.clear();
      router.push("/login?registered=true");
    },
  });

  // ── Login mutation ───────────────────────────────────────────────────────────
  const loginMutation = useMutation({
    mutationFn: async (payload: LoginPayload) => {
      // Clear old state before login
      storeLogout();
      queryClient.clear();
      const { data } = await api.post<TokenResponse>("/auth/login", payload);
      return data;
    },
    onSuccess: async (tokenData) => {
      const { data: userData } = await api.get<User>("/auth/me", {
        headers: { Authorization: `Bearer ${tokenData.access_token}` },
      });
      setAuth(userData, tokenData.access_token, tokenData.refresh_token);

      if (!userData.has_profile) {
        router.push("/profile/setup");
      } else {
        router.push("/dashboard");
      }
    },
  });

  // ── Logout ───────────────────────────────────────────────────────────────────
  const logout = useCallback(() => {
    storeLogout();
    queryClient.clear();
  }, [storeLogout, queryClient]);

  return {
    user,
    isAuthenticated,
    isLoadingUser,
    login: loginMutation.mutate,
    loginAsync: loginMutation.mutateAsync,
    isLoginPending: loginMutation.isPending,
    loginError: loginMutation.error,
    register: registerMutation.mutate,
    isRegisterPending: registerMutation.isPending,
    registerError: registerMutation.error,
    logout,
  };
}
