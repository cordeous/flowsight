import { HashRouter, Routes, Route, useLocation } from 'react-router-dom'
import { DataProvider } from './context/DataContext'
import { useData } from './context/DataContext'
import Sidebar from './components/layout/Sidebar'
import TopBar from './components/layout/TopBar'
import ExportWidget from './components/ui/ExportWidget'
import Spinner from './components/ui/Spinner'
import ExecutiveSummary from './pages/ExecutiveSummary'
import InventoryHealth from './pages/InventoryHealth'
import DemandForecast from './pages/DemandForecast'
import AnomaliesSuppliers from './pages/AnomaliesSuppliers'
import { C } from './utils/colors'
import React, { useState } from 'react'

function Shell() {
  const { isLoading, errors } = useData()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()

  const pageTitle = location.pathname === '/' ? 'Executive Summary' :
    location.pathname === '/inventory' ? 'Inventory Health' :
      location.pathname === '/forecast' ? 'Demand Forecast' :
        'Anomalies & Suppliers'

  const now = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-800 font-sans selection:bg-indigo-500/30">
      <Sidebar mobileMenuOpen={mobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen} />

      <div id="pdf-capture-zone" className="flex-1 flex flex-col min-w-0 min-h-screen">
        {/* Header */}
        <div className="bg-white border-b border-slate-200 px-4 md:px-8 py-3.5 flex flex-wrap justify-between items-center sticky top-0 z-20 shadow-sm gap-4">
          <div className="flex items-center gap-3">
            <button
              className="md:hidden p-2 -ml-2 text-slate-500 hover:text-indigo-600 rounded-lg hover:bg-slate-100 transition-colors"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            </button>
            <div className="text-sm md:text-lg font-extrabold text-slate-800 tracking-tight">{pageTitle}</div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-xs text-slate-400 hidden sm:flex items-center gap-2">
              <span>Data as of:</span>
              <span className="bg-slate-50 px-2 py-1 rounded border border-slate-200 text-slate-600 font-medium">{now}</span>
            </div>
            <ExportWidget pageTitle={pageTitle} />
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 p-4 md:p-8 max-w-[1600px] w-full mx-auto">
          {errors.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 text-red-700 text-sm flex items-start gap-3">
              <span className="text-xl">⚠️</span>
              <div>
                <strong className="block mb-1">Data load error</strong>
                {errors.join(', ')} — run <code className="bg-red-100 px-1.5 py-0.5 rounded mx-1">python scripts/run_all.py</code> then <code className="bg-red-100 px-1.5 py-0.5 rounded mx-1">npm run build</code>
              </div>
            </div>
          )}

          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Spinner />
            </div>
          ) : (
            <div className="animate-in fade-in duration-500 slide-in-from-bottom-4">
              <TopBar />
              <Routes>
                <Route path="/" element={<ExecutiveSummary />} />
                <Route path="/inventory" element={<InventoryHealth />} />
                <Route path="/forecast" element={<DemandForecast />} />
                <Route path="/anomalies" element={<AnomaliesSuppliers />} />
              </Routes>
            </div>
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
