import { NavLink, Outlet } from 'react-router-dom'
import {
  Building2,
  CalendarClock,
  ExternalLink,
  LayoutDashboard,
  Megaphone,
  Settings,
  Users,
} from 'lucide-react'

const links = [
  { to: '/admin', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/admin/leads', label: 'All Leads', icon: Users },
  { to: '/admin/follow-ups', label: 'Follow-ups', icon: CalendarClock },
  { to: '/admin/campaigns', label: 'Campaigns', icon: Megaphone },
  { to: '/admin/settings', label: 'Settings', icon: Settings },
]

export default function AdminLayout() {
  return (
    <div className="admin-shell">
      <aside className="sidebar">
        <a className="brand" href="/admin" aria-label="EstateConnect admin home">
          <span className="brand-mark"><Building2 size={21} /></span>
          <span>Estate<span className="brand-light">Connect</span><small>LEAD RECOVERY CRM</small></span>
        </a>
        <div className="nav-caption">WORKSPACE</div>
        <nav className="side-nav" aria-label="Admin navigation">
          {links.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Icon size={18} /><span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="admin-avatar">A</div>
          <div><strong>Administrator</strong><small>Workspace account</small></div>
        </div>
      </aside>
      <main className="admin-main">
        <header className="topbar">
          <div><span className="eyebrow">REAL ESTATE OPERATIONS</span><strong>Lead Management</strong></div>
          <a href="/" className="public-link">Seller Portal <ExternalLink size={15} /></a>
        </header>
        <div className="page-content"><Outlet /></div>
      </main>
    </div>
  )
}
