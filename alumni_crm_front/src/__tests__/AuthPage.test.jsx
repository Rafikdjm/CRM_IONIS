import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { act } from 'react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import AuthPage from '../components/AuthPage'
import { loginAPI } from '../services/api'
import { ThemeProvider } from '../contexts/ThemeContext'

vi.mock('../services/api', () => ({
  loginAPI: {
    requestOTP: vi.fn(),
    verifyOTP: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
    isAdmin: vi.fn(),
  },
}))

function renderAuthPage() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <ThemeProvider>
        <AuthPage />
      </ThemeProvider>
    </MemoryRouter>
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

afterEach(() => {
  vi.useRealTimers()
})

describe('AuthPage - Email Step', () => {
  it('renders the email input form by default', () => {
    renderAuthPage()

    expect(screen.getByLabelText(/adresse email/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /envoyer le code/i })).toBeInTheDocument()
  })

  it('disables submit button when email is empty', () => {
    renderAuthPage()

    const button = screen.getByRole('button', { name: /envoyer le code/i })
    expect(button).toBeDisabled()
  })

  it('enables submit button when email is entered', async () => {
    const user = userEvent.setup()
    renderAuthPage()

    await user.type(screen.getByLabelText(/adresse email/i), 'test@test.com')

    const button = screen.getByRole('button', { name: /envoyer le code/i })
    expect(button).toBeEnabled()
  })

  it('calls requestOTP and transitions to OTP step on success', async () => {
    const user = userEvent.setup()
    loginAPI.requestOTP.mockResolvedValueOnce({ message: 'OK' })

    renderAuthPage()

    await user.type(screen.getByLabelText(/adresse email/i), 'test@test.com')
    await user.click(screen.getByRole('button', { name: /envoyer le code/i }))

    expect(loginAPI.requestOTP).toHaveBeenCalledWith('test@test.com')

    await waitFor(() => {
      expect(screen.getByText(/saisissez le code à 6 chiffres/i)).toBeInTheDocument()
    })
  })

  it('shows error message when requestOTP fails', async () => {
    const user = userEvent.setup()
    loginAPI.requestOTP.mockRejectedValueOnce({
      response: { data: { detail: 'Email non trouvé' } },
    })

    renderAuthPage()

    await user.type(screen.getByLabelText(/adresse email/i), 'bad@test.com')
    await user.click(screen.getByRole('button', { name: /envoyer le code/i }))

    await waitFor(() => {
      expect(screen.getByText('Email non trouvé')).toBeInTheDocument()
    })
  })

  it('shows default error when no detail in response', async () => {
    const user = userEvent.setup()
    loginAPI.requestOTP.mockRejectedValueOnce(new Error('Network error'))

    renderAuthPage()

    await user.type(screen.getByLabelText(/adresse email/i), 'test@test.com')
    await user.click(screen.getByRole('button', { name: /envoyer le code/i }))

    await waitFor(() => {
      expect(screen.getByText(/impossible d'envoyer le code/i)).toBeInTheDocument()
    })
  })

  it('displays loading state during request', async () => {
    const user = userEvent.setup()
    let resolveRequest
    loginAPI.requestOTP.mockImplementation(
      () => new Promise((resolve) => { resolveRequest = resolve })
    )

    renderAuthPage()

    await user.type(screen.getByLabelText(/adresse email/i), 'test@test.com')
    await user.click(screen.getByRole('button', { name: /envoyer le code/i }))

    expect(screen.getByText(/envoi en cours/i)).toBeInTheDocument()

    resolveRequest({ message: 'OK' })
    await waitFor(() => {
      expect(screen.getByText(/saisissez le code à 6 chiffres/i)).toBeInTheDocument()
    })
  })
})

describe('AuthPage - OTP Step', () => {
  async function goToOTPStep() {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    loginAPI.requestOTP.mockResolvedValueOnce({ message: 'OK' })

    renderAuthPage()

    await user.type(screen.getByLabelText(/adresse email/i), 'test@test.com')
    await user.click(screen.getByRole('button', { name: /envoyer le code/i }))

    await screen.findByText(/saisissez le code à 6 chiffres/i)
    return user
  }

  it('displays 6 OTP input fields', async () => {
    await goToOTPStep()

    const inputs = screen.getAllByRole('textbox')
    expect(inputs).toHaveLength(6)
  })

  it('shows the email address in the subtitle', async () => {
    await goToOTPStep()

    expect(screen.getByText('test@test.com')).toBeInTheDocument()
  })

  it('starts resend cooldown at 60s', async () => {
    await goToOTPStep()

    expect(screen.getByText(/renvoyer le code dans 60s/i)).toBeInTheDocument()
  })

  it('decrements cooldown over time', async () => {
    await goToOTPStep()

    for (let i = 0; i < 5; i++) {
      await act(async () => {
        vi.advanceTimersByTime(1000)
      })
    }

    expect(screen.getByText(/renvoyer le code dans 55s/i)).toBeInTheDocument()
  })

  it('enables resend button after cooldown expires', async () => {
    await goToOTPStep()

    for (let i = 0; i < 60; i++) {
      await act(async () => {
        vi.advanceTimersByTime(1000)
      })
    }

    const resendButton = screen.getByRole('button', { name: /renvoyer le code$/i })
    expect(resendButton).toBeEnabled()
  })

  it('resends OTP and resets cooldown', async () => {
    const user = await goToOTPStep()

    for (let i = 0; i < 60; i++) {
      await act(async () => {
        vi.advanceTimersByTime(1000)
      })
    }

    loginAPI.requestOTP.mockResolvedValueOnce({ message: 'OK' })

    const resendButton = screen.getByRole('button', { name: /renvoyer le code$/i })
    expect(resendButton).toBeEnabled()

    await user.click(resendButton)

    expect(loginAPI.requestOTP).toHaveBeenCalledWith('test@test.com')
    await waitFor(() => {
      expect(screen.getByText(/renvoyer le code dans 60s/i)).toBeInTheDocument()
    })
  })

  it('shows rate-limit message and syncs cooldown when resend hits 429', async () => {
    const user = await goToOTPStep()

    for (let i = 0; i < 60; i++) {
      await act(async () => {
        vi.advanceTimersByTime(1000)
      })
    }

    loginAPI.requestOTP.mockRejectedValueOnce({
      response: {
        status: 429,
        headers: { 'retry-after': '45' },
        data: { detail: 'Trop de demandes. Réessayez dans 45 secondes.' },
      },
    })

    const resendButton = screen.getByRole('button', { name: /renvoyer le code$/i })
    expect(resendButton).toBeEnabled()

    await user.click(resendButton)

    await waitFor(() => {
      expect(screen.getByText(/réessayez dans 45 secondes/i)).toBeInTheDocument()
      expect(screen.getByText(/renvoyer le code dans 45s/i)).toBeInTheDocument()
    })
    expect(resendButton).toBeDisabled()
  })

  it('allows navigating back to email step', async () => {
    const user = await goToOTPStep()

    await user.click(screen.getByRole('button', { name: /modifier l'email/i }))

    expect(screen.getByLabelText(/adresse email/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /envoyer le code/i })).toBeInTheDocument()
  })

  it('auto-submits when all 6 digits are entered', async () => {
    const user = await goToOTPStep()

    loginAPI.verifyOTP.mockResolvedValueOnce({
      data: { token: 'jwt-123', alumni: { id_etudiant: 1, nom: 'Test', prenom: 'User', email: 'test@test.com' }, role: 'alumni' },
    })

    const inputs = screen.getAllByRole('textbox')
    for (let i = 0; i < 6; i++) {
      await user.type(inputs[i], String(i + 1))
    }

    await waitFor(() => {
      expect(loginAPI.verifyOTP).toHaveBeenCalledWith('test@test.com', '123456')
    })
  })

  it('shows error on incorrect code with remaining attempts', async () => {
    const user = await goToOTPStep()

    loginAPI.verifyOTP.mockRejectedValueOnce({
      response: { status: 400, data: { detail: 'Code incorrect. 2 tentatives restantes.' } },
    })

    const inputs = screen.getAllByRole('textbox')
    for (let i = 0; i < 6; i++) {
      await user.type(inputs[i], '0')
    }

    await waitFor(() => {
      expect(screen.getByText(/code incorrect/i)).toBeInTheDocument()
      expect(screen.getByText(/il vous reste 2 tentative/i)).toBeInTheDocument()
    })
  })

  it('handles 429 too many requests - redirects to email after 3s', async () => {
    const user = await goToOTPStep()

    loginAPI.verifyOTP.mockRejectedValueOnce({
      response: { status: 429, data: { detail: 'Trop de tentatives.' } },
    })

    const inputs = screen.getAllByRole('textbox')
    for (let i = 0; i < 6; i++) {
      await user.type(inputs[i], '9')
    }

    await waitFor(() => {
      expect(screen.getByText(/trop de tentatives/i)).toBeInTheDocument()
    })

    await act(async () => {
      vi.advanceTimersByTime(3000)
    })

    await waitFor(() => {
      expect(screen.getByLabelText(/adresse email/i)).toBeInTheDocument()
    })
  })

  it('handles 410 expired code', async () => {
    const user = await goToOTPStep()

    loginAPI.verifyOTP.mockRejectedValueOnce({
      response: { status: 410, data: { detail: 'Code expiré' } },
    })

    const inputs = screen.getAllByRole('textbox')
    for (let i = 0; i < 6; i++) {
      await user.type(inputs[i], '5')
    }

    await waitFor(() => {
      expect(screen.getByText(/code a expiré/i)).toBeInTheDocument()
      expect(screen.getByText(/renvoyer le code dans 60s/i)).toBeInTheDocument()
    })
  })

  it('calls verifyOTP for alumni on successful verification', async () => {
    const user = await goToOTPStep()

    loginAPI.verifyOTP.mockResolvedValueOnce({
      data: {
        token: 'jwt-ok',
        alumni: { id_etudiant: 42, nom: 'Dupont', prenom: 'Jean', email: 'jean@test.com' },
        role: 'alumni',
      },
    })

    const inputs = screen.getAllByRole('textbox')
    for (let i = 0; i < 6; i++) {
      await user.type(inputs[i], '1')
    }

    await waitFor(() => {
      expect(loginAPI.verifyOTP).toHaveBeenCalledWith('test@test.com', '111111')
    })
  })

  it('calls verifyOTP for admin on successful verification', async () => {
    const user = await goToOTPStep()

    loginAPI.verifyOTP.mockResolvedValueOnce({
      data: { token: 'jwt-admin', alumni: null, role: 'admin' },
    })

    const inputs = screen.getAllByRole('textbox')
    for (let i = 0; i < 6; i++) {
      await user.type(inputs[i], '2')
    }

    await waitFor(() => {
      expect(loginAPI.verifyOTP).toHaveBeenCalledWith('test@test.com', '222222')
    })
  })

  it('displays loading state during verification', async () => {
    const user = await goToOTPStep()

    let resolveVerify
    loginAPI.verifyOTP.mockImplementation(
      () => new Promise((resolve) => { resolveVerify = resolve })
    )

    const inputs = screen.getAllByRole('textbox')
    for (let i = 0; i < 6; i++) {
      await user.type(inputs[i], '3')
    }

    expect(screen.getByText(/vérification en cours/i)).toBeInTheDocument()

    resolveVerify({ data: { token: 't', alumni: null, role: 'admin' } })
  })
})
