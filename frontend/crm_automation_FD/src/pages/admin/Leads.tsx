import { useCallback, useEffect, useMemo, useState } from 'react'
import { RefreshCw, Search } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '../../services/api'
import type { Lead } from '../../types/lead'


const statuses = ['new', 'contacted', 'qualified', 'follow_up', 'recovered', 'lost']

export default function Leads() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const load = useCallback(async () => {
    setLoading(true); setError('')
    try { setLeads(await api.getLeads()) }
    catch (e) { setError(e instanceof Error ? e.message : 'Could not load leads') }
    finally { setLoading(false) }
  }, [])
  useEffect(() => { void load() }, [load])
  const filtered = useMemo(() => leads.filter(l => {
    const q = search.trim().toLowerCase()
    const matches = [l.name, l.email, l.phone, l.location, l.property_type].some(v => (v || '').toLowerCase().includes(q))
    return matches && (status === 'all' || l.status === status)
  }), [leads, search, status])

  return <>
    <div className="page-heading"><div><span className="eyebrow">PIPELINE</span><h1>All leads</h1><p>Review and manage every seller enquiry in one place.</p></div><button className="secondary-button" onClick={() => void load()} disabled={loading}><RefreshCw size={15} />Refresh</button></div>
    <section className="panel"><div className="toolbar"><label className="search-box"><Search size={17} /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search name, email, phone or location" aria-label="Search leads" /></label><select className="filter-select" value={status} onChange={e => setStatus(e.target.value)} aria-label="Filter by status"><option value="all">All statuses</option>{statuses.map(s => <option key={s} value={s}>{s.replaceAll('_', ' ')}</option>)}</select></div>
      {error && <div className="alert error" role="alert">{error}</div>}
      {loading ? <div className="empty-state">Loading leads…</div> : filtered.length === 0 ? <div className="empty-state">No matching leads found.</div> : <div className="table-wrap"><table><thead><tr><th>Lead</th><th>Phone</th><th>Property</th><th>Location</th><th>Estimated value</th><th>Timeline</th><th>Status</th><th /></tr></thead><tbody>{filtered.map(l => <tr key={l.id}><td><Link className="lead-name" to={`/admin/leads/${encodeURIComponent(l.id)}`}>{l.name || 'Unnamed lead'}</Link><small>{l.email}</small></td><td>{l.phone || '—'}</td><td>{(l.property_type || '—').replaceAll('_', ' ')}</td><td>{l.location || '—'}</td><td>{l.estimated_value ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(l.estimated_value) : '—'}</td><td>{(l.selling_timeline || '—').replaceAll('_', ' ')}</td><td><span className={`status status-${l.status}`}>{(l.status || 'unknown').replaceAll('_', ' ')}</span></td><td><Link className="row-action" to={`/admin/leads/${encodeURIComponent(l.id)}`}>View</Link></td></tr>)}</tbody></table></div>}
    </section><p className="result-count">Showing {filtered.length} of {leads.length} leads</p>
  </>
}
