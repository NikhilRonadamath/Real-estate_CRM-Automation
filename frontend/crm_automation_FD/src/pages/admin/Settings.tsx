import { useEffect, useState } from 'react'
import { api } from '../../services/api'

export default function Settings() {
  const [health, setHealth] = useState('Checking…')
  useEffect(() => { api.getHealth().then(result => setHealth(result.status)).catch(() => setHealth('Unavailable')) }, [])
  return <>
    <div className="page-heading"><div><span className="eyebrow">WORKSPACE</span><h1>Settings</h1><p>Basic application and service information.</p></div></div>
    <section className="panel settings-panel"><h2>EstateConnect</h2><p>Lead Recovery CRM</p><div className="detail-grid"><div className="detail-field"><span>Frontend</span><strong>React + TypeScript</strong></div><div className="detail-field"><span>Backend</span><strong>Python + FastAPI · {health}</strong></div><div className="detail-field"><span>Database</span><strong>Google Cloud Firestore REST API</strong></div><div className="detail-field"><span>AI automation</span><strong>Not enabled yet</strong></div></div><div className="alert info">Admin authentication must be configured before deploying this dashboard publicly.</div></section>
  </>
}
