const API_BASE = '/api';

const apiFetch = (input, init = {}) => fetch(input, { credentials: 'include', ...init });

const getHeaders = (isMultipart = false) => {
  const token = import.meta.env.DEV ? localStorage.getItem('jansahay_token') : null;
  const headers = {};
  if (!isMultipart) {
    headers['Content-Type'] = 'application/json';
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

export const api = {
  // Profile
  getProfile: async () => {
    const res = await apiFetch(`${API_BASE}/profile`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to load profile');
    return res.json();
  },
  updateProfile: async (data) => {
    const res = await apiFetch(`${API_BASE}/profile`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update profile');
    return res.json();
  },

  // Schemes
  getSchemes: async (params = {}) => {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        searchParams.append(key, val);
      }
    });
    const res = await apiFetch(`${API_BASE}/schemes?${searchParams.toString()}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch schemes');
    return res.json();
  },
  getSchemeDetails: async (idOrSlug) => {
    const res = await apiFetch(`${API_BASE}/schemes/${idOrSlug}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch scheme details');
    return res.json();
  },
  getCategories: async () => {
    const res = await apiFetch(`${API_BASE}/schemes/categories`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch categories');
    return res.json();
  },

  // Recommendations
  getRecommendations: async (category = '') => {
    const url = category
      ? `${API_BASE}/recommendations?category=${encodeURIComponent(category)}`
      : `${API_BASE}/recommendations`;
    const res = await apiFetch(url, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch recommendations');
    return res.json();
  },
  trackScheme: async (schemeId, status = 'Saved', notes = '') => {
    const res = await apiFetch(`${API_BASE}/recommendations/track`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ scheme_id: schemeId, status, notes }),
    });
    if (!res.ok) throw new Error('Failed to update tracking');
    return res.json();
  },
  getTrackedSchemes: async () => {
    const res = await apiFetch(`${API_BASE}/recommendations/tracked`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch tracked schemes');
    return res.json();
  },

  // Eligibility
  checkEligibility: async (schemeId, profile = null) => {
    const res = await apiFetch(`${API_BASE}/eligibility/check`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ scheme_id: schemeId, profile }),
    });
    if (!res.ok) throw new Error('Failed to run eligibility evaluation');
    return res.json();
  },

  // Chat
  sendMessage: async (message, sessionId = 'default-session', language = 'en') => {
    const res = await apiFetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ message, session_id: sessionId, language }),
    });
    if (!res.ok) throw new Error('Failed to send chat message');
    return res.json();
  },
  getChatHistory: async (sessionId = 'default-session') => {
    const res = await apiFetch(`${API_BASE}/chat/history/${sessionId}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch chat history');
    return res.json();
  },

  // Document Center & OCR
  uploadDocument: async (file, documentTypeHint = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (documentTypeHint) {
      formData.append('document_type', documentTypeHint);
    }
    const res = await apiFetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      headers: getHeaders(true),
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to upload document' }));
      throw new Error(err.detail || 'Failed to upload document');
    }
    return res.json();
  },
  getUserDocuments: async () => {
    const res = await apiFetch(`${API_BASE}/documents`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch user documents');
    return res.json();
  },
  confirmDocumentData: async (docId, confirmedData) => {
    const res = await apiFetch(`${API_BASE}/documents/${docId}/confirm`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(confirmedData),
    });
    if (!res.ok) throw new Error('Failed to confirm document data');
    return res.json();
  },
  deleteDocument: async (docId) => {
    const res = await apiFetch(`${API_BASE}/documents/${docId}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to delete document');
    return res.json();
  },

  // Admin Portal
  getAdminStats: async () => {
    const res = await apiFetch(`${API_BASE}/admin/stats`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch admin statistics');
    return res.json();
  },
  getAdminQualityMetrics: async () => {
    const res = await apiFetch(`${API_BASE}/admin/quality-metrics`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch quality metrics');
    return res.json();
  },
  getAdminConflicts: async () => {
    const res = await apiFetch(`${API_BASE}/admin/conflicts`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch scheme conflicts');
    return res.json();
  },
  getAdminAuditLogs: async () => {
    const res = await apiFetch(`${API_BASE}/admin/audit-logs`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  },
  reimportDataset: async () => {
    const res = await apiFetch(`${API_BASE}/admin/reimport`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to trigger dataset re-import');
    return res.json();
  },
  getAdminSchemes: async () => {
    const res = await apiFetch(`${API_BASE}/admin/schemes`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch admin schemes');
    return res.json();
  },
  toggleVerifyScheme: async (schemeId) => {
    const res = await apiFetch(`${API_BASE}/admin/schemes/${schemeId}/verify`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to update verification');
    return res.json();
  },
};
