import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
 
const LoginPage = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { login, cargando, error } = useAuth()
  const navigate = useNavigate()
 
  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await login(email, password)
      navigate('/laboratorios')
    } catch {}
  }
 
  return (
    <div style={s.bg}>
      <div style={s.card}>
        <div style={s.iconWrap}>🔬</div>
        <h1 style={s.title}>Bienvenido</h1>
        <p style={s.sub}>Sistema de reservas de laboratorios</p>
 
        {error && <div style={s.error} data-testid="login-error">{error}</div>}
 
        <form onSubmit={handleSubmit}>
          <label htmlFor="login-email" style={s.label}>Correo institucional</label>
          <input
            id="login-email"
            style={s.input}
            type="email"
            placeholder="usuario@universidad.edu"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <label htmlFor="login-pwd" style={s.label}>Contraseña</label>
          <input
            id="login-pwd"
            style={s.input}
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button style={s.btn} type="submit" disabled={cargando}>
            {cargando ? 'Iniciando sesión...' : 'Iniciar sesión'}
          </button>
        </form>
      </div>
    </div>
  )
}
 
const s = {
  bg: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f0f2f5' },
  card: { background: '#fff', borderRadius: 12, padding: '36px 32px', width: 340, boxShadow: '0 2px 16px rgba(0,0,0,0.08)' },
  iconWrap: { fontSize: 36, textAlign: 'center', marginBottom: 12 },
  title: { fontSize: 22, fontWeight: 600, margin: '0 0 4px', textAlign: 'center', color: '#1a1a2e' },
  sub: { fontSize: 13, color: '#666', textAlign: 'center', margin: '0 0 24px' },
  label: { display: 'block', fontSize: 12, color: '#555', marginBottom: 4 },
  input: { width: '100%', padding: '9px 12px', border: '1px solid #ddd', borderRadius: 8, fontSize: 14, marginBottom: 14, boxSizing: 'border-box', outline: 'none' },
  btn: { width: '100%', padding: 10, background: '#185FA5', color: '#fff', border: 'none', borderRadius: 8, fontSize: 14, fontWeight: 500, cursor: 'pointer', marginTop: 4 },
  error: { background: '#fef2f2', color: '#dc2626', padding: '10px 12px', borderRadius: 8, fontSize: 13, marginBottom: 14 },
}
 
export default LoginPage