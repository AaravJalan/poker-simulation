import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import './Layout.css'

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  return (
    <div className="layout">
      <button
        type="button"
        className="layout-menu-btn"
        onClick={() => setSidebarOpen((v) => !v)}
        title="Menu"
        aria-label="Toggle menu"
      >
        &#9776;
      </button>
      <div className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`} onClick={() => setSidebarOpen(false)} aria-hidden="true" />
      <aside className={`layout-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <Sidebar onNav={() => setSidebarOpen(false)} />
      </aside>
      <main className="layout-main" onClick={() => setSidebarOpen(false)}>
        <Outlet />
      </main>
    </div>
  )
}
