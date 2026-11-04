import { useCallback, useEffect, useMemo, useState } from 'react'
import { ArrowUpRight, Clock3, RefreshCw, Trophy, UserCheck, Users } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '../../services/api'
import type { Lead } from '../../types/lead'

const date = (value?: string) => value ? new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
const propertyLabel = (value?: string) => (value || '—').replaceAll('_', ' ')

export default function Dashboard() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try { setLeads(await api.getLeads()) }
    catch (e) { setError(e instanceof Error ? e.message : 'Could not load leads') }
    finally { setLoading(false) }
  }, [])
  useEffect(() => { void load() }, [load])

  const stats = useMemo(() => [
    { label: 'Total leads', value: leads.length, icon: Users, tone: 'blue' },
    { label: 'New leads', value: leads.filter(x => x.status === 'new').length, icon: Clock3, tone: 'amber' },
    { label: 'Qualified', value: leads.filter(x => x.status === 'qualified').length, icon: UserCheck, tone: 'green' },
    { label: 'Recovered', value: leads.filter(x => x.status === 'recovered').length, icon: Trophy, tone: 'violet' },
  ], [leads])

  return <>
    <div className="page-heading"><div><span className="eyebrow">OVERVIEW</span><h1>Dashboard</h1><p>Here’s what’s happening with your property leads.</p></div><button className="secondary-button" onClick={() => void load()} disabled={loading}><RefreshCw size={15} />Refresh</button></div>
    {error && <div className="alert error" role="alert">{error}</div>}
    <section className="stats-grid">{stats.map(s => <article className="stat-card" key={s.label}><div className={`stat-icon ${s.tone}`}><s.icon size={19} /></div><span>{s.label}</span><strong>{loading ? '—' : s.value}</strong><small>From your leads collection</small></article>)}</section>
    <section className="panel"><div className="panel-heading"><div><h2>Recent leads</h2><p>Your latest seller enquiries</p></div><Link to="/admin/leads" className="text-link">View all leads <ArrowUpRight size={15} /></Link></div>
      {loading ? <div className="empty-state">Loading leads…</div> : leads.length === 0 ? <div className="empty-state">No leads yet. New seller enquiries will appear here.</div> : <div className="table-wrap"><table><thead><tr><th>Lead</th><th>Property</th><th>Location</th><th>Timeline</th><th>Status</th><th>Added</th></tr></thead><tbody>{[...leads].sort((a,b) => (b.created_at || '').localeCompare(a.created_at || '')).slice(0, 6).map(l => <tr key={l.id}><td><Link className="lead-name" to={`/admin/leads/${encodeURIComponent(l.id)}`}>{l.name || 'Unnamed lead'}</Link><small>{l.email}</small></td><td>{propertyLabel(l.property_type)}</td><td>{l.location || '—'}</td><td>{propertyLabel(l.selling_timeline)}</td><td><span className={`status status-${l.status}`}>{propertyLabel(l.status)}</span></td><td>{date(l.created_at)}</td></tr>)}</tbody></table></div>}
    </section>
    <div className="dashboard-note"><strong>Next step</strong><span>Review enquiries and update their status from the Leads page. Campaign automation can be added as a later workflow.</span></div>
  </>
}
