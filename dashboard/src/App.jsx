import { HashRouter, Routes, Route } from 'react-router-dom'
import { DataProvider } from './context/DataContext'
import { useData } from './context/DataContext'
import Sidebar from './components/layout/Sidebar'
import TopBar from './components/layout/TopBar'
import Spinner from './components/ui/Spinner'
import ExecutiveSummary from './pages/ExecutiveSummary'
import InventoryHealth from './pages/InventoryHealth'
import DemandForecast from './pages/DemandForecast'
import AnomaliesSuppliers from './pages/AnomaliesSuppliers'
import { C } from './utils/colors'

function Shell() {
  const { isLoading, errors } = useData()

  const now = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* Header */}
        <div style={{
          background: C.surface,
          borderBottom: `1px solid ${C.border}`,
          padding: '12px 28px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: C.text }}>FlowSight — Supply Chain Intelligence Platform</div>
          <div style={{ fontSize: 11, color: C.subtle }}>Data as of {now}</div>
        </div>
        {/* Content */}
        <main style={{ flex: 1, padding: '20px 28px', maxWidth: 1600, width: '100%', margin: '0 auto' }}>
          {errors.length > 0 && (
            <div style={{ background: `${C.red}18`, border: `1px solid ${C.red}`, borderRadius: 8, padding: '12px 16px', marginBottom: 16, color: C.red, fontSize: 12 }}>
              <b>Data load error:</b> {errors.join(', ')} — run <code>python scripts/run_all.py</code> then <code>npm run build</code>
            </div>
          )}
          {isLoading ? <Spinner /> : (
            <>
              <TopBar />
              <Routes>
                <Route path="/"          element={<ExecutiveSummary />} />
                <Route path="/inventory" element={<InventoryHealth />} />
                <Route path="/forecast"  element={<DemandForecast />} />
                <Route path="/anomalies" element={<AnomaliesSuppliers />} />
              </Routes>
            </>
          )}
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <HashRouter>
      <DataProvider>
        <Shell />
      </DataProvider>
    </HashRouter>
  )
}
