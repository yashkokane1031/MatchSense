"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { api, type ClientHealthStatus } from "@/lib/api";

export function useHealthStatus() {
  const [health, setHealth] = useState<ClientHealthStatus>({
    status: "healthy",
    derivedStatus: "healthy",
    model_loaded: true,
    database_connected: true,
    models: {},
  });
  const lastFetchRef = useRef<number>(0);

  const fetchHealth = useCallback(async () => {
    const now = Date.now();
    if (now - lastFetchRef.current < 30_000) return; // Throttle 30s
    lastFetchRef.current = now;
    const res = await api.getHealth();
    setHealth(res);
  }, []);

  useEffect(() => {
    fetchHealth();
    const onFocus = () => fetchHealth();
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, [fetchHealth]);

  return { health, refetch: fetchHealth };
}
