import React, { useState, useEffect } from "react";
import { apiClient } from "../lib/api";
import type { Tunnel } from "../types/tunnel";
import { PublicTunnelCard } from "../components/tunnel/PublicTunnelCard";
import { GlobeAltIcon } from "@heroicons/react/24/outline";

export const PublicTunnelsPage: React.FC = () => {
  const [tunnels, setTunnels] = useState<Tunnel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const publicBaseUrl =
    import.meta.env.VITE_PUBLIC_BASE_URL || "http://localhost:8000";

  useEffect(() => {
    loadPublicTunnels();
  }, []);

  const loadPublicTunnels = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.getPublicTunnels();
      setTunnels(response.data.tunnels);
      setError(null);
    } catch (err: any) {
      console.error("Failed to load public tunnels:", err);
      setError("Failed to load public tunnels. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading public tunnels...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <GlobeAltIcon className="h-8 w-8 text-primary-600" />
              <h1 className="text-xl font-semibold text-gray-900">
                RouteTunnel - Public Tunnels
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Public Tunnels</h2>
            <p className="text-gray-600 mt-1">
              Discover and access publicly available tunnels
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">{error}</h3>
              </div>
            </div>
          </div>
        )}

        {/* Tunnels Grid */}
        {tunnels.length === 0 ? (
          <div className="text-center py-12">
            <GlobeAltIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No public tunnels
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              There are no public tunnels available at the moment.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tunnels.map((tunnel) => (
              <PublicTunnelCard
                key={tunnel.route}
                tunnel={tunnel}
                publicBaseUrl={publicBaseUrl}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};