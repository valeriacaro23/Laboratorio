import PropTypes from 'prop-types'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const PrivateRoute = ({ children, roles }) => {
  const { autenticado, rol } = useAuth()
  if (!autenticado) return <Navigate to="/login" replace />
  if (roles && !roles.includes(rol)) return <Navigate to="/laboratorios" replace />
  return children
}

PrivateRoute.propTypes = {
  children: PropTypes.node.isRequired,
  roles: PropTypes.arrayOf(PropTypes.string),
}

export default PrivateRoute