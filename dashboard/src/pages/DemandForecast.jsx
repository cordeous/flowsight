import { useMemo, useState } from 'react'
import { useData } from '../context/DataContext'
import KpiCard from '../components/ui/KpiCard'
import SectionTitle from '../components/ui/SectionTitle'
import Card from '../components/ui/Card'
import ForecastTimelineChart from '../components/charts/ForecastTimelineChart'
import ConfidenceBandChart from '../components/charts/ConfidenceBandChart'
import ForecastCategoryBar from '../components/charts/ForecastCategoryBar'
import { C } from '../utils/colors'
import { fmtPct, fmtNum } from '../utils/fmt'

export default function DemandForecast() {
  const { forecast, evaluation } = useData()
  const [horizon, setHorizon] = useState(30)
  const [selectedProduct, setSelectedProduct] = useState(null)

  const products = useMemo(() => {
    if (!forecast) return []
    const map = {}
    forecast.forEach(r => { map[r.ProductID] = r.ProductName })
    return Object.entries(map).map(([id, name]) => ({ id: Number(id), name })).sort((a, b) => a.id - b.id)
  }, [forecast])

  const effectiveProduct = selectedProduct ?? products[0]?.id

  const kpis = useMemo(() => {
    if (!evaluation || !forecast) return null
    const arimaRows = evaluation.filter(r => r.ModelName === 'ARIMA')
    const hwRows = evaluation.filter(r => r.ModelName === 'HoltWinters')
    const arimaMAPE = arimaRows.reduce((s, r) => s + r.MAPE, 0) / (arimaRows.length || 1)
    const hwMAPE = hwRows.reduce((s, r) => s + r.MAPE, 0) / (hwRows.length || 1)
    const forecastedProducts = new Set(forecast.map(r => r.ProductID)).size
    const total30d = forecast.filter(r => r.HorizonDays === 30 && r.ModelName === 'ARIMA')
      .reduce((s, r) => s + r.ForecastQty, 0)
    return { arimaMAPE, hwMAPE, forecastedProducts, total30d }
  }, [evaluation, forecast])

  const modelRows = useMemo(() => {
    if (!evaluation) return []
    const map = {}
    evaluation.forEach(r => {
      if (!map[r.ModelName]) map[r.ModelName] = { model: r.ModelName, mae: [], rmse: [], mape: [] }
      map[r.ModelName].mae.push(r.MAE)
      map[r.ModelName].rmse.push(r.RMSE)
      map[r.ModelName].mape.push(r.MAPE)
    })
    return Object.values(map).map(d => ({
      model: d.model,
      MAE: (d.mae.reduce((a, b) => a + b, 0) / d.mae.length).toFixed(2),
      RMSE: (d.rmse.reduce((a, b) => a + b, 0) / d.rmse.length).toFixed(2),
      MAPE: ((d.mape.reduce((a, b) => a + b, 0) / d.mape.length) * 100).toFixed(1) + '%',
    }))
  }, [evaluation])

  const btnStyle = (active) => `
    px-4 py-1.5 text-xs font-semibold rounded-lg border transition-all duration-200
    ${active
      ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-500/20'
      : 'bg-transparent border-slate-200 text-slate-600 hover:text-indigo-600 hover:bg-white'
    }
  `

  return (
    <div className="space-y-6">
      <SectionTitle>Forecast Accuracy KPIs</SectionTitle>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard icon="🎯" label="ARIMA MAPE" value={fmtPct(kpis?.arimaMAPE * 100, 1)} accentColor="#0d6efd"
          sub="Mean Absolute % Error (lower = better)" />
        <KpiCard icon="📈" label="Holt-Winters MAPE" value={fmtPct(kpis?.hwMAPE * 100, 1)} accentColor="#fd7e14"
          sub="Mean Absolute % Error (lower = better)" />
        <KpiCard icon="📦" label="Forecasted Products" value={kpis?.forecastedProducts ?? '—'} accentColor="#198754" />
        <KpiCard icon="🔮" label="Total 30-Day Demand" value={fmtNum(kpis?.total30d)} accentColor="indigo"
          sub="ARIMA forecast across all products" />
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-4 bg-white/50 p-4 rounded-xl border border-slate-200 backdrop-blur-md">
        <div className="flex gap-2 bg-slate-100/80 p-1 rounded-xl">
          {[30, 60, 90].map(h => (
            <button key={h} onClick={() => setHorizon(h)} className={btnStyle(horizon === h)}>{h}d</button>
          ))}
        </div>

        <div className="flex-1 min-w-[200px] max-w-sm ml-auto">
          <select
            value={effectiveProduct ?? ''}
            onChange={e => setSelectedProduct(Number(e.target.value))}
            className="w-full bg-white border border-slate-200 text-slate-700 hover:border-indigo-300 text-sm rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all cursor-pointer shadow-sm"
          >
            {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
      </div>

      <SectionTitle>Fleet Forecast</SectionTitle>
      <div className="mb-6">
        <ForecastTimelineChart forecast={forecast} horizon={horizon} />
      </div>

      <SectionTitle>Product Forecast with Confidence Band</SectionTitle>
      <div className="mb-6">
        <ConfidenceBandChart forecast={forecast} productId={effectiveProduct} horizon={horizon} />
      </div>

      <SectionTitle>Forecast by Category &amp; Model Accuracy</SectionTitle>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
        <ForecastCategoryBar forecast={forecast} horizon={horizon} />

        <Card className="flex flex-col h-full">
          <div className="font-bold text-sm text-slate-700 mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Model Accuracy Comparison
          </div>

          <div className="flex-1 overflow-x-auto">
            <table className="w-full text-sm text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200">
                  {['Model', 'MAE', 'RMSE', 'MAPE'].map((h, i) => (
                    <th key={h} className={`px-4 py-3 bg-slate-50/80 text-xs font-bold tracking-wider uppercase text-slate-500 ${i > 0 ? 'text-right' : ''}`}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {modelRows.map((row, i) => (
                  <tr key={row.model} className="hover:bg-indigo-50/50 transition-colors group">
                    <td className="px-4 py-3 font-medium text-slate-800">{row.model}</td>
                    <td className="px-4 py-3 text-right text-slate-600 group-hover:text-indigo-900 transition-colors">{row.MAE}</td>
                    <td className="px-4 py-3 text-right text-slate-600 group-hover:text-indigo-900 transition-colors">{row.RMSE}</td>
                    <td className={`px-4 py-3 text-right font-bold tracking-wide ${i === 0 ? 'text-emerald-600' : 'text-amber-600'}`}>
                      {row.MAPE}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 text-xs text-slate-500 border-t border-slate-100 pt-3">
            <span className="inline-block w-2 h-2 rounded-sm bg-slate-700 mr-2"></span>
            Walk-forward backtest with 90-day holdout. Lower MAPE = better accuracy.
          </div>
        </Card>
      </div>
    </div>
  )
}
