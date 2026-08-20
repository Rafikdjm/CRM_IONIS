import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'

vi.mock('axios', () => {
  const mockAxios = {
    create: vi.fn(() => mockAxios),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  }
  return { default: mockAxios }
})

const mockedAxios = vi.mocked(axios.create())

beforeEach(() => {
  vi.clearAllMocks()
})

describe('loginAPI', () => {
  let loginAPI

  beforeEach(async () => {
    vi.resetModules()
    const api = await import('../services/api.js')
    loginAPI = api.loginAPI
  })

  describe('requestOTP', () => {
    it('sends normalized email to /auth/otp/request', async () => {
      mockedAxios.post.mockResolvedValueOnce({ data: { message: 'OK' } })

      await loginAPI.requestOTP('  User@Example.COM  ')

      expect(mockedAxios.post).toHaveBeenCalledWith('/auth/otp/request', {
        email: 'user@example.com',
      })
    })

    it('returns response data on success', async () => {
      const payload = { message: 'Code envoyé' }
      mockedAxios.post.mockResolvedValueOnce({ data: payload })

      const result = await loginAPI.requestOTP('test@test.com')
      expect(result).toEqual(payload)
    })

    it('throws on API error', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: { status: 404, data: { detail: 'Email non trouvé' } },
      })

      await expect(loginAPI.requestOTP('unknown@test.com')).rejects.toThrow()
    })
  })

  describe('verifyOTP', () => {
    it('sends normalized email and code to /auth/otp/verify', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: { token: 'jwt-123', alumni: null, role: 'admin' },
      })

      await loginAPI.verifyOTP('  Admin@Test.COM  ', '123456')

      expect(mockedAxios.post).toHaveBeenCalledWith('/auth/otp/verify', {
        email: 'admin@test.com',
        code: '123456',
      })
    })

    it('stores token in localStorage on success', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: { token: 'jwt-abc', alumni: null, role: 'admin' },
      })

      await loginAPI.verifyOTP('a@b.com', '111111')
      expect(localStorage.getItem('token')).toBe('jwt-abc')
    })

    it('stores admin_role and clears alumni keys for admin', async () => {
      localStorage.setItem('alumni_id', '42')
      localStorage.setItem('alumni_email', 'old@test.com')
      localStorage.setItem('alumni_name', 'Old Name')

      mockedAxios.post.mockResolvedValueOnce({
        data: { token: 'jwt-admin', alumni: null, role: 'admin' },
      })

      await loginAPI.verifyOTP('admin@test.com', '123456')

      expect(localStorage.getItem('admin_role')).toBe('admin')
      expect(localStorage.getItem('alumni_id')).toBeNull()
      expect(localStorage.getItem('alumni_email')).toBeNull()
      expect(localStorage.getItem('alumni_name')).toBeNull()
    })

    it('stores alumni info and clears admin_role for alumni role', async () => {
      localStorage.setItem('admin_role', 'admin')

      mockedAxios.post.mockResolvedValueOnce({
        data: {
          token: 'jwt-alumni',
          alumni: {
            id_etudiant: 99,
            nom: 'Dupont',
            prenom: 'Jean',
            email: 'jean@test.com',
          },
          role: 'alumni',
        },
      })

      const result = await loginAPI.verifyOTP('jean@test.com', '654321')

      expect(localStorage.getItem('token')).toBe('jwt-alumni')
      expect(localStorage.getItem('alumni_id')).toBe('99')
      expect(localStorage.getItem('alumni_email')).toBe('jean@test.com')
      expect(localStorage.getItem('alumni_name')).toBe('Jean Dupont')
      expect(localStorage.getItem('admin_role')).toBeNull()
      expect(result.data.role).toBe('alumni')
      expect(result.data.alumni.last_name).toBe('Dupont')
    })

    it('throws on invalid code', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: { status: 400, data: { detail: 'Code incorrect. 2 tentatives restantes.' } },
      })

      await expect(loginAPI.verifyOTP('a@b.com', '000000')).rejects.toThrow()
    })
  })

  describe('logout', () => {
    it('clears all auth keys from localStorage', () => {
      localStorage.setItem('token', 'tok')
      localStorage.setItem('admin_role', 'admin')
      localStorage.setItem('alumni_id', '1')
      localStorage.setItem('alumni_email', 'e@e.com')
      localStorage.setItem('alumni_name', 'Name')

      loginAPI.logout()

      expect(localStorage.getItem('token')).toBeNull()
      expect(localStorage.getItem('admin_role')).toBeNull()
      expect(localStorage.getItem('alumni_id')).toBeNull()
      expect(localStorage.getItem('alumni_email')).toBeNull()
      expect(localStorage.getItem('alumni_name')).toBeNull()
    })
  })

  describe('getCurrentUser', () => {
    it('returns null when no alumni_id in localStorage', () => {
      expect(loginAPI.getCurrentUser()).toBeNull()
    })

    it('returns user object from localStorage', () => {
      localStorage.setItem('alumni_id', '42')
      localStorage.setItem('alumni_email', 'test@test.com')
      localStorage.setItem('alumni_name', 'Jean Dupont')

      const user = loginAPI.getCurrentUser()
      expect(user).toEqual({
        id: '42',
        email: 'test@test.com',
        name: 'Jean Dupont',
      })
    })
  })

  describe('isAdmin', () => {
    it('returns false when no admin_role', () => {
      expect(loginAPI.isAdmin()).toBe(false)
    })

    it('returns true when admin_role is set', () => {
      localStorage.setItem('admin_role', 'admin')
      expect(loginAPI.isAdmin()).toBe(true)
    })
  })
})
