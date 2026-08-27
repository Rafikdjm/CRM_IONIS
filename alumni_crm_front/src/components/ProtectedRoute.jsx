import { Navigate } from 'react-router-dom';
import { loginAPI } from '../services/api';

const isTokenExpired = (token) => {
  try {
    const payload = token.split('.')[1];
    const decoded = decodeURIComponent(
      atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join(''),
    );
    const { exp } = JSON.parse(decoded);
    if (!exp) return false;
    return Date.now() >= exp * 1000;
  } catch {
    return true;
  }
};

export default function ProtectedRoute({ children, requireAlumni = false, requireAdmin = false }) {
  const token = localStorage.getItem('token');

  if (requireAlumni) {
    const user = loginAPI.getCurrentUser();
    if (!user || !token || isTokenExpired(token)) {
      return <Navigate to="/" replace />;
    }
  }

  if (requireAdmin) {
    if (!token || !loginAPI.isAdmin() || isTokenExpired(token)) {
      return <Navigate to="/" replace />;
    }
  }

  return children;
}
