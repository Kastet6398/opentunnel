export interface Tunnel {
  route: string;
  connected: boolean;
  created_at: number;
  token: string;
  last_seen?: number;
  description?: string;
  is_public: boolean;
}

export interface CreateTunnelRequest {
  route: string;
  description?: string;
  is_public?: boolean;
}

export interface CreateTunnelResponse {
  route: string;
  token: string;
  public_url: string;
  ws_url: string;
}

export interface ListTunnelsResponse {
  tunnels: Tunnel[];
}
