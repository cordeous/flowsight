import { useState } from 'react'
import { useData } from '../../context/DataContext'

export default function ExportWidget({ pageTitle }) {
    const { forecast, stockout, anomaly, reorder, sales } = useData()
    const [loading, setLoading] = useState(false)

    const exportPDF = async () => {
        setLoading(true)
        try {
            const html2canvas = (await import('html2canvas')).default
            const { jsPDF } = await import('jspdf')

            // Capture only the main content area (not sidebar)
            const target = document.getElementById('pdf-capture-zone') || document.body
            const canvas = await html2canvas(target, {
                scale: 1.5,
                useCORS: true,
                backgroundColor: '#f8fafc',
                logging: false,
            })

            const imgData = canvas.toDataURL('image/png')
            const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
            const pageW = pdf.internal.pageSize.getWidth()
            const pageH = pdf.internal.pageSize.getHeight()

            // Dark header bar
            pdf.setFillColor(24, 24, 27)
            pdf.rect(0, 0, pageW, 18, 'F')

            // Indigo logo badge
            pdf.setFillColor(99, 102, 241)
            pdf.roundedRect(6, 4, 10, 10, 1.5, 1.5, 'F')
            pdf.setTextColor(255, 255, 255)
            pdf.setFontSize(7)
            pdf.setFont('helvetica', 'bold')
            pdf.text('FS', 11, 10.5, { align: 'center' })

            // Page title
            pdf.setFontSize(12)
            pdf.setFont('helvetica', 'bold')
            pdf.text('FlowSight \u2014 ' + pageTitle, 20, 11)

            // Timestamp right-aligned
            pdf.setFontSize(7)
            pdf.setFont('helvetica', 'normal')
            pdf.setTextColor(161, 161, 170)
            const ts = new Date().toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' })
            pdf.text('Generated: ' + ts, pageW - 6, 11, { align: 'right' })

            // Content image
            const contentY = 20
            const availH = pageH - contentY - 8
            const imgAspect = canvas.height / canvas.width
            const imgH = Math.min(pageW * imgAspect, availH)
            pdf.addImage(imgData, 'PNG', 0, contentY, pageW, imgH)

            // Footer
            pdf.setFillColor(245, 245, 250)
            pdf.rect(0, pageH - 7, pageW, 7, 'F')
            pdf.setTextColor(120, 120, 150)
            pdf.setFontSize(6)
            pdf.text('FlowSight Supply Chain Analytics  |  Confidential', pageW / 2, pageH - 2.5, { align: 'center' })

            pdf.save('FlowSight_' + pageTitle.replace(/\s+/g, '_') + '_' + Date.now() + '.pdf')
        } catch (err) {
            console.error('PDF export failed:', err)
            alert('PDF export failed: ' + err.message)
        }
        setLoading(false)
    }

    const exportCSV = () => {
        let data = []
        if (pageTitle.includes('Executive')) data = sales || []
        else if (pageTitle.includes('Inventory')) data = reorder || []
        else if (pageTitle.includes('Forecast')) data = forecast || []
        else data = anomaly || []

        if (!data.length) { alert('No data available to export.'); return }

        const keys = Object.keys(data[0])
        const csvContent = [
            keys.join(','),
            ...data.map(row =>
                keys.map(k => '"' + String(row[k] ?? '').replace(/"/g, '""') + '"').join(',')
            )
        ].join('\n')

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = 'FlowSight_' + pageTitle.replace(/\s+/g, '_') + '.csv'
        link.click()
        URL.revokeObjectURL(url)
    }

    return (
        <div className="flex items-center gap-2">
            <button
                onClick={exportCSV}
                className="px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-200 bg-white text-slate-600 hover:text-indigo-600 hover:border-indigo-200 transition-all flex items-center gap-1.5 shadow-sm"
            >
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                        d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="hidden sm:inline">CSV</span>
            </button>

            <button
                onClick={exportPDF}
                disabled={loading}
                className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-60 disabled:cursor-wait transition-all flex items-center gap-1.5 shadow-sm"
            >
                {loading ? (
                    <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                ) : (
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                )}
                <span className="hidden sm:inline">{loading ? 'Exporting…' : 'PDF'}</span>
            </button>
        </div>
    )
}
