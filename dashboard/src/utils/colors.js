export const C = {
  bg:      '#0f1117',
  surface: '#1a1d27',
  border:  '#2a2d3e',
  blue:    '#0d6efd',
  green:   '#198754',
  red:     '#dc3545',
  orange:  '#fd7e14',
  grey:    '#6c757d',
  text:    '#e8eaf6',
  subtle:  '#8892b0',
  purple:  '#a855f7',
}

export const CATEGORY_COLORS = {
  'Electronics':      C.blue,
  'Industrial Parts': C.orange,
  'Packaging':        C.green,
  'Raw Materials':    C.red,
  'Office Supplies':  C.grey,
}

export const ALERT_COLORS = {
  'ORDER NOW':  C.red,
  'ORDER SOON': C.orange,
  'OK':         C.green,
}

export const SEVERITY_COLORS = {
  HIGH:   C.red,
  MEDIUM: C.orange,
  LOW:    C.subtle,
}

export const CHART_PALETTE = [C.blue, C.orange, C.green, C.red, C.purple, C.grey]

export const CHART_BASE = {
  style: { background: C.surface },
  margin: { top: 16, right: 24, left: 0, bottom: 4 },
}

export const AXIS_STYLE = {
  tick: { fill: C.subtle, fontSize: 11 },
  axisLine: { stroke: C.border },
  tickLine: { stroke: C.border },
}

export const GRID_STYLE = {
  stroke: C.border,
  strokeDasharray: '3 3',
}

export const TOOLTIP_STYLE = {
  contentStyle: {
    background: C.surface,
    border: `1px solid ${C.border}`,
    borderRadius: 8,
    color: C.text,
    fontSize: 12,
  },
  itemStyle: { color: C.text },
  labelStyle: { color: C.subtle, marginBottom: 4 },
}
