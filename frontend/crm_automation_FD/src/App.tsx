import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AdminLayout from './layouts/AdminLayout'
import Campaigns from './pages/admin/Campaigns'
import Dashboard from './pages/admin/Dashboard'
import FollowUps from './pages/admin/FollowUps'
import LeadDetails from './pages/admin/LeadDetails'
import Leads from './pages/admin/Leads'
import Settings from './pages/admin/Settings'
import LeadForm from './pages/LeadForm'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LeadForm />} />
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="leads" element={<Leads />} />
          <Route path="leads/:id" element={<LeadDetails />} />
          <Route path="follow-ups" element={<FollowUps />} />
          <Route path="campaigns" element={<Campaigns />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
