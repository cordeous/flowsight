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
    const hwRows    = evaluation.filter(r => r.ModelName === 'HoltWinters')
    const arimaMAPE = arimaRows.reduce((s, r) => s + r.MAPE, 0) / (arimaRows.length || 1)
    const hwMAPE    = hwRows.reduce((s, r)    => s + r.MAPE, 0) / (hwRows.length || 1)
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
      MAE:   (d.mae.reduce((a, b) => a + b, 0) / d.mae.length).toFixed(2),
      RMSE:  (d.rmse.reduce((a, b) => a + b, 0) / d.rmse.length).toFixed(2),
      MAPE:  ((d.mape.reduce((a, b) => a + b, 0) / d.mape.length) * 100).toFixed(1) + '%',
    }))
  }, [evaluation])

  const btnStyle = (active) => ({
    padding: '5px 14px', fontSize: 12, cursor: 'pointer', borderRadius: 6, border: `1px solid ${C.border}`,
    background: active ? C.blue : 'transparent', color: active ? '#fff' : C.subtle,
  })

  return (
    <div>
      <SectionTitle>Forecast Accuracy KPIs</SectionTitle>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 20 }}>
        <KpiCard label="ARIMA MAPE" value={fmtPct(kpis?.arimaMAPE * 100, 1)} accent={C.blue}
          sub="Mean Absolute % Error (lower = better)" />
        <KpiCard label="Holt-Winters MAPE" value={fmtPct(kpis?.hwMAPE * 100, 1)} accent={C.orange}
          sub="Mean Absolute % Error (lower = better)" />
        <KpiCard label="Forecasted Products" value={kpis?.forecastedProducts ?? '—'} accent={C.green} />
        <KpiCard label="Total 30-Day Demand" value={fmtNum(kpis?.total30d)} accent={C.purple ?? C.blue}
          sub="ARIMA forecast across all products" />
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', gap: 16, alignItems: 'center', marginBottom: 16, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', gap: 4 }}>
          {[30, 60, 90].map(h => (
            <button key={h} onClick={() => setHorizon(h)} style={btnStyle(horizon === h)}>{h}d</button>
          ))}
        </div>
        <select value={effectiveProduct ?? ''} onChange={e => setSelectedProduct(Number(e.target.value))}
          style={{ background: C.surface, border: `1px solid ${C.border}`, color: C.text,
            borderRadius: 6, padding: '5px 12px', fontSize: 12, cursor: 'pointer' }}>
          {products.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
      </div>

      <SectionTitle>Fleet Forecast</SectionTitle>
      <ForecastTimelineChart forecast={forecast} horizon={horizon} />

      <SectionTitle>Product Forecast with Confidence Band</SectionTitle>
      <ConfidenceBandChart forecast={forecast} productId={effectiveProduct} horizon={horizon} />

      <SectionTitle>Forecast by Category &amp; Model Accuracy</SectionTitle>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 20 }}>
        <ForecastCategoryBar forecast={forecast} horizon={horizon} />
        <Card>
          <div style={{ fontWeight: 600, fontSize: 14, color: C.text, marginBottom: 16 }}>Model Accuracy Comparison</div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr>
                {['Model', 'MAE', 'RMSE', 'MAPE'].map(h => (
                  <th key={h} style={{ padding: '8px 12px', textAlign: h === 'Model' ? 'left' : 'right',
                    background: C.bg, color: C.subtle, fontSize: 11, letterSpacing: '0.06em',
                    textTransform: 'uppercase', borderBottom: `1px solid ${C.border}` }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {modelRows.map((row, i) => (
                <tr key={row.model} style={{ borderBottom: `1px solid ${C.border}` }}>
                  <td style={{ padding: '10px 12px', color: C.text, fontWeight: 600 }}>{row.model}</td>
                  <td style={{ padding: '10px 12px', color: C.text, textAlign: 'right' }}>{row.MAE}</td>
                  <td style={{ padding: '10px 12px', color: C.text, textAlign: 'right' }}>{row.RMSE}</td>
                  <td style={{ padding: '10px 12px', color: i === 0 ? C.green : C.orange, textAlign: 'right', fontWeight: 700 }}>{row.MAPE}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: 16, fontSize: 11, color: C.subtle }}>
            Walk-forward backtest with 90-day holdout. Lower MAPE = better accuracy.
          </div>
        </Card>
      </div>
    </div>
  )
}
