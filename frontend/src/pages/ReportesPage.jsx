import { useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import {
  getUsoLaboratorio,
  getOcupacionMensual,
  getReporteDocente,
  descargarUsoCSV,
  descargarDocenteCSV,
} from '../services/reportes'

const TABS = ['Uso por laboratorio', 'Ocupación mensual', 'Por docente']

const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]

const ReportesPage = () => {
  const [tab, setTab] = useState(0)
  const [datos, setDatos] = useState([])
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  // Filtros uso / docente
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')

  // Filtros ocupación mensual
  const now = new Date()
  const [mes, setMes] = useState(now.getMonth() + 1)
  const [anio, setAnio] = useState(now.getFullYear())

  const buildFechaParams = () => {
    const params = {}
    if (fechaDesde) params.fecha_desde = fechaDesde
    if (fechaHasta) params.fecha_hasta = fechaHasta
    return params
  }

  const cargar = async () => {
    setCargando(true)
    setError(null)
    setDatos([])

    try {
      let response
      if (tab === 1) {
        response = await getOcupacionMensual(mes, anio)
      } else if (tab === 0) {
        response = await getUsoLaboratorio(buildFechaParams())
      } else {
        response = await getReporteDocente(buildFechaParams())
      }
      setDatos(Array.isArray(response) ? response : [])

    } catch (err) {
      console.error(err)
      setError(err?.response?.data?.detail || err?.message || 'Error al cargar el reporte')

    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
  }, [tab])

  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Navbar />

      <div style={{ padding: 24 }}>

        <div style={s.header}>
          <h2 style={s.title}>Reportes</h2>
        </div>

        <div style={s.tabs}>
          {TABS.map((t) => (
            <button
              key={t}
              style={{
                ...s.tab,
                ...(tab === i ? s.tabActive : {})
              }}
              onClick={() => setTab(i)}
            >
              {t}
            </button>
          ))}
        </div>

        <div style={s.filtrosRow}>

          {tab === 1 ? (
            <>
              <div>
                <label htmlFor="reporte-mes" style={s.label}>Mes</label>

                <select
                  id="reporte-mes"
                  style={s.input}
                  value={mes}
                  onChange={e => setMes(Number(e.target.value))}
                >
                  {MESES.map((m, i) => (
                    <option key={m} value={i + 1}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="reporte-anio" style={s.label}>Año</label>

                <input
                  id="reporte-anio"
                  style={s.input}
                  type="number"
                  value={anio}
                  onChange={e => setAnio(Number(e.target.value))}
                  min="2000"
                  max="2100"
                />
              </div>
            </>
          ) : (
            <>
              <div>
                <label htmlFor="reporte-desde" style={s.label}>Fecha desde</label>

                <input
                  id="reporte-desde"
                  style={s.input}
                  type="date"
                  value={fechaDesde}
                  onChange={e => setFechaDesde(e.target.value)}
                />
              </div>

              <div>
                <label htmlFor="reporte-hasta" style={s.label}>Fecha hasta</label>

                <input
                  id="reporte-hasta"
                  style={s.input}
                  type="date"
                  value={fechaHasta}
                  onChange={e => setFechaHasta(e.target.value)}
                />
              </div>
            </>
          )}

          <button style={s.btnBuscar} onClick={cargar}>
            Buscar
          </button>

          {tab === 0 && (
            <button
              style={s.btnCSV}
              onClick={() => {
                const params = {}

                if (fechaDesde) {
                  params.fecha_desde = fechaDesde
                }

                if (fechaHasta) {
                  params.fecha_hasta = fechaHasta
                }

                descargarUsoCSV(params)
              }}
            >
              ⬇ CSV
            </button>
          )}

          {tab === 2 && (
            <button
              style={s.btnCSV}
              onClick={() => {
                const params = {}

                if (fechaDesde) {
                  params.fecha_desde = fechaDesde
                }

                if (fechaHasta) {
                  params.fecha_hasta = fechaHasta
                }

                descargarDocenteCSV(params)
              }}
            >
              ⬇ CSV
            </button>
          )}

        </div>

        {error && (
          <div style={s.error}>
            {typeof error === 'string'
              ? error
              : JSON.stringify(error)}
          </div>
        )}

        {cargando && (
          <p style={s.msg}>Cargando...</p>
        )}

        {!cargando && datos.length === 0 && !error && (
          <p style={s.msg}>
            No hay datos para mostrar.
          </p>
        )}

        {!cargando && datos.length > 0 && (
          <div style={s.tableWrap}>

            <table style={s.table}>

              <thead>
                <tr style={s.thead}>

                  {tab === 0 && (
                    <>
                      <th style={s.th}>Laboratorio</th>
                      <th style={s.th}>Total reservas</th>
                      <th style={s.th}>Horas ocupadas</th>
                      <th style={s.th}>Canceladas</th>
                    </>
                  )}

                  {tab === 1 && (
                    <>
                      <th style={s.th}>Laboratorio</th>
                      <th style={s.th}>Mes</th>
                      <th style={s.th}>Total reservas</th>
                      <th style={s.th}>% Ocupación</th>
                    </>
                  )}

                  {tab === 2 && (
                    <>
                      <th style={s.th}>Email</th>
                      <th style={s.th}>Total reservas</th>
                      <th style={s.th}>Labs usados</th>
                      <th style={s.th}>Última reserva</th>
                    </>
                  )}

                </tr>
              </thead>

              <tbody>

                {datos.map((d, i) => (

                  <tr key={d.laboratorio_id ?? d.email ?? i} style={s.tr}>

                    {tab === 0 && (
                      <>
                        <td style={s.td}>
                          {d.nombre || '—'}
                        </td>

                        <td style={s.td}>
                          {Number(d.total_reservas || 0)}
                        </td>

                        <td style={s.td}>
                          {Number(d.horas_ocupadas || 0).toFixed(1)} h
                        </td>

                        <td style={s.td}>
                          <span
                            style={{
                              ...s.badge,
                              background:
                                Number(d.reservas_canceladas || 0) > 0
                                  ? '#fef2f2'
                                  : '#f0fdf4',
                              color:
                                Number(d.reservas_canceladas || 0) > 0
                                  ? '#dc2626'
                                  : '#166534'
                            }}
                          >
                            {Number(d.reservas_canceladas || 0)}
                          </span>
                        </td>
                      </>
                    )}

                    {tab === 1 && (
                      <>
                        <td style={s.td}>
                          {d.nombre || '—'}
                        </td>

                        <td style={s.td}>
                          {MESES[(d.mes || 1) - 1]} {d.anio || ''}
                        </td>

                        <td style={s.td}>
                          {Number(d.total_reservas || 0)}
                        </td>

                        <td style={s.td}>
                          <div style={s.barWrap}>

                            <div
                              style={{
                                ...s.bar,
                                width: `${Math.min(
                                  Number(d.porcentaje_ocupacion || 0),
                                  100
                                )}%`
                              }}
                            />

                            <span style={s.barLabel}>
                              {Number(
                                d.porcentaje_ocupacion || 0
                              ).toFixed(1)}%
                            </span>

                          </div>
                        </td>
                      </>
                    )}

                    {tab === 2 && (
                      <>
                        <td style={s.td}>
                          {d.email || '—'}
                        </td>

                        <td style={s.td}>
                          {Number(d.total_reservas || 0)}
                        </td>

                        <td style={s.td}>
                          {Number(d.laboratorios_usados || 0)}
                        </td>

                        <td style={s.td}>
                          {d.ultima_reserva || '—'}
                        </td>
                      </>
                    )}

                  </tr>

                ))}

              </tbody>

            </table>

          </div>
        )}

      </div>
    </div>
  )
}

const s = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16
  },

  title: {
    fontSize: 20,
    fontWeight: 600,
    margin: 0,
    color: '#1a1a2e'
  },

  tabs: {
    display: 'flex',
    gap: 4,
    marginBottom: 18,
    borderBottom: '1px solid #e5e7eb',
    paddingBottom: 0
  },

  tab: {
    padding: '8px 18px',
    background: 'none',
    border: 'none',
    borderBottom: '2px solid transparent',
    fontSize: 13,
    color: '#666',
    cursor: 'pointer',
    marginBottom: -1
  },

  tabActive: {
    color: '#185FA5',
    borderBottomColor: '#185FA5',
    fontWeight: 500
  },

  filtrosRow: {
    display: 'flex',
    alignItems: 'flex-end',
    gap: 12,
    marginBottom: 18,
    flexWrap: 'wrap'
  },

  label: {
    display: 'block',
    fontSize: 12,
    color: '#555',
    marginBottom: 4
  },

  input: {
    padding: '8px 12px',
    border: '1px solid #ddd',
    borderRadius: 8,
    fontSize: 13,
    background: '#fff'
  },

  btnBuscar: {
    padding: '8px 18px',
    background: '#185FA5',
    color: '#fff',
    border: 'none',
    borderRadius: 8,
    fontSize: 13,
    fontWeight: 500,
    cursor: 'pointer'
  },

  btnCSV: {
    padding: '8px 16px',
    background: 'transparent',
    border: '1px solid #185FA5',
    color: '#185FA5',
    borderRadius: 8,
    fontSize: 13,
    cursor: 'pointer'
  },

  tableWrap: {
    background: '#fff',
    borderRadius: 12,
    border: '1px solid #e5e7eb',
    overflow: 'hidden'
  },

  table: {
    width: '100%',
    borderCollapse: 'collapse'
  },

  thead: {
    background: '#f8fafc'
  },

  th: {
    padding: '10px 16px',
    textAlign: 'left',
    fontSize: 12,
    color: '#555',
    fontWeight: 500,
    borderBottom: '1px solid #e5e7eb'
  },

  tr: {
    borderBottom: '1px solid #f1f5f9'
  },

  td: {
    padding: '12px 16px',
    fontSize: 13,
    color: '#1a1a2e'
  },

  badge: {
    display: 'inline-block',
    padding: '3px 10px',
    borderRadius: 100,
    fontSize: 11,
    fontWeight: 500
  },

  barWrap: {
    display: 'flex',
    alignItems: 'center',
    gap: 8
  },

  bar: {
    height: 8,
    background: '#185FA5',
    borderRadius: 4,
    transition: 'width 0.3s',
    minWidth: 4
  },

  barLabel: {
    fontSize: 12,
    color: '#555',
    whiteSpace: 'nowrap'
  },

  error: {
    background: '#fef2f2',
    color: '#dc2626',
    padding: '10px 14px',
    borderRadius: 8,
    marginBottom: 14,
    fontSize: 13
  },

  msg: {
    textAlign: 'center',
    color: '#999',
    marginTop: 40,
    fontSize: 14
  },
}

export default ReportesPage