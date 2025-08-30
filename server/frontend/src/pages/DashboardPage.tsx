import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { apiClient } from "../lib/api";
import type {
  Tunnel,
  CreateTunnelRequest,
  CreateTunnelResponse,
} from "../types/tunnel";
import { CreateTunnelModal } from "../components/tunnel/CreateTunnelModal";
import { TunnelCard } from "../components/tunnel/TunnelCard";
import { FormButton } from "../components/forms/FormButton";

import {
  PlusIcon,
  ArrowRightOnRectangleIcon,
  UserIcon,
  GlobeAltIcon,
  CheckIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import { CopyButton } from "../components/general/CopyButton";

export const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();
  const [tunnels, setTunnels] = useState<Tunnel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newTunnelData, setNewTunnelData] =
    useState<CreateTunnelResponse | null>(null);
  const [showTokenModal, setShowTokenModal] = useState(false);

  const publicBaseUrl =
    import.meta.env.VITE_PUBLIC_BASE_URL || "http://localhost:8000";
  const wsBaseUrl = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000";

  useEffect(() => {
    loadTunnels();
  }, []);

  const loadTunnels = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.getTunnels();
      setTunnels(response.data.tunnels);
      setError(null);
    } catch (err: any) {
      console.error("Failed to load tunnels:", err);
      setError("Failed to load tunnels. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTunnel = async (data: CreateTunnelRequest) => {
    try {
      setIsCreating(true);
      const response = await apiClient.createTunnel(data);
      // Store the new tunnel data to show in the token modal
      setNewTunnelData(response.data);
      // Reload tunnels to get the updated list
      await loadTunnels();
      // Show the token modal with the new tunnel information
      setShowTokenModal(true);
    } catch (err: any) {
      throw err; // Let the modal handle the error display
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteTunnel = async (route: string) => {
    try {
      await apiClient.deleteTunnel(route);
      setTunnels(tunnels.filter((t) => t.route !== route));
    } catch (err: any) {
      console.error("Failed to delete tunnel:", err);
      throw err;
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const handleCloseTokenModal = () => {
    setShowTokenModal(false);
    setNewTunnelData(null);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
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
                RouteTunnel
              </h1>
            </div>

            <div className="flex items-center space-x-4">
              <Link
                to="/public-tunnels"
                className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                <GlobeAltIcon className="h-4 w-4" />
                <span>Public Tunnels</span>
              </Link>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <UserIcon className="h-4 w-4" />
                <span>{user?.email}</span>
              </div>
              <FormButton
                variant="secondary"
                size="sm"
                className="flex items-center space-x-2"
                onClick={handleLogout}
              >
                <ArrowRightOnRectangleIcon className="h-4 w-4 mr-2" />
                Logout
              </FormButton>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Your Tunnels</h2>
              <p className="text-gray-600 mt-1">
                Create and manage your secure tunnels
              </p>
            </div>
            <FormButton
              variant="primary"
              className="flex items-center space-x-2"
              onClick={() => setShowCreateModal(true)}
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Create Tunnel
            </FormButton>
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
              No tunnels
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating your first tunnel.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tunnels.map((tunnel) => (
              <TunnelCard
                key={tunnel.route}
                tunnel={tunnel}
                onDelete={handleDeleteTunnel}
                publicBaseUrl={publicBaseUrl}
                wsBaseUrl={wsBaseUrl}
              />
            ))}
          </div>
        )}
      </main>

      {/* Create Tunnel Modal */}
      <CreateTunnelModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreateTunnel={handleCreateTunnel}
        isLoading={isCreating}
      />

      {/* Token Display Modal */}
      {showTokenModal && newTunnelData && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <CheckIcon className="h-8 w-8 text-green-500" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      Tunnel Created Successfully!
                    </h3>
                    <p className="text-sm text-gray-600">
                      Your tunnel "{newTunnelData.route}" is ready to use.
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleCloseTokenModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-6">
                {/* Connection Token */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Connection Token
                  </label>
                  <p className="text-sm text-gray-600 mb-3">
                    Use this token to connect your local service to the tunnel.
                    Keep it secure!
                  </p>
                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={newTunnelData.token}
                      readOnly
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-sm font-mono"
                    />
                    <CopyButton text={newTunnelData.token} />
                  </div>
                </div>

                {/* Public URL */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Public URL
                  </label>
                  <p className="text-sm text-gray-600 mb-3">
                    This is the public URL where your service will be
                    accessible.
                  </p>
                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={newTunnelData.public_url}
                      readOnly
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-sm"
                    />
                    <CopyButton text={newTunnelData.public_url} />
                  </div>
                </div>

                {/* WebSocket URL */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    WebSocket URL
                  </label>
                  <p className="text-sm text-gray-600 mb-3">
                    Use this URL to establish the WebSocket connection with your
                    token.
                  </p>
                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={newTunnelData.ws_url}
                      readOnly
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-sm"
                    />
                    <CopyButton text={newTunnelData.ws_url} />
                  </div>
                </div>

                {/* Important Notice */}
                <div className="rounded-md bg-yellow-50 p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg
                        className="h-5 w-5 text-yellow-400"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h3 className="font-medium text-yellow-800">Important</h3>
                      <div className="mt-2 text-sm text-yellow-700">
                        <p>
                          <b>
                            Save the token - you will not be able to copy it
                            again
                          </b>
                          , unless you create another route. You'll need it to
                          connect your local service to this tunnel.{" "}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end pt-6">
                <FormButton variant="primary" onClick={handleCloseTokenModal}>
                  Got it!
                </FormButton>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
