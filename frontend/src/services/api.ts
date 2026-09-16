const API_BASE = 'http://127.0.0.1:8000';

export async function sendChatMessage(message: string, conversationId?: string) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, conversation_id: conversationId })
  });
  return res.json();
}

export async function getConversations() {
  const res = await fetch(`${API_BASE}/api/chat/conversations`);
  return res.json();
}

export async function getSystemMetrics() {
  const res = await fetch(`${API_BASE}/api/system/metrics`);
  return res.json();
}

export async function getRunningProcesses() {
  const res = await fetch(`${API_BASE}/api/system/processes`);
  return res.json();
}

export async function getTools() {
  const res = await fetch(`${API_BASE}/api/tools`);
  return res.json();
}

export async function executeTool(toolName: string, parameters: Record<string, any> = {}) {
  const res = await fetch(`${API_BASE}/api/tools/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tool_name: toolName, parameters })
  });
  return res.json();
}

export async function resolvePermission(requestId: string, approved: boolean) {
  const res = await fetch(`${API_BASE}/api/tools/permissions/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ request_id: requestId, approved })
  });
  return res.json();
}

export async function getMemories(query: string = '') {
  const res = await fetch(`${API_BASE}/api/memory?query=${encodeURIComponent(query)}`);
  return res.json();
}

export async function createMemory(key: string, value: string, type: string = 'fact') {
  const res = await fetch(`${API_BASE}/api/memory`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key, value, type })
  });
  return res.json();
}

export async function deleteMemory(key: string) {
  const res = await fetch(`${API_BASE}/api/memory/${encodeURIComponent(key)}`, {
    method: 'DELETE'
  });
  return res.json();
}

export async function getTasks() {
  const res = await fetch(`${API_BASE}/api/tasks`);
  return res.json();
}

export async function createTask(title: string, description?: string, priority: string = 'medium') {
  const res = await fetch(`${API_BASE}/api/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, description, priority })
  });
  return res.json();
}

export async function updateTask(taskId: string, status?: string, priority?: string) {
  const res = await fetch(`${API_BASE}/api/tasks/${taskId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, priority })
  });
  return res.json();
}

export async function deleteTask(taskId: string) {
  const res = await fetch(`${API_BASE}/api/tasks/${taskId}`, {
    method: 'DELETE'
  });
  return res.json();
}

export async function triggerEmergencyStop() {
  const res = await fetch(`${API_BASE}/api/system/emergency-stop`, { method: 'POST' });
  return res.json();
}

export async function triggerEmergencyReset() {
  const res = await fetch(`${API_BASE}/api/system/emergency-reset`, { method: 'POST' });
  return res.json();
}

export async function getSettings() {
  const res = await fetch(`${API_BASE}/api/settings`);
  return res.json();
}

export async function updateSettings(settingsData: Record<string, any>) {
  const res = await fetch(`${API_BASE}/api/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settingsData)
  });
  return res.json();
}

export async function synthesizeTTS(text: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}/api/voice/tts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  return res.blob();
}
