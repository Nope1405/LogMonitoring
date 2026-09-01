import { useState } from 'react'
import {
  Monitor,
  BarChart3,
  Bell,
  Settings,
  ChevronLeft,
  ChevronRight,
  Radio,
} from 'lucide-react'

const navItems = [
  { id: 'dashboard', icon: BarChart3, label: 'Dashboard' },
  { id: 'logs', icon: Monitor, label: 'Log Explorer' },
  { id: 'alerts', icon: Bell, label: 'Alerts' },
  { id: 'settings', icon: Settings, label: 'Settings' },
]

export default function Layout({ children, wsConnected }) {
  const [collapsed, setCollapsed] = useState(false)
  const [activeNav, setActiveNav] = useState('dashboard')

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside
        style={{
          width: collapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-width)',
          height: '100vh',
          position: 'fixed',
          top: 0,
          left: 0,
          background: 'var(--bg-secondary)',
          borderRight: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          transition: 'width 0.3s ease',
          zIndex: 100,
          overflow: 'hidden',
        }}
      >
        {/* Logo */}
        <div
          style={{
            padding: collapsed ? '20px 16px' : '20px 24px',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            minHeight: '72px',
          }}
        >
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 'var(--radius-md)',
              background: 'var(--gradient-blue)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <Radio size={20} color="white" />
          </div>
          {!collapsed && (
            <div style={{ overflow: 'hidden', whiteSpace: 'nowrap' }}>
              <span style={{ fontWeight: 800, fontSize: '1.1rem' }}>Log</span>
              <span
                style={{
                  fontWeight: 800,
                  fontSize: '1.1rem',
                  background: 'var(--gradient-blue)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Moni
              </span>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav style={{ flex: 1, padding: '16px 12px' }}>
          {navItems.map((item) => (
            <button
              key={item.id}
              id={`nav-${item.id}`}
              onClick={() => setActiveNav(item.id)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: collapsed ? '12px 14px' : '12px 16px',
                marginBottom: '4px',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                background: activeNav === item.id
                  ? 'var(--accent-blue-glow)'
                  : 'transparent',
                color: activeNav === item.id
                  ? 'var(--accent-blue)'
                  : 'var(--text-secondary)',
                cursor: 'pointer',
                fontSize: '0.875rem',
                fontWeight: activeNav === item.id ? 600 : 400,
                fontFamily: 'var(--font-sans)',
                transition: 'all 0.2s ease',
                textAlign: 'left',
                whiteSpace: 'nowrap',
              }}
              onMouseEnter={(e) => {
                if (activeNav !== item.id) {
                  e.currentTarget.style.background = 'var(--bg-card-hover)'
                }
              }}
              onMouseLeave={(e) => {
                if (activeNav !== item.id) {
                  e.currentTarget.style.background = 'transparent'
                }
              }}
            >
              <item.icon size={20} style={{ flexShrink: 0 }} />
              {!collapsed && item.label}
            </button>
          ))}
        </nav>

        {/* Connection Status */}
        <div
          style={{
            padding: collapsed ? '16px 12px' : '16px 20px',
            borderTop: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}
        >
          <span className={`status-dot ${wsConnected ? 'active' : 'inactive'}`} />
          {!collapsed && (
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {wsConnected ? 'Live Connected' : 'Disconnected'}
            </span>
          )}
        </div>

        {/* Collapse Toggle */}
        <button
          id="sidebar-toggle"
          onClick={() => setCollapsed(!collapsed)}
          style={{
            position: 'absolute',
            top: '50%',
            right: '-14px',
            transform: 'translateY(-50%)',
            width: 28,
            height: 28,
            borderRadius: '50%',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-light)',
            color: 'var(--text-secondary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            zIndex: 101,
          }}
        >
          {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </aside>

      {/* Main Content */}
      <main
        className="main-content"
        style={{
          marginLeft: collapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-width)',
        }}
      >
        {children}
      </main>
    </div>
  )
}
