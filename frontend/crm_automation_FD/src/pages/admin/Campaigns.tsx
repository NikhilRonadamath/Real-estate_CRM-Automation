import { Megaphone, Sparkles } from 'lucide-react'

export default function Campaigns() {
  return <>
    <div className="page-heading"><div><span className="eyebrow">RE-ENGAGEMENT</span><h1>Recovery campaigns</h1><p>Plan how older enquiries will be reactivated.</p></div></div>
    <section className="panel campaign-empty"><div className="campaign-icon"><Megaphone size={25} /></div><h2>Campaign automation is coming next</h2><p>This area can later support lead segments, message sequences, outreach tracking, and recovered-opportunity reporting.</p><div className="coming-pill"><Sparkles size={14} />Planned next phase</div></section>
  </>
}
