import React from "react";
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from "@heroicons/react/24/outline";
import { Link } from "react-router-dom";

interface PublicTunnelCardProps {
  tunnel: {
    route: string;
    connected: boolean;
    created_at: number;
    last_seen?: number;
    description?: string;
  };
  publicBaseUrl: string;
}

export const PublicTunnelCard: React.FC<PublicTunnelCardProps> = ({
  tunnel,
  publicBaseUrl
}) => {
  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  const publicUrl = `${publicBaseUrl}/r/${tunnel.route}`;

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              <Link to={publicUrl}>{tunnel.route}</Link>
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
      </div>
    </div>
  );
};
