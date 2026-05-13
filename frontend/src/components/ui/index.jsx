import { X, AlertTriangle, Search, ChevronLeft, ChevronRight } from 'lucide-react'

/* ─── Spinner ─────────────────────────────────────────────────────────── */
export function Spinner() {
  return <div className="spinner-wrap"><div className="spinner" /></div>
}

/* ─── Icon wrapper ────────────────────────────────────────────────────── */
export function Icon({ icon: I, size = 16, ...p }) {
  return <I size={size} {...p} />
}

/* ─── Avatar ──────────────────────────────────────────────────────────── */
export function Avatar({ name = '?', size = 'md', src }) {
  const initials = name.split(' ').slice(0,2).map(w => w[0]).join('').toUpperCase()
  return src
    ? <img src={src} alt={name} className={`avatar avatar-${size}`} style={{objectFit:'cover'}}/>
    : <div className={`avatar avatar-${size}`}>{initials}</div>
}

/* ─── StatusBadge ─────────────────────────────────────────────────────── */
const badgeMap = {
  active:'success', approved:'success', paid:'success', closed:'success', resolved:'success',
  pending:'warning', open:'info', rejected:'danger', inactive:'muted',
  high:'danger', medium:'warning', low:'success',
}
export function StatusBadge({ status }) {
  const s = String(status).toLowerCase()
  const cls = badgeMap[s] ?? 'muted'
  return <span className={`badge badge-${cls}`}>{status}</span>
}

/* ─── EmptyState ──────────────────────────────────────────────────────── */
export function EmptyState({ title = 'No data found', desc = '' }) {
  return (
    <div className="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <circle cx="12" cy="12" r="10"/><path d="M8 12h8M12 8v8"/>
      </svg>
      <h3>{title}</h3>
      {desc && <p>{desc}</p>}
    </div>
  )
}

/* ─── SearchInput ─────────────────────────────────────────────────────── */
export function SearchInput({ value, onChange, placeholder = 'Search…' }) {
  return (
    <div className="search-input-wrap">
      <Search size={14} className="search-icon" />
      <input
        className="field input"
        style={{paddingLeft:34, background:'var(--c-surface3)', border:'1px solid var(--c-border)', borderRadius:'var(--radius-sm)', color:'var(--c-text)', padding:'9px 14px 9px 34px', outline:'none'}}
        placeholder={placeholder}
        value={value}
        onChange={e => onChange(e.target.value)}
      />
    </div>
  )
}

/* ─── Field ───────────────────────────────────────────────────────────── */
export function Field({ label, children, className = '' }) {
  return (
    <div className={`field ${className}`}>
      {label && <label>{label}</label>}
      {children}
    </div>
  )
}
export function Input({ label, ...p }) {
  return <Field label={label}><input {...p} /></Field>
}
export function Select({ label, children, ...p }) {
  return <Field label={label}><select {...p}>{children}</select></Field>
}
export function Textarea({ label, ...p }) {
  return <Field label={label}><textarea {...p} /></Field>
}

/* ─── Pagination ──────────────────────────────────────────────────────── */
export function Pagination({ meta, onPage }) {
  if (!meta || meta.last_page <= 1) return null
  const { current_page: cur, last_page: last } = meta
  return (
    <div className="pagination">
      <button onClick={() => onPage(cur - 1)} disabled={cur === 1}><ChevronLeft size={14}/></button>
      {Array.from({ length: last }, (_, i) => i + 1).map(p => (
        <button key={p} className={cur === p ? 'active' : ''} onClick={() => onPage(p)}>{p}</button>
      ))}
      <button onClick={() => onPage(cur + 1)} disabled={cur === last}><ChevronRight size={14}/></button>
    </div>
  )
}

/* ─── Modal ───────────────────────────────────────────────────────────── */
export function Modal({ open, onClose, title, children, size = '' }) {
  if (!open) return null
  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className={`modal ${size}`} role="dialog" aria-modal="true">
        <div className="modal-header">
          <h2>{title}</h2>
          <button className="btn-icon" onClick={onClose} aria-label="Close"><X size={16}/></button>
        </div>
        {children}
      </div>
    </div>
  )
}

/* ─── Confirm ─────────────────────────────────────────────────────────── */
export function Confirm({ open, onClose, onConfirm, title = 'Are you sure?', message = 'This action cannot be undone.', loading }) {
  if (!open) return null
  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal" style={{maxWidth:420}} role="alertdialog">
        <div style={{display:'flex',gap:14,alignItems:'flex-start'}}>
          <div style={{background:'rgba(239,68,68,.15)',borderRadius:10,padding:10,flexShrink:0}}>
            <AlertTriangle size={22} color="var(--c-danger)"/>
          </div>
          <div>
            <h2 style={{fontSize:'1rem',marginBottom:6}}>{title}</h2>
            <p style={{color:'var(--c-muted)',fontSize:'.875rem'}}>{message}</p>
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-danger" onClick={onConfirm} disabled={loading}>
            {loading ? 'Deleting…' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  )
}
