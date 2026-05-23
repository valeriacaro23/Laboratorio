import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import Navbar from '../components/Navbar'
import { getLaboratorios } from '../services/laboratorios'
import { getHorariosPorLab } from '../services/horarios'
import { crearReserva } from '../services/reservas'
 
// JS getDay(): 0=dom,1=lun,...,6=sáb
// API dia_semana: asumimos 0=lun,...,6=dom (convención ISO)
const JS_A_API = [7, 1, 2, 3, 4, 5, 6]

const NuevaReservaPage = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const labInicial = location.state?.lab || null
 
  const [labs, setLabs] = useState([])
  const [labId, setLabId] = useState(labInicial?.laboratorio_id?.toString() || '')
  const [horarios, setHorarios] = useState([])
  const [slotSel, setSlotSel] = useState(null)
  const [fecha, setFecha] = useState('')
  const [curso, setCurso] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState(null)
  const [exito, setExito] = useState(false)
 
  useEffect(() => {
    getLaboratorios().then((data) => setLabs(data.filter((l) => l.estado)))
  }, [])
 
  useEffect(() => {
    if (!labId) { setHorarios([]); setSlotSel(null); return }
    getHorariosPorLab(labId)
      .then(setHorarios)
      .catch(() => setHorarios([]))
    setSlotSel(null)
  }, [labId])
 
  // Filtrar horarios por el día de semana de la fecha elegida
  const slotsFiltrados = (() => {
    if (!fecha || horarios.length === 0) return horarios
    const diaJS = new Date(fecha + 'T12:00:00').getDay()
    const diaAPI = JS_A_API[diaJS]
    return horarios.filter((h) => h.dia_semana === diaAPI)
  })()
 
  const handleSubmit = async () => {
    if (!labId || !fecha || !curso.trim() || !slotSel) {
      setError('Completá todos los campos y seleccioná una franja horaria.')
      return
    }
    setEnviando(true)
    setError(null)
    try {
      await crearReserva({
        laboratorio_id: Number(labId),
        curso: curso.trim(),
        fecha,
        hora_inicio: slotSel.hora_inicio,
        hora_fin: slotSel.hora_fin,
      })
      setExito(true)
      setTimeout(() => navigate('/historial'), 1500)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al crear la reserva.')
    } finally {
      setEnviando(false)
    }
  }
 
  return (
    <div style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Navbar />
      <div style={{ padding: 24, maxWidth: 520, margin: '0 auto' }}>
        <h2 style={s.title}>Nueva reserva</h2>
 
        {exito && <div style={s.success}>¡Reserva creada con éxito! Redirigiendo...</div>}
        {error && <div style={s.error}>{error}</div>}
 
        <div style={s.card}>
          <label htmlFor="reserva-lab" style={s.label}>Laboratorio</label>
          <select id="reserva-lab" style={s.input} value={labId} onChange={(e) => setLabId(e.target.value)}>
            <option value="">Seleccioná un laboratorio</option>
            {labs.map((l) => (
              <option key={l.laboratorio_id} value={l.laboratorio_id}>
                {l.nombre} — {l.ubicacion} (Cap. {l.capacidad_maxima})
              </option>
            ))}
          </select>
 
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label htmlFor="reserva-fecha" style={s.label}>Fecha</label>
              <input
                id="reserva-fecha"
                style={s.input}
                type="date"
                value={fecha}
                min={new Date().toISOString().split('T')[0]}
                onChange={(e) => { setFecha(e.target.value); setSlotSel(null) }}
              />
            </div>
            <div>
              <label htmlFor="reserva-curso" style={s.label}>Curso / asignatura</label>
              <input
                id="reserva-curso"
                style={s.input}
                type="text"
                placeholder="Ej: Redes de computadores"
                value={curso}
                onChange={(e) => setCurso(e.target.value)}
              />
            </div>
          </div>
 
          <label style={s.label}>
            Franja horaria
            {fecha && labId && slotsFiltrados.length === 0 && (
              <span style={{ color: '#dc2626', marginLeft: 8, fontWeight: 400 }}>
                Sin horarios configurados para ese día
              </span>
            )}
          </label>
          <div style={s.slotGrid}>
            {!labId && (
              <p style={s.slotHint}>Seleccioná un laboratorio primero</p>
            )}
            {slotsFiltrados.map((h) => (
              <button
                key={h.horario_id}
                disabled={!h.disponible}
                style={{
                  ...s.slot,
                  ...(slotSel?.horario_id === h.horario_id ? s.slotSel : {}),
                  ...(!h.disponible ? s.slotOcc : {}),
                }}
                onClick={() => setSlotSel(h)}
                title={!h.disponible ? h.motivo_bloqueo || 'No disponible' : ''}
              >
                {h.hora_inicio.slice(0, 5)}
                <br />
                <span style={{ fontSize: 10, opacity: 0.7 }}>→ {h.hora_fin.slice(0, 5)}</span>
              </button>
            ))}
          </div>
 
          <div style={{ display: 'flex', gap: 10, marginTop: 22 }}>
            <button style={s.btnCancel} onClick={() => navigate('/laboratorios')}>
              Cancelar
            </button>
            <button style={s.btnPrimary} onClick={handleSubmit} disabled={enviando}>
              {enviando ? 'Guardando...' : 'Confirmar reserva'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
 
const s = {
  title: { fontSize: 20, fontWeight: 600, margin: '0 0 18px', color: '#1a1a2e' },
  card: { background: '#fff', borderRadius: 12, padding: 24, border: '1px solid #e5e7eb' },
  label: { display: 'block', fontSize: 12, color: '#555', fontWeight: 500, margin: '14px 0 6px' },
  input: { width: '100%', padding: '9px 12px', border: '1px solid #ddd', borderRadius: 8, fontSize: 14, boxSizing: 'border-box', background: '#fff' },
  slotGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, marginTop: 4, minHeight: 48 },
  slotHint: { color: '#999', fontSize: 13, gridColumn: '1 / -1', margin: '8px 0' },
  slot: { padding: '10px 4px', border: '1px solid #e5e7eb', borderRadius: 8, fontSize: 13, cursor: 'pointer', background: '#fff', textAlign: 'center', lineHeight: 1.4 },
  slotSel: { border: '2px solid #185FA5', color: '#185FA5', background: '#EBF3FB' },
  slotOcc: { opacity: 0.35, cursor: 'not-allowed', textDecoration: 'line-through' },
  btnCancel: { flex: 1, padding: 10, border: '1px solid #ddd', borderRadius: 8, background: '#fff', fontSize: 14, cursor: 'pointer', color: '#666' },
  btnPrimary: { flex: 2, padding: 10, background: '#185FA5', color: '#fff', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 500, cursor: 'pointer' },
  success: { background: '#f0fdf4', color: '#166534', padding: '10px 14px', borderRadius: 8, marginBottom: 14, fontSize: 13 },
  error: { background: '#fef2f2', color: '#dc2626', padding: '10px 14px', borderRadius: 8, marginBottom: 14, fontSize: 13 },
}
 
export default NuevaReservaPage