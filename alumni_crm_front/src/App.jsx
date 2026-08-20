import { Routes, Route, Navigate } from 'react-router-dom';
import AdminLayout from './components/admin/AdminLayout';
import AdminDashboard from './components/admin/AdminDashboard';
import AlumniDirectory from './components/admin/AlumniDirectory';
import ExcelImport from './components/admin/ExcelImport';
import AdminQuestionnaires from './components/admin/AdminQuestionnaires';
import AdminPromotions from './components/admin/AdminPromotions';
import AdminRgpdDemandes from './components/admin/AdminRgpdDemandes';
import AlumniLayout from './components/alumni/AlumniLayout';
import AlumniRegistration from './components/alumni/AlumniRegistration';
import AlumniProfile from './components/alumni/AlumniProfile';
import AlumniCareer from './components/alumni/AlumniCareer';
import AlumniConsent from './components/alumni/AlumniConsent';
import AlumniSurvey from './components/alumni/AlumniSurvey';
import AuthPage from './components/AuthPage';
import ProtectedRoute from './components/ProtectedRoute';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<AuthPage />} />

      <Route
        path="/admin"
        element={
          <ProtectedRoute requireAdmin>
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<AdminDashboard />} />
        <Route path="annuaire" element={<AlumniDirectory />} />
        <Route path="promotions" element={<AdminPromotions />} />
        <Route path="demandes-rgpd" element={<AdminRgpdDemandes />} />
        <Route path="import" element={<ExcelImport />} />
        <Route path="questionnaires" element={<AdminQuestionnaires />} />
      </Route>

      <Route
        path="/alumni"
        element={
          <ProtectedRoute requireAlumni>
            <AlumniLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<AlumniProfile />} />
        <Route path="career" element={<AlumniCareer />} />
        <Route path="consent" element={<AlumniConsent />} />
        <Route path="survey" element={<AlumniSurvey />} />
      </Route>

      <Route path="/alumni/register" element={<AlumniLayout />}>
        <Route index element={<AlumniRegistration />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
