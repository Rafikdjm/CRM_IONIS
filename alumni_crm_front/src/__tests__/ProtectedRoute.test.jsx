import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import ProtectedRoute from '../components/ProtectedRoute'
import { loginAPI } from '../services/api'

vi.mock('../services/api', () => ({
  loginAPI: {
    getCurrentUser: vi.fn(),
    isAdmin: vi.fn(),
    logout: vi.fn(),
    requestOTP: vi.fn(),
    verifyOTP: vi.fn(),
  },
}))

beforeEach(() => {
  vi.clearAllMocks()
})

function renderWithRouter(ui, { route = '/' } = {}) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      {ui}
    </MemoryRouter>
  )
}

describe('ProtectedRoute', () => {
  describe('requireAlumni', () => {
    it('redirects to / when no token', () => {
      loginAPI.getCurrentUser.mockReturnValue(null)

      renderWithRouter(
        <ProtectedRoute requireAlumni>
          <div>Protected Content</div>
        </ProtectedRoute>
      )

      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
    })

    it('redirects to / when no user', () => {
      localStorage.setItem('token', 'tok')
      loginAPI.getCurrentUser.mockReturnValue(null)

      renderWithRouter(
        <ProtectedRoute requireAlumni>
          <div>Protected Content</div>
        </ProtectedRoute>
      )

      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
    })

    it('renders children when authenticated as alumni', () => {
      localStorage.setItem('token', 'tok')
      loginAPI.getCurrentUser.mockReturnValue({ id: '1', email: 'e@e.com', name: 'Test' })

      renderWithRouter(
        <ProtectedRoute requireAlumni>
          <div>Alumni Content</div>
        </ProtectedRoute>
      )

      expect(screen.getByText('Alumni Content')).toBeInTheDocument()
    })
  })

  describe('requireAdmin', () => {
    it('redirects to / when no token', () => {
      loginAPI.isAdmin.mockReturnValue(false)

      renderWithRouter(
        <ProtectedRoute requireAdmin>
          <div>Admin Content</div>
        </ProtectedRoute>
      )

      expect(screen.queryByText('Admin Content')).not.toBeInTheDocument()
    })

    it('redirects to / when not admin', () => {
      localStorage.setItem('token', 'tok')
      loginAPI.isAdmin.mockReturnValue(false)

      renderWithRouter(
        <ProtectedRoute requireAdmin>
          <div>Admin Content</div>
        </ProtectedRoute>
      )

      expect(screen.queryByText('Admin Content')).not.toBeInTheDocument()
    })

    it('renders children when authenticated as admin', () => {
      localStorage.setItem('token', 'tok')
      loginAPI.isAdmin.mockReturnValue(true)

      renderWithRouter(
        <ProtectedRoute requireAdmin>
          <div>Admin Content</div>
        </ProtectedRoute>
      )

      expect(screen.getByText('Admin Content')).toBeInTheDocument()
    })
  })
})
