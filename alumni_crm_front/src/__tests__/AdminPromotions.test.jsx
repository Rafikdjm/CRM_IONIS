import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AdminPromotions from '../components/admin/AdminPromotions'
import { promotionsAPI } from '../services/api'

vi.mock('../services/api', () => ({
  promotionsAPI: {
    getAll: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
  },
}))

const PROMO = {
  id: 1,
  name: 'MSc Data Science',
  year: 2025,
  filiere: 'Informatique',
  nb_etudiants: 3,
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.spyOn(window, 'confirm').mockImplementation(() => true)
  promotionsAPI.getAll.mockReset().mockResolvedValue({ data: [PROMO] })
  promotionsAPI.create.mockReset()
  promotionsAPI.update.mockReset()
  promotionsAPI.remove.mockReset()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('AdminPromotions - affichage de la liste', () => {
  it('affiche nom, annee, filiere et nombre d etudiants', async () => {
    render(<AdminPromotions />)
    await waitFor(() => {
      expect(screen.getByText('MSc Data Science')).toBeInTheDocument()
    })
    expect(screen.getByText('2025')).toBeInTheDocument()
    expect(screen.getByText('Informatique')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
  })
})

describe('AdminPromotions - creation', () => {
  it('appelle promotionsAPI.create avec les champs saisis', async () => {
    promotionsAPI.create.mockResolvedValue({ data: { id_promotion: 99 } })
    const user = userEvent.setup()
    render(<AdminPromotions />)
    await screen.findByText('MSc Data Science')

    await user.click(screen.getByRole('button', { name: /Ajouter une promotion/i }))
    await user.type(screen.getByPlaceholderText('Ex : MSc Data Science'), 'MSc Cybersécurité')
    await user.type(screen.getByPlaceholderText('Ex : 2026'), '2026')
    await user.type(screen.getByPlaceholderText('Ex : Informatique'), 'Cybersécurité')
    await user.click(screen.getByRole('button', { name: /Créer la promotion/i }))

    await waitFor(() => {
      expect(promotionsAPI.create).toHaveBeenCalledWith({
        nom_promotion: 'MSc Cybersécurité',
        annee_diplome: 2026,
        filiere: 'Cybersécurité',
      })
    })
  })

  it('bloque la creation si un champ est manquant', async () => {
    const user = userEvent.setup()
    render(<AdminPromotions />)
    await screen.findByText('MSc Data Science')

    await user.click(screen.getByRole('button', { name: /Ajouter une promotion/i }))
    await user.type(screen.getByPlaceholderText('Ex : MSc Data Science'), 'MSc Test')
    await user.click(screen.getByRole('button', { name: /Créer la promotion/i }))

    await screen.findByText('Tous les champs sont obligatoires.')
    expect(promotionsAPI.create).not.toHaveBeenCalled()
  })
})

describe('AdminPromotions - modification', () => {
  it('pre-remplit le formulaire et appelle promotionsAPI.update', async () => {
    promotionsAPI.update.mockResolvedValue({ data: { id_promotion: 1 } })
    const user = userEvent.setup()
    render(<AdminPromotions />)
    await screen.findByText('MSc Data Science')

    await user.click(screen.getByRole('button', { name: /Modifier/i }))
    const nomInput = screen.getByDisplayValue('MSc Data Science')
    await user.clear(nomInput)
    await user.type(nomInput, 'MSc Data Science (MAJ)')
    await user.click(screen.getByRole('button', { name: /Enregistrer les modifications/i }))

    await waitFor(() => {
      expect(promotionsAPI.update).toHaveBeenCalledWith(1, {
        nom_promotion: 'MSc Data Science (MAJ)',
        annee_diplome: 2025,
        filiere: 'Informatique',
      })
    })
  })
})

describe('AdminPromotions - suppression', () => {
  it('supprime directement (204) sans modal en cascade quand aucun etudiant', async () => {
    promotionsAPI.remove.mockResolvedValue({ status: 204 })
    const user = userEvent.setup()
    render(<AdminPromotions />)
    await screen.findByText('MSc Data Science')

    await user.click(screen.getByRole('button', { name: /Supprimer/i }))
    await waitFor(() => {
      expect(promotionsAPI.remove).toHaveBeenCalledWith(1)
    })
    expect(screen.queryByText(/Suppression en cascade/i)).not.toBeInTheDocument()
  })

  it('affiche la modal en cascade sur 409 puis renvoie avec force=true', async () => {
    promotionsAPI.remove
      .mockRejectedValueOnce({
        response: {
          status: 409,
          data: {
            detail:
              'Impossible de supprimer cette promotion : 3 étudiant(s) y sont rattachés. Confirmez la suppression en cascade explicite (force=true) pour continuer.',
          },
        },
      })
      .mockResolvedValueOnce({ status: 204 })
    const user = userEvent.setup()
    render(<AdminPromotions />)
    await screen.findByText('MSc Data Science')

    await user.click(screen.getByRole('button', { name: /Supprimer/i }))

    const dialog = await screen.findByRole('dialog')
    expect(dialog).toHaveTextContent(/Suppression en cascade/i)
    expect(dialog).toHaveTextContent('3')
    expect(dialog).toHaveTextContent(/DÉFINITIVE/i)

    await user.click(screen.getByRole('button', { name: /Supprimer définitivement/i }))
    await waitFor(() => {
      expect(promotionsAPI.remove).toHaveBeenLastCalledWith(1, true)
    })
    expect(screen.queryByText(/Suppression en cascade/i)).not.toBeInTheDocument()
  })

  it('annule sans renvoyer force=true quand l admin refuse la cascade', async () => {
    promotionsAPI.remove.mockRejectedValueOnce({
      response: {
        status: 409,
        data: {
          detail:
            'Impossible de supprimer cette promotion : 3 étudiant(s) y sont rattachés. Confirmez la suppression en cascade explicite (force=true) pour continuer.',
        },
      },
    })
    const user = userEvent.setup()
    render(<AdminPromotions />)
    await screen.findByText('MSc Data Science')

    await user.click(screen.getByRole('button', { name: /Supprimer/i }))
    await screen.findByRole('dialog')
    await user.click(screen.getByRole('button', { name: /Annuler/i }))

    await waitFor(() => {
      expect(screen.queryByText(/Suppression en cascade/i)).not.toBeInTheDocument()
    })
    expect(promotionsAPI.remove).toHaveBeenCalledTimes(1)
    expect(promotionsAPI.remove).toHaveBeenCalledWith(1)
  })
})
