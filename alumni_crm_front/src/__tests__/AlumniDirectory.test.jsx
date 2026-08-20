import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AlumniDirectory from '../components/admin/AlumniDirectory'
import { alumniAPI, promotionsAPI } from '../services/api'

vi.mock('../services/api', () => ({
  alumniAPI: {
    getAll: vi.fn(),
    getById: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    anonymise: vi.fn(),
  },
  promotionsAPI: {
    getAll: vi.fn(),
  },
  adminIdentityAPI: {
    getName: vi.fn(() => 'Jean Admin'),
    setName: vi.fn(),
  },
}))

const ALUMNUS = {
  id: 42,
  last_name: 'Dupont',
  first_name: 'Jean',
  email: 'jean.dupont@example.com',
  promotion: 'MSc Data Science',
  current_company: 'Acme',
  current_position: 'Data Analyst',
  sector: 'Informatique',
  availability_status: 'en_poste',
  contact_status: 'actif',
  certifications_count: 1,
  skills: ['Python'],
  is_anonymised: false,
}

const PROFILE = {
  id: 42,
  first_name: 'Jean',
  last_name: 'Dupont',
  email: 'jean.dupont@example.com',
  phone: '0600000000',
  address: '',
  city: 'Paris',
  country: 'France',
  linkedin: '',
  availability_status: 'en_poste',
  sector: 'Informatique',
  skills: ['Python'],
  promotion: 'MSc Data Science',
  id_promotion: 1,
  experiences_count: 0,
  date_naissance: '2000-01-01',
  date_inscription: '2024-01-01',
  email_academique: '',
  parcours_anterieur: '',
}

beforeEach(() => {
  vi.clearAllMocks()
  alumniAPI.getAll.mockResolvedValue({ data: [ALUMNUS] })
  promotionsAPI.getAll.mockResolvedValue({ data: [{ id: 1, name: 'MSc Data Science', year: 2025 }] })
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('AlumniDirectory - boutons Modifier / Anonymiser / Supprimer', () => {
  it('affiche les boutons Modifier et Anonymiser, et le menu d\'actions secondaires', async () => {
    render(<AlumniDirectory />)
    await screen.findByText('Dupont')
    expect(screen.getByRole('button', { name: /Modifier/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Anonymiser/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Plus d'actions/i })).toBeInTheDocument()
  })

  it('modifie un etudiant via alumniAPI.update', async () => {
    alumniAPI.getById.mockResolvedValue({ data: PROFILE })
    alumniAPI.update.mockResolvedValue({ data: { ...PROFILE, last_name: 'Martin' } })
    const user = userEvent.setup()
    render(<AlumniDirectory />)
    await screen.findByText('Dupont')

    await user.click(screen.getByRole('button', { name: /Modifier/i }))
    const nomInput = await screen.findByDisplayValue('Dupont')
    await user.clear(nomInput)
    await user.type(nomInput, 'Martin')
    await user.click(screen.getByRole('button', { name: /Enregistrer/i }))

    await waitFor(() => {
      expect(alumniAPI.update).toHaveBeenCalledTimes(1)
    })
    const [id, payload] = alumniAPI.update.mock.calls[0]
    expect(id).toBe(42)
    expect(payload.last_name).toBe('Martin')
    expect(payload.id_promotion).toBe(1)
    expect(payload.availability_status).toBe('en_poste')
  })

  it('anonymise un etudiant via alumniAPI.anonymise (RGPD direct par admin)', async () => {
    alumniAPI.anonymise.mockResolvedValue({ data: { id_etudiant: 42, statut: 'anonymise' } })
    const user = userEvent.setup()
    render(<AlumniDirectory />)
    await screen.findByText('Dupont')

    await user.click(screen.getByRole('button', { name: /Anonymiser/i }))

    const dialog = await screen.findByRole('dialog')
    expect(dialog).toHaveTextContent(/Anonymiser cet alumni/i)
    expect(dialog).toHaveTextContent(/masque les données personnelles/i)
    expect(dialog).toHaveTextContent(/différente/i)

    await user.click(within(dialog).getByRole('button', { name: /Anonymiser/i }))
    await waitFor(() => {
      expect(alumniAPI.anonymise).toHaveBeenCalledWith(42, 'Jean Admin')
    })
  })

  it('annule l\'anonymisation sans appeler alumniAPI.anonymise', async () => {
    const user = userEvent.setup()
    render(<AlumniDirectory />)
    await screen.findByText('Dupont')

    await user.click(screen.getByRole('button', { name: /Anonymiser/i }))
    const dialog = await screen.findByRole('dialog')
    await user.click(within(dialog).getByRole('button', { name: /Annuler/i }))

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })
    expect(alumniAPI.anonymise).not.toHaveBeenCalled()
  })

  it('supprime un etudiant apres confirmation explicite de suppression reelle', async () => {
    alumniAPI.delete.mockResolvedValue({ status: 204 })
    const user = userEvent.setup()
    render(<AlumniDirectory />)
    await screen.findByText('Dupont')

    await user.click(screen.getByRole('button', { name: /Plus d'actions/i }))
    await user.click(screen.getByRole('button', { name: /Supprimer définitivement/i }))

    const dialog = await screen.findByRole('dialog')
    expect(dialog).toHaveTextContent(/Action irréversible/i)
    expect(dialog).toHaveTextContent(/à réserver aux erreurs de saisie ou doublons/i)
    expect(dialog).toHaveTextContent(/demandes de suppression RGPD normales/i)

    await user.click(within(dialog).getByRole('button', { name: /Supprimer définitivement/i }))
    await waitFor(() => {
      expect(alumniAPI.delete).toHaveBeenCalledWith(42, 'Jean Admin')
    })
  })

  it('annule la suppression sans appeler alumniAPI.delete', async () => {
    const user = userEvent.setup()
    render(<AlumniDirectory />)
    await screen.findByText('Dupont')

    await user.click(screen.getByRole('button', { name: /Plus d'actions/i }))
    await user.click(screen.getByRole('button', { name: /Supprimer définitivement/i }))
    const dialog = await screen.findByRole('dialog')
    await user.click(within(dialog).getByRole('button', { name: /Annuler/i }))

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })
    expect(alumniAPI.delete).not.toHaveBeenCalled()
  })

  it('desactive Modifier et Anonymiser mais garde la suppression definitive disponible pour un compte anonymise', async () => {
    alumniAPI.getAll.mockResolvedValue({ data: [{ ...ALUMNUS, is_anonymised: true }] })
    const user = userEvent.setup()
    render(<AlumniDirectory />)
    await screen.findByText('Dupont')
    expect(screen.getByRole('button', { name: /Modifier/i })).toBeDisabled()
    expect(screen.getByRole('button', { name: /Anonymiser/i })).toBeDisabled()
    const moreBtn = screen.getByRole('button', { name: /Plus d'actions/i })
    expect(moreBtn).toBeEnabled()
    await user.click(moreBtn)
    expect(screen.getByRole('button', { name: /Supprimer définitivement/i })).toBeInTheDocument()
  })
})
