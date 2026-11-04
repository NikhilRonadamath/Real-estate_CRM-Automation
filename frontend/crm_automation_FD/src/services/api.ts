import axios from 'axios'
import type { Lead, LeadPayload, LeadStatus } from '../types/lead'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

function normalizeLead(lead: Lead): Lead {
  return { ...lead, id: lead.id || lead.lead_id || '' }
}

export const api = {
  createLead: async (payload: LeadPayload) => {
    const response = await apiClient.post('/api/leads/', payload)
    return response.data as {
      success: boolean
      message: string
      lead_id: string
    }
  },

  getLeads: async () => {
    const response = await apiClient.get<Lead[]>('/api/leads/')
    return response.data.map(normalizeLead)
  },

  getLead: async (id: string) => {
    const response = await apiClient.get<Lead>(`/api/leads/${encodeURIComponent(id)}`)
    return normalizeLead(response.data)
  },

  updateLeadStatus: async (id: string, status: LeadStatus) => {
    const response = await apiClient.patch<{ success: boolean; lead: Lead }>(
      `/api/leads/${encodeURIComponent(id)}/status`,
      { status },
    )
    return { ...response.data, lead: normalizeLead(response.data.lead) }
  },

  getHealth: async () => {
    const response = await apiClient.get<{ status: string }>('/api/health')
    return response.data
  },
}

// Keep the existing seller form's default-imported Axios client compatible.
export default apiClient
