import { useState, useEffect } from 'react'
import { EmptyState, Modal, StatusBadge } from '../../components/ui/index'
import { Briefcase, ListTodo } from 'lucide-react'

// Dummy data for client projects since there's no specific clientApi for projects yet.
const MOCK_PROJECTS = [
  { id: 1, name: 'Website Redesign', status: 'active', progress: 75, deadline: '2026-08-15', desc: 'Revamping the main corporate site.' },
  { id: 2, name: 'Mobile App V2', status: 'pending', progress: 20, deadline: '2026-10-01', desc: 'New mobile app features for iOS and Android.' },
  { id: 3, name: 'SEO Optimization', status: 'completed', progress: 100, deadline: '2026-03-10', desc: 'On-page and technical SEO improvements.' }
]

const MOCK_TASKS = {
  1: [{ id:101, name:'Design Mockups', status:'done' }, { id:102, name:'Frontend Build', status:'in_progress' }, { id:103, name:'Backend API', status:'todo' }],
  2: [{ id:201, name:'UI/UX Wireframes', status:'in_progress' }, { id:202, name:'Database Schema', status:'todo' }],
  3: [{ id:301, name:'Keyword Research', status:'done' }, { id:302, name:'Content Update', status:'done' }]
}

export default function ClientProjects() {
  const [projects] = useState(MOCK_PROJECTS)
  const [activeProj, setActiveProj] = useState(null)

  return (
    <>
      <div className="page-header">
        <h1>Projects</h1>
        <p>Overview of your ongoing and past projects.</p>
      </div>

      {projects.length === 0 ? (
        <div className="card"><EmptyState title="No projects yet" /></div>
      ) : (
        <div className="grid-3">
          {projects.map(p => (
            <div key={p.id} className="card" style={{display:'flex', flexDirection:'column'}}>
              <div style={{display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:12}}>
                <div style={{display:'flex', alignItems:'center', gap:10}}>
                  <div className="stat-icon purple" style={{width:36, height:36, borderRadius:8}}><Briefcase size={16}/></div>
                  <div className="font-semibold">{p.name}</div>
                </div>
                <StatusBadge status={p.status}/>
              </div>
              <p style={{color:'var(--c-muted)', fontSize:'.875rem', marginBottom:16, flex:1}}>{p.desc}</p>
              <div style={{marginBottom:16}}>
                <div style={{display:'flex', justifyContent:'space-between', fontSize:'.8rem', marginBottom:4}}>
                  <span>Progress</span><span>{p.progress}%</span>
                </div>
                <div style={{height:6, background:'var(--c-surface3)', borderRadius:3, overflow:'hidden'}}>
                  <div style={{height:'100%', width:`${p.progress}%`, background:'var(--c-primary)'}} />
                </div>
              </div>
              <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                <span style={{fontSize:'.8rem', color:'var(--c-muted)'}}>Due: {p.deadline}</span>
                <button className="btn btn-secondary btn-sm" onClick={() => setActiveProj(p)}>
                  <ListTodo size={14}/> Tasks
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={!!activeProj} onClose={() => setActiveProj(null)} title={`${activeProj?.name} - Tasks`}>
        {activeProj && MOCK_TASKS[activeProj.id] ? (
          <div style={{display:'flex', flexDirection:'column', gap:10}}>
            {MOCK_TASKS[activeProj.id].map(t => (
              <div key={t.id} style={{display:'flex', alignItems:'center', justifyContent:'space-between', padding:12, background:'var(--c-surface2)', borderRadius:'var(--radius-sm)', border:'1px solid var(--c-border)'}}>
                <span className="font-semibold" style={{fontSize:'.9rem'}}>{t.name}</span>
                <StatusBadge status={t.status === 'done' ? 'success' : t.status === 'in_progress' ? 'warning' : 'pending'} />
              </div>
            ))}
          </div>
        ) : (
          <EmptyState title="No tasks found" />
        )}
      </Modal>
    </>
  )
}
