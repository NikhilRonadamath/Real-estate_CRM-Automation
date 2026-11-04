
const API_BASE_URL = 'http://127.0.0.1:8000/api'

export interface AILeadAnalysis {
  seller_intent:
    | 'ready_to_sell'
    | 'exploring'
    | 'not_interested'
    | 'uncertain'
    | 'unknown'

  motivation_analysis: string

  selling_urgency:
    | 'immediate'
    | 'high'
    | 'medium'
    | 'low'
    | 'unknown'

  lead_score: number
  qualification_summary: string
  missing_information: string[]

  recommended_action:
    | 'schedule_valuation'
    | 'contact_seller'
    | 'request_property_details'
    | 'nurture_lead'
    | 'human_handoff'
    | 'no_action'

  recommendation_reason: string
  confidence: number
}

export interface SavedAIAnalysisResponse {
  success: boolean
  lead_id: string
  analysis: AILeadAnalysis | null
  analyzed_at: string | null
}

export async function getSavedAIAnalysis(
  leadId: string,
): Promise<SavedAIAnalysisResponse> {
  const response = await fetch(
    `${API_BASE_URL}/ai/leads/${encodeURIComponent(leadId)}/analysis`,
  )

  if (!response.ok) {
    throw new Error('Unable to load saved AI analysis')
  }

  return response.json() as Promise<SavedAIAnalysisResponse>
}

export async function analyzeLead(
  leadId: string,
): Promise<SavedAIAnalysisResponse> {
  const response = await fetch(
    `${API_BASE_URL}/ai/leads/${encodeURIComponent(leadId)}/analyze`,
    { method: 'POST' },
  )

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'AI analysis failed')
  }

  const data: SavedAIAnalysisResponse = await response.json()
  return data
}