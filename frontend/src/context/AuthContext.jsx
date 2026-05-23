import PropTypes from 'prop-types'
import { createContext, useContext, useState } from 'react'
import { login as loginService, logout as logoutService, getMe, getCachedUsuario, isAuthenticated } from '../services/auth'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [autenticado, setAutenticado] = useState(isAuthenticated())
  const [usuario, setUsuario] = useState(getCachedUsuario)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  const login = async (email, password) => {
    setCargando(true)
    setError(null)
    try {
      await loginService(email, password)
      const me = await getMe()
      setUsuario(me)
      setAutenticado(true)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Error al iniciar sesión'
      setError(msg)
      throw err
    } finally {
      setCargando(false)
    }
  }

  const logout = () => {
    logoutService()
    setAutenticado(false)
    setUsuario(null)
  }

  return (
    <AuthContext.Provider value={{ autenticado, usuario, rol: usuario?.rol || null, login, logout, cargando, error }}>
      {children}
    </AuthContext.Provider>
  )
}

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
}

export const useAuth = () => useContext(AuthContext)
