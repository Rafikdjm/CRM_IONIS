import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AlumniCareer from '../components/alumni/AlumniCareer'
import { careerAPI, alumniAPI } from '../services/api'

vi.mock('../services/api', () => ({
  careerAPI: {
    getByAlumni: vi.fn(),
    getCertifications: vi.fn(),
    add: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    addCertification: vi.fn(),
    deleteCertification: vi.fn(),
  },
  alumniAPI: {
    getById: vi.fn(),
  },
}))

const SAVED_CAREER = {
  id: 7,
  company: 'Acme',
  position: 'Data Engineer',
  sector: 'Informatique',
  type_contrat: 'CDI',
  start_date: '2024-01',
  end_date: '',
  salary_range: '45',
  is_current: true,
}

const SAVED_CERT = { id: 12, name: 'AWS SA', issuer: 'Amazon', date_obtained: '2024-05' }

const setupDefaultMocks = () => {
  careerAPI.getByAlumni.mockResolvedValue({ data: [] })
  careerAPI.getCertifications.mockResolvedValue({ data: [] })
  alumniAPI.getById.mockResolvedValue({ data: { availability_status: 'en_poste', is_anonymised: false } })
  careerAPI.delete.mockResolvedValue({})
  careerAPI.deleteCertification.mockResolvedValue({})
}

beforeEach(() => {
  localStorage.setItem('alumni_id', '42')
  setupDefaultMocks()
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('AlumniCareer - bouton Retirer sur les postes', () => {
  it('retire un poste non sauvegardé du formulaire sans appel API ni confirmation', async () => {
    const user = userEvent.setup()
    render(<AlumniCareer />)
    await screen.findByRole('button', { name: /Ajouter$/i })

    await user.click(screen.getByRole('button', { name: /Ajouter$/i }))
    expect(screen.getByText('Non sauvegardé')).toBeInTheDocument()
    expect(screen.getByText(/Poste #/)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /Retirer/i }))

    await waitFor(() => {
      expect(screen.queryByText(/Poste #/)).not.toBeInTheDocument()
    })
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(careerAPI.delete).not.toHaveBeenCalled()
    expect(careerAPI.add).not.toHaveBeenCalled()
  })

  it('supprime un poste déjà existant via l\'API après confirmation', async () => {
    careerAPI.getByAlumni.mockResolvedValue({ data: [SAVED_CAREER] })
    const user = userEvent.setup()
    render(<AlumniCareer />)
    await screen.findAllByText('Poste actuel')
    expect(screen.queryByText('Non sauvegardé')).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /Retirer/i }))

    const dialog = await screen.findByRole('dialog')
    expect(dialog).toHaveTextContent(/Supprimer ce poste/i)
    expect(dialog).toHaveTextContent(/irréversible/i)
    expect(careerAPI.delete).not.toHaveBeenCalled()

    await user.click(within(dialog).getByRole('button', { name: /Supprimer définitivement/i }))

    await waitFor(() => {
      expect(careerAPI.delete).toHaveBeenCalledWith('42', 7)
    })
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
      expect(screen.queryByText('Poste actuel')).not.toBeInTheDocument()
    })
  })

  it('annule la suppression d\'un poste existant sans appeler l\'API', async () => {
    careerAPI.getByAlumni.mockResolvedValue({ data: [SAVED_CAREER] })
    const user = userEvent.setup()
    render(<AlumniCareer />)
    await screen.findAllByText('Poste actuel')

    await user.click(screen.getByRole('button', { name: /Retirer/i }))
    const dialog = await screen.findByRole('dialog')
    await user.click(within(dialog).getByRole('button', { name: /Annuler/i }))

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })
    expect(careerAPI.delete).not.toHaveBeenCalled()
    expect(screen.getAllByText('Poste actuel').length).toBeGreaterThan(0)
  })

  it('bloque la suppression d\'un poste existant si le compte est anonymisé (RGPD)', async () => {
    careerAPI.getByAlumni.mockResolvedValue({ data: [SAVED_CAREER] })
    alumniAPI.getById.mockResolvedValue({ data: { availability_status: 'en_poste', is_anonymised: true } })
    const user = userEvent.setup()
    render(<AlumniCareer />)
    await screen.findAllByText('Poste actuel')

    expect(screen.getByText(/Votre compte est anonymisé \(RGPD\)/i)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /Retirer/i }))

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(careerAPI.delete).not.toHaveBeenCalled()
    expect(screen.getByText(/compte est anonymisé \(RGPD\) : la suppression est impossible/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Sauvegarder le parcours/i })).toBeDisabled()
  })

  it('bloque l\'ajout d\'un nouveau poste si le compte est anonymisé (RGPD)', async () => {
    alumniAPI.getById.mockResolvedValue({ data: { availability_status: 'en_poste', is_anonymised: true } })
    const user = userEvent.setup()
    render(<AlumniCareer />)
    await screen.findByRole('button', { name: /Ajouter$/i })

    await user.click(screen.getByRole('button', { name: /Ajouter$/i }))

    expect(screen.queryByText('Non sauvegardé')).not.toBeInTheDocument()
    expect(screen.getByText(/compte est anonymisé \(RGPD\) : toute modification est impossible/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Sauvegarder le parcours/i })).toBeDisabled()
  })
})

describe('AlumniCareer - bouton Retirer sur les certifications', () => {
  it('retire une certification non sauvegardée sans appel API', async () => {
    const user = userEvent.setup()
    render(<AlumniCareer />)
    await screen.findByRole('button', { name: /Ajouter une certification/i })

    await user.click(screen.getByRole('button', { name: /Ajouter une certification/i }))
    expect(screen.getByText('Non sauvegardée')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /Retirer/i }))

    await waitFor(() => {
      expect(screen.queryByText(/Certification #/)).not.toBeInTheDocument()
    })
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(careerAPI.deleteCertification).not.toHaveBeenCalled()
  })

  it('supprime une certification existante via l\'API après confirmation', async () => {
    careerAPI.getCertifications.mockResolvedValue({ data: [SAVED_CERT] })
    const user = userEvent.setup()
    render(<AlumniCareer />)
    await screen.findByText(/Certification #1/i)

    await user.click(screen.getByRole('button', { name: /Retirer/i }))

    const dialog = await screen.findByRole('dialog')
    expect(dialog).toHaveTextContent(/Supprimer cette certification/i)

    await user.click(within(dialog).getByRole('button', { name: /Supprimer définitivement/i }))

    await waitFor(() => {
      expect(careerAPI.deleteCertification).toHaveBeenCalledWith('42', 12)
    })
  })

  it('bloque la suppression d\'une certification existante si compte anonymisé', async () => {
    careerAPI.getCertifications.mockResolvedValue({ data: [SAVED_CERT] })
    alumniAPI.getById.mockResolvedValue({ data: { availability_status: 'en_poste', is_anonymised: true } })
    const user = userEvent.setup()
    render(<AlumniCareer />)
    await screen.findByText(/Certification #1/i)

    await user.click(screen.getByRole('button', { name: /Retirer/i }))

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(careerAPI.deleteCertification).not.toHaveBeenCalled()
  })
})
