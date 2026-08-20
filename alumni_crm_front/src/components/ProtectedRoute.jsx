import { Navigate } from 'react-router-dom';
import { loginAPI } from '../services/api';

export default function ProtectedRoute({ children, requireAlumni = false, requireAdmin = false }) {
  const token = localStorage.getItem('token');

  if (requireAlumni) {
    const user = loginAPI.getCurrentUser();
    if (!user || !token) {
      return <Navigate to="/" replace />;
    }
  }

  if (requireAdmin) {
    if (!token || !loginAPI.isAdmin()) {
      return <Navigate to="/" replace />;
    }
  }

  return children;
}
