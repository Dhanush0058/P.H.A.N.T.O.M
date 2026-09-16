export type AssistantState =
  | 'IDLE'
  | 'LISTENING'
  | 'THINKING'
  | 'EXECUTING'
  | 'SPEAKING'
  | 'ERROR';

export type PermissionLevel = 'SAFE' | 'CONFIRM' | 'DANGEROUS' | 'BLOCKED';

export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, any>;
  result?: {
    success: boolean;
    data?: any;
    error?: string;
    message?: string;
  };
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'tool' | 'system';
  content: string;
  timestamp: string;
  tool_calls?: ToolCall[];
  tools_invoked?: string[];
}

export interface PermissionRequestEvent {
  request_id: string;
  tool_name: string;
  permission_level: PermissionLevel;
  action_summary: string;
  parameters: Record<string, any>;
}

export interface SystemMetrics {
  os: string;
  cpu: {
    usage_percent: number;
    cores: number;
    freq_mhz: number;
  };
  memory: {
    total_gb: number;
    used_gb: number;
    free_gb: number;
    percent: number;
  };
  disk: {
    drive: string;
    total_gb: number;
    used_gb: number;
    free_gb: number;
    percent: number;
  };
  network: {
    bytes_sent_mb: number;
    bytes_recv_mb: number;
  };
  battery: {
    percent: number | null;
    power_plugged: boolean;
  };
  timestamp: string;
}

export interface MemoryItem {
  id: string;
  key: string;
  value: string;
  type: string;
  created_at?: string;
}

export interface TaskItem {
  id: string;
  title: string;
  description?: string;
  status: string;
  priority: string;
  created_at?: string;
  due_at?: string;
}

export interface ToolDefinition {
  name: string;
  description: string;
  category: string;
  permission_level: PermissionLevel;
  parameters: Record<string, any>;
}
