import { createContext, useContext, useMemo } from 'react'
import { useCSVData } from '../hooks/useCSVData'

const DataContext = createContext(null)

export function DataProvider({ children }) {
  const sales      = useCSVData('vw_sales_trend.csv')
  const turnover   = useCSVData('vw_kpi_inventory_turnover.csv')
  const stockout   = useCSVData('vw_kpi_stockout.csv')
  const supplier   = useCSVData('vw_supplier_performance.csv')
  const forecast   = useCSVData('vw_demand_forecast.csv')
  const reorder    = useCSVData('vw_reorder_alerts.csv')
  const eoq        = useCSVData('vw_eoq_recommendations.csv')
  const anomaly    = useCSVData('vw_anomaly_summary.csv')
  const evaluation = useCSVData('vw_forecast_evaluation.csv')

  const datasets = [sales, turnover, stockout, supplier, forecast, reorder, eoq, anomaly, evaluation]
  const isLoading = datasets.some(d => d.loading)
  const errors    = datasets.filter(d => d.error).map(d => d.error)

  const value = useMemo(() => ({
    sales:      sales.data,
    turnover:   turnover.data,
    stockout:   stockout.data,
    supplier:   supplier.data,
    forecast:   forecast.data,
    reorder:    reorder.data,
    eoq:        eoq.data,
    anomaly:    anomaly.data,
    evaluation: evaluation.data,
    isLoading,
    errors,
  }), [
    sales.data, turnover.data, stockout.data, supplier.data,
    forecast.data, reorder.data, eoq.data, anomaly.data,
    evaluation.data, isLoading, errors.length,
  ])

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>
}

export const useData = () => useContext(DataContext)
