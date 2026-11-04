
import { useCallback, useEffect, useState } from 'react'
import { ArrowLeft, RefreshCw, BrainCircuit } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import { api } from '../../services/api'
import type { Lead, LeadStatus } from '../../types/lead'
import {
  analyzeLead,
  getSavedAIAnalysis,
  type AILeadAnalysis,
} from '../../services/aiapi'
const statuses: LeadStatus[] = [
  'new',
  'contacted',
  'qualified',
  'follow_up',
  'recovered',
  'lost',
]

function Field({
  label,
  value,
}: {
  label: string
  value?: string | number | null
}) {
  return (
    <div className="detail-field">
      <span>{label}</span>
      <strong>
        {value === null || value === undefined || value === ''
          ? '—'
          : String(value)}
      </strong>
    </div>
  )
}

export default function LeadDetails() {
  const { id: leadId = '' } = useParams()

  // Lead information
  const [aiAnalyzedAt, setAiAnalyzedAt] = useState<string | null>(null)
  const [lead, setLead] = useState<Lead | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  // AI analysis state
  const [aiAnalysis, setAiAnalysis] =
    useState<AILeadAnalysis | null>(null)

  const [aiLoading, setAiLoading] = useState(false)
  const [aiError, setAiError] = useState('')

  // Load lead details
const load = useCallback(async () => {
  if (!leadId) {
    setError('Invalid lead ID')
    setLoading(false)
    return
  }

  setLoading(true)
  setError('')
  setAiError('')

  try {
    // Load the lead profile.
    const leadData = await api.getLead(leadId)
    setLead(leadData)

    // Load previously saved AI analysis.
    try {
      const saved = await getSavedAIAnalysis(leadId)

      setAiAnalysis(saved.analysis)
      setAiAnalyzedAt(saved.analyzed_at)
    } catch (aiLoadError) {
      console.error('Could not load saved AI analysis:', aiLoadError)
      setAiAnalysis(null)
      setAiAnalyzedAt(null)
      setAiError('Could not load saved AI analysis.')
    }
  } catch (e) {
    setError(
      e instanceof Error
        ? e.message
        : 'Could not load lead',
    )
  } finally {
    setLoading(false)
  }
}, [leadId])

  useEffect(() => {
    void load()
  }, [load])

  // Run AI lead analysis
  async function handleAIAnalysis() {
  try {
    setAiLoading(true)
    setAiError('')

    const result = await analyzeLead(leadId)

    console.log('Latest analysis:', result.analysis)

    if (!result.success || !result.analysis) {
      throw new Error('No analysis returned by the server')
    }

    setAiAnalysis(result.analysis)
    setAiAnalyzedAt(result.analyzed_at)

  } catch (e) {
    setAiError(
      e instanceof Error ? e.message : 'AI analysis failed',
    )
  } finally {
    setAiLoading(false)
  }
}

  // Update lead status
  async function update(status: LeadStatus) {
    if (!lead) return

    setSaving(true)
    setError('')

    try {
      const result = await api.updateLeadStatus(
        leadId,
        status
      )

      setLead(result.lead)
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : 'Could not update status'
      )
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="empty-state">
        Loading lead…
      </div>
    )
  }

  if (!lead) {
    return (
      <>
        <Link
          to="/admin/leads"
          className="back-link"
        >
          <ArrowLeft size={16} />
          Back to leads
        </Link>

        <div className="alert error">
          {error || 'Lead not found'}
        </div>
      </>
    )
  }

  return (
    <>
      {/* Navigation */}
      <Link
        to="/admin/leads"
        className="back-link"
      >
        <ArrowLeft size={16} />
        Back to leads
      </Link>

      {/* Page heading */}
      <div className="page-heading">
        <div>
          <span className="eyebrow">
            LEAD PROFILE
          </span>

          <h1>{lead.name}</h1>

          <p>
            {lead.email} · {lead.phone}
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={() => void load()}
          disabled={loading}
        >
          <RefreshCw size={15} />
          Refresh
        </button>
      </div>

      {error && (
        <div
          className="alert error"
          role="alert"
        >
          {error}
        </div>
      )}

      {/* Lead information */}
      <div className="details-layout">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Property information</h2>
              <p>Seller and property details</p>
            </div>

            <span
              className={`status status-${lead.status}`}
            >
              {(lead.status || 'unknown').replaceAll('_', ' ')}
            </span>
          </div>

          <div className="detail-grid">
            <Field
              label="Full name"
              value={lead.name}
            />

            <Field
              label="Email"
              value={lead.email}
            />

            <Field
              label="Phone"
              value={lead.phone}
            />

            <Field
              label="Property type"
              value={lead.property_type?.replaceAll('_', ' ')}
            />

            <Field
              label="Location"
              value={lead.location}
            />

            <Field
              label="Estimated value"
              value={
                lead.estimated_value
                  ? new Intl.NumberFormat('en-IN', {
                      style: 'currency',
                      currency: 'INR',
                      maximumFractionDigits: 0,
                    }).format(lead.estimated_value)
                  : '—'
              }
            />

            <Field
              label="Selling timeline"
              value={lead.selling_timeline?.replaceAll('_', ' ')}
            />

            <Field
              label="Lead source"
              value={lead.source}
            />

            <Field
              label="Lead score"
              value={lead.lead_score}
            />

            <Field
              label="Seller intent"
              value={lead.seller_intent}
            />
          </div>

          <div className="motivation">
            <span>Seller motivation</span>
            <p>
              {lead.motivation ||
                'No motivation details provided.'}
            </p>
          </div>
        </section>

        {/* Status management */}
        <aside className="panel status-panel">
          <h2>Update lead status</h2>

          <p>
            Move this enquiry through your sales pipeline.
          </p>

          <label className="stacked-label">
            Current status

            <select
              disabled={saving}
              value={lead.status}
              onChange={(e) =>
                void update(e.target.value as LeadStatus)
              }
            >
              {statuses.map((s) => (
                <option key={s} value={s}>
                  {s.replaceAll('_', ' ')}
                </option>
              ))}
            </select>
          </label>

          {saving && (
            <small className="muted">
              Saving…
            </small>
          )}

          <div className="detail-meta">
            <span>Lead ID</span>
            <code>{lead.lead_id || lead.id}</code>

            <span>Created</span>
            <strong>
              {lead.created_at
                ? new Date(lead.created_at).toLocaleString()
                : '—'}
            </strong>

            <span>Last updated</span>
            <strong>
              {lead.updated_at
                ? new Date(lead.updated_at).toLocaleString()
                : '—'}
            </strong>
          </div>
        </aside>
      </div>

      {/* AI Lead Intelligence */}
      <section className="panel ai-panel">
        <div className="panel-heading">
          <div>
            <h2>
              <BrainCircuit
                size={20}
                style={{
                  display: 'inline',
                  marginRight: '8px',
                }}
              />
              AI Lead Intelligence
            </h2>

            <p>
              Analyze seller intent, qualification and
              recommended actions. This does not contact
              the seller or automatically change lead data.
            </p>
          </div>

          <button
            className="primary-button"
            onClick={() => void handleAIAnalysis()}
            disabled={aiLoading || !leadId}
          >
            {aiAnalyzedAt && (
                <p className="muted">
                     Last analyzed:{' '}
                    {new Date(aiAnalyzedAt).toLocaleString('en-IN')}
                 </p>
            )}
            {aiLoading
              ? 'Analyzing…'
              : 'Analyze with AI'}
          </button>
        </div>

        {aiError && (
          <div
            className="alert error"
            role="alert"
          >
            {aiError}
          </div>
        )}

        {aiLoading && (
          <div className="empty-state">
            Analyzing the lead details…
          </div>
        )}

        {!aiAnalysis && !aiLoading && !aiError && (
          <div className="empty-state">
            Click Analyze with AI to generate
            seller intelligence.
          </div>
        )}

        {aiAnalysis && (
          <>
            <div className="ai-analysis-grid">
              <Field
                label="Seller intent"
                value={aiAnalysis.seller_intent.replaceAll('_', ' ')}
              />

              <Field
                label="Lead score"
                value={`${aiAnalysis.lead_score}/100`}
              />

              <Field
                label="Selling urgency"
                value={aiAnalysis.selling_urgency}
              />

              <Field
                label="Confidence"
                value={`${(aiAnalysis.confidence * 100).toFixed(0)}%`}
              />

              <Field
                label="Motivation analysis"
                value={aiAnalysis.motivation_analysis}
              />

              <Field
                label="Qualification"
                value={aiAnalysis.qualification_summary}
              />

              <Field
                label="Recommended action"
                value={aiAnalysis.recommended_action.replaceAll('_', ' ')}
              />

              <Field
                label="Recommendation reason"
                value={aiAnalysis.recommendation_reason}
              />

              <div className="detail-field ai-missing">
                <span>Missing information</span>

                {aiAnalysis.missing_information.length > 0 ? (
                  <ul>
                    {aiAnalysis.missing_information.map(
                      (item, index) => (
                        <li key={`${item}-${index}`}>
                          {item}
                        </li>
                      )
                    )}
                  </ul>
                ) : (
                  <strong>
                    None identified
                  </strong>
                )}
              </div>
            </div>

            <p className="muted">
              AI-generated assessment. Lead score and
              confidence are experimental indicators,
              not validated conversion probabilities.
            </p>
          </>
        )}
      </section>
    </>
  )
}
