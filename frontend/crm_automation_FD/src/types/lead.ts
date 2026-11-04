export type LeadStatus =
  | 'new'
  | 'contacted'
  | 'qualified'
  | 'follow_up'
  | 'recovered'
  | 'lost'

export interface Lead {
  id: string
  lead_id?: string
  name: string
  email: string
  phone: string
  property_type: string
  location: string
  estimated_value?: number | null
  selling_timeline: string
  motivation?: string | null
  status: LeadStatus | string
  source?: string
  seller_intent?: string
  lead_score?: number
  assigned_agent?: string | null
  created_at?: string
  updated_at?: string
}

export interface LeadPayload {
  name: string
  email: string
  phone: string
  property_type: string
  location: string
  estimated_value?: number | null
  selling_timeline: string
  motivation?: string
}

// Compatibility with the existing seller form.
export type LeadFormData = LeadPayload

export interface LeadResponse {
  success: boolean
  message: string
  lead_id: string
}
