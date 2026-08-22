import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import LoadingSpinner from './components/shared/LoadingSpinner';

const AuthPage = lazy(() => import('./components/AuthPage'));
const AdminLayout = lazy(() => import('./components/admin/AdminLayout'));
const AdminDashboard = lazy(() => import('./components/admin/AdminDashboard'));
const AlumniDirectory = lazy(() => import('./components/admin/AlumniDirectory'));
const ExcelImport = lazy(() => import('./components/admin/ExcelImport'));
const AdminQuestionnaires = lazy(() => import('./components/admin/AdminQuestionnaires'));
const AdminPromotions = lazy(() => import('./components/admin/AdminPromotions'));
const AdminRgpdDemandes = lazy(() => import('./components/admin/AdminRgpdDemandes'));
const AlumniLayout = lazy(() => import('./components/alumni/AlumniLayout'));
const AlumniRegistration = lazy(() => import('./components/alumni/AlumniRegistration'));
const AlumniProfile = lazy(() => import('./components/alumni/AlumniProfile'));
const AlumniCareer = lazy(() => import('./components/alumni/AlumniCareer'));
const AlumniConsent = lazy(() => import('./components/alumni/AlumniConsent'));
const AlumniSurvey = lazy(() => import('./components/alumni/AlumniSurvey'));

export default function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
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
    </Suspense>
  );
}
