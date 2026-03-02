import { useState, useEffect } from 'react'
import Papa from 'papaparse'

export function useCSVData(filename) {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    const url = `${import.meta.env.BASE_URL}data/${filename}`
    Papa.parse(url, {
      download: true,
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results) => { setData(results.data); setLoading(false) },
      error: (err)       => { setError(err.message);  setLoading(false) },
    })
  }, [filename])

  return { data, loading, error }
}
