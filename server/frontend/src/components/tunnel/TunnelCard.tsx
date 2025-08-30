import React, { useState } from "react";
import {
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  GlobeAltIcon,
  LockClosedIcon,
} from "@heroicons/react/24/outline";
import { FormButton } from "../forms/FormButton";
import { CopyButton } from "../general/CopyButton";

interface TunnelCardProps {
  tunnel: {
    route: string;
    connected: boolean;
    created_at: number;
    last_seen?: number;
    description?: string;
    is_public: boolean;
  };
  onDelete: (route: string) => Promise<void>;
  publicBaseUrl: string;
  wsBaseUrl: string;
}

export const TunnelCard: React.FC<TunnelCardProps> = ({
  tunnel,
  onDelete,
  publicBaseUrl,
  wsBaseUrl,
}) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const handleDelete = async () => {
    if (
      window.confirm(
        `Are you sure you want to delete tunnel "${tunnel.route}"?`
      )
    ) {
      setIsDeleting(true);
      try {
        await onDelete(tunnel.route);
      } catch (error) {
        console.error("Failed to delete tunnel:", error);
      } finally {
        setIsDeleting(false);
      }
    }
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  const publicUrl = `${publicBaseUrl}/r/${tunnel.route}`;
  const wsUrl = `${wsBaseUrl}/ws/tunnel?token=YOUR_TOKEN`;

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {tunnel.route}
            </h3>
            <span
              className={`text-sm font-medium flex items-center space-x-2 ${
                tunnel.connected ? "text-green-600" : "text-red-600"
              }`}
            >
              {tunnel.connected ? (
                <CheckCircleIcon className="h-5 w-5 text-green-500" />
              ) : (
                <XCircleIcon className="h-5 w-5 text-red-500" />
              )}
              {tunnel.connected ? "Connected" : "Disconnected"}
            </span>
            <span
              className={`text-sm font-medium flex items-center space-x-1 ${
                tunnel.is_public ? "text-blue-600" : "text-gray-600"
              }`}
            >
              {tunnel.is_public ? (
                <GlobeAltIcon className="h-4 w-4 text-blue-500" />
              ) : (
                <LockClosedIcon className="h-4 w-4 text-gray-500" />
              )}
              {tunnel.is_public ? "Public" : "Private"}
            </span>
          </div>

          {tunnel.description && (
            <p className="text-gray-600 text-sm mb-3">{tunnel.description}</p>
          )}

          <div className="text-sm text-gray-500 space-y-1">
            <div className="flex items-center space-x-1">
              <ClockIcon className="h-4 w-4" />
              <span>Created: {formatDate(tunnel.created_at)}</span>
            </div>
            {tunnel.last_seen && (
              <div className="flex items-center space-x-1">
                <ClockIcon className="h-4 w-4" />
                <span>Last seen: {formatDate(tunnel.last_seen)}</span>
              </div>
            )}
          </div>
        </div>

        <div className="flex space-x-2">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            {showDetails ? "Hide Details" : "Show Details"}
          </button>
          <FormButton
            variant="danger"
            size="sm"
            onClick={handleDelete}
            loading={isDeleting}
          >
            <TrashIcon className="h-4 w-4" />
          </FormButton>
        </div>
      </div>

      {showDetails && (
        <div className="mt-4 pt-4 border-t border-gray-200 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Public URL
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={publicUrl}
                readOnly
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-sm"
              />
              <CopyButton text={publicUrl} />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              WebSocket URL
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={wsUrl}
                readOnly
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-sm"
              />
              <CopyButton text={wsUrl} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
