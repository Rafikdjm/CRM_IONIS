import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AdminRgpdDemandes from '../components/admin/AdminRgpdDemandes'
import { adminRgpdAPI } from '../services/api'
import downloadBlob from '../utils/downloadBlob'

vi.mock('../services/api', () => ({
  adminRgpdAPI: {
    list: vi.fn(),
    traiter: vi.fn(),
    prendreEnCharge: vi.fn(),
    exportData: vi.fn(),
    bulkTraiter: vi.fn(),
    bulkDelete: vi.fn(),
    bulkExport: vi.fn(),
    purgeCloturees: vi.fn(),
  },
  adminIdentityAPI: {
    getName: vi.fn(() => ''),
    setName: vi.fn(),
  },
}))

vi.mock('../utils/downloadBlob', () => ({ default: vi.fn() }))

const DEMANDES = [
  {
    id_demande: 1,
    id_etudiant: 10,
    type_demande: 'export',
    statut: 'envoyee',
    nom_complet: 'Jean Dupont',
    email: 'jean.dupont@test.fr',
    date_demande: '2026-08-01T10:00:00Z',
  },
  {
    id_demande: 2,
    id_etudiant: 11,
    type_demande: 'suppression',
    statut: 'envoyee',
    nom_complet: 'Marie Martin',
    email: 'marie.martin@test.fr',
    date_demande: '2026-08-02T10:00:00Z',
  },
]

const DEMANDES_AVEC_CLOTUREE = [
  ...DEMANDES,
  {
    id_demande: 3,
    id_etudiant: 12,
    type_demande: 'export',
    statut: 'traitee',
    nom_complet: 'Alex Terne',
    email: 'alex.terne@test.fr',
    date_demande: '2026-08-03T10:00:00Z',
    traitee_par: 'Admin',
  },
]

async function selectionner(user, ids) {
  for (const id of ids) {
    await user.click(screen.getByLabelText(`Sélectionner la demande ${id}`))
  }
}

async function confirmer(user, actionLabel) {
  await user.click(screen.getByRole('button', { name: actionLabel }))
  await user.type(screen.getByLabelText(/votre nom/i), 'Admin')
  await user.click(screen.getByRole('button', { name: 'Confirmer' }))
}

describe('AdminRgpdDemandes - message après action groupée', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    adminRgpdAPI.list.mockResolvedValue(DEMANDES)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('traitement groupé : résumé lisible sans JSON brut', async () => {
    const user = userEvent.setup()
    adminRgpdAPI.bulkTraiter.mockResolvedValue({
      total: 1,
      succes: 1,
      erreurs: 0,
      resultats: [{ id_demande: 1, ok: true, statut: 'traitee' }],
    })

    render(<AdminRgpdDemandes />)
    await screen.findByText('Jean Dupont')

    await selectionner(user, [1])
    await confirmer(user, 'Marquer comme traitée')

    expect(adminRgpdAPI.bulkTraiter).toHaveBeenCalledWith([1], 'traitee', 'Admin')
    expect(await screen.findByText('✓ 1 demande traitée avec succès')).toBeInTheDocument()
    expect(
      screen.getByText('Export effectué pour Jean Dupont (jean.dupont@test.fr)'),
    ).toBeInTheDocument()

    expect(screen.queryByText(/Action groupée terminée/)).not.toBeInTheDocument()
    expect(screen.queryByText(/"resultats"/)).not.toBeInTheDocument()
    expect(screen.queryByText(/consentements/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/erreur rencontrée/i)).not.toBeInTheDocument()
  })

  it('traitement groupé : précise « Suppression effectuée » pour une demande de suppression', async () => {
    const user = userEvent.setup()
    adminRgpdAPI.bulkTraiter.mockResolvedValue({
      total: 1,
      succes: 1,
      erreurs: 0,
      resultats: [{ id_demande: 2, ok: true, statut: 'traitee' }],
    })

    render(<AdminRgpdDemandes />)
    await screen.findByText('Marie Martin')

    await selectionner(user, [2])
    await confirmer(user, 'Marquer comme traitée')

    expect(await screen.findByText('✓ 1 demande traitée avec succès')).toBeInTheDocument()
    expect(
      screen.getByText('Suppression effectuée pour Marie Martin (marie.martin@test.fr)'),
    ).toBeInTheDocument()
  })

  it('plusieurs demandes traitées : chaque alumni est listé sur sa ligne', async () => {
    const user = userEvent.setup()
    adminRgpdAPI.bulkTraiter.mockResolvedValue({
      total: 2,
      succes: 2,
      erreurs: 0,
      resultats: [
        { id_demande: 1, ok: true, statut: 'traitee' },
        { id_demande: 2, ok: true, statut: 'traitee' },
      ],
    })

    render(<AdminRgpdDemandes />)
    await screen.findByText('Jean Dupont')

    await selectionner(user, [1, 2])
    await confirmer(user, 'Marquer comme traitée')

    expect(await screen.findByText('✓ 2 demandes traitées avec succès')).toBeInTheDocument()
    expect(
      screen.getByText('Export effectué pour Jean Dupont (jean.dupont@test.fr)'),
    ).toBeInTheDocument()
    expect(
      screen.getByText('Suppression effectuée pour Marie Martin (marie.martin@test.fr)'),
    ).toBeInTheDocument()
  })

  it('échecs partiels : les erreurs sont affichées séparément, pas en JSON', async () => {
    const user = userEvent.setup()
    adminRgpdAPI.bulkTraiter.mockResolvedValue({
      total: 2,
      succes: 1,
      erreurs: 1,
      resultats: [
        { id_demande: 1, ok: true, statut: 'traitee' },
        { id_demande: 2, ok: false, erreur: 'Déjà en cours de traitement par Autre.' },
      ],
    })

    render(<AdminRgpdDemandes />)
    await screen.findByText('Jean Dupont')

    await selectionner(user, [1, 2])
    await confirmer(user, 'Marquer comme traitée')

    expect(await screen.findByText('✓ 1 demande traitée avec succès')).toBeInTheDocument()
    expect(
      screen.getByText('Export effectué pour Jean Dupont (jean.dupont@test.fr)'),
    ).toBeInTheDocument()
    expect(screen.getByText(/n'a pas pu être traitée/)).toBeInTheDocument()
    expect(screen.getByText('1 erreur rencontrée :')).toBeInTheDocument()
    expect(
      screen.getByText('Demande #2 : Déjà en cours de traitement par Autre.'),
    ).toBeInTheDocument()
    expect(screen.queryByText(/"resultats"/)).not.toBeInTheDocument()
  })

  it('rejet groupé : titre et lignes adaptés', async () => {
    const user = userEvent.setup()
    adminRgpdAPI.bulkTraiter.mockResolvedValue({
      total: 1,
      succes: 1,
      erreurs: 0,
      resultats: [{ id_demande: 1, ok: true, statut: 'rejetee' }],
    })

    render(<AdminRgpdDemandes />)
    await screen.findByText('Jean Dupont')

    await selectionner(user, [1])
    await user.click(screen.getByRole('button', { name: 'Rejeter' }))
    await user.type(screen.getByLabelText(/motif du refus/i), 'Motif de test')
    await user.type(screen.getByLabelText(/votre nom/i), 'Admin')
    await user.click(screen.getByRole('button', { name: 'Confirmer' }))

    expect(adminRgpdAPI.bulkTraiter).toHaveBeenCalledWith([1], 'rejetee', 'Admin', 'Motif de test')
    expect(await screen.findByText('✓ 1 demande rejetée')).toBeInTheDocument()
    expect(
      screen.getByText('Demande rejetée pour Jean Dupont (jean.dupont@test.fr)'),
    ).toBeInTheDocument()
  })

  it('export groupé : téléchargement déclenché et résumé affiché', async () => {
    const user = userEvent.setup()
    const donneesJson = { exports: { 1: { etudiant: { prenom: 'Jean', nom: 'Dupont' } } }, erreurs: {} }
    adminRgpdAPI.bulkExport.mockResolvedValue({
      data: donneesJson,
      blob: new Blob([JSON.stringify(donneesJson)], { type: 'application/json' }),
      filename: 'export_rgpd_groupe_2026-08-01.json',
    })

    render(<AdminRgpdDemandes />)
    await screen.findByText('Jean Dupont')

    await selectionner(user, [1])
    await confirmer(user, 'Exporter (JSON)')

    expect(adminRgpdAPI.bulkExport).toHaveBeenCalledWith([1], 'json')
    expect(downloadBlob).toHaveBeenCalledTimes(1)
    expect(await screen.findByText('✓ Export effectué pour 1 demande')).toBeInTheDocument()
    expect(
      screen.getByText('Export effectué pour Jean Dupont (jean.dupont@test.fr)'),
    ).toBeInTheDocument()
    expect(screen.queryByText(/experiences/i)).not.toBeInTheDocument()
  })

  it('export groupé en Excel : sélecteur de format pris en compte', async () => {
    const user = userEvent.setup()
    adminRgpdAPI.bulkExport.mockResolvedValue({
      data: null,
      blob: new Blob(['xlsx-content']),
      filename: 'export_rgpd_groupe_2026-08-01.xlsx',
    })

    render(<AdminRgpdDemandes />)
    await screen.findByText('Jean Dupont')

    await user.selectOptions(screen.getByLabelText('Format d\'export'), 'xlsx')
    await selectionner(user, [1])
    await confirmer(user, 'Exporter (Excel (.xlsx))')

    expect(adminRgpdAPI.bulkExport).toHaveBeenCalledWith([1], 'xlsx')
    expect(downloadBlob).toHaveBeenCalledWith(
      expect.any(Blob),
      'export_rgpd_groupe_2026-08-01.xlsx',
    )
    expect(await screen.findByText(/Fichier d'export groupé téléchargé/)).toBeInTheDocument()
  })

  it('export groupé : erreurs d’export listées séparément', async () => {
    const user = userEvent.setup()
    const donneesJson = {
      exports: {},
      erreurs: { 2: 'Compte supprimé/anonymisé, export impossible.' },
    }
    adminRgpdAPI.bulkExport.mockResolvedValue({
      data: donneesJson,
      blob: new Blob([JSON.stringify(donneesJson)], { type: 'application/json' }),
      filename: 'export_rgpd_groupe_2026-08-01.json',
    })

    render(<AdminRgpdDemandes />)
    await screen.findByText('Marie Martin')

    await selectionner(user, [2])
    await confirmer(user, 'Exporter (JSON)')

    expect(await screen.findByText('✓ Export groupé terminé')).toBeInTheDocument()
    expect(screen.getByText('1 erreur rencontrée :')).toBeInTheDocument()
    expect(
      screen.getByText('Demande #2 : Compte supprimé/anonymisé, export impossible.'),
    ).toBeInTheDocument()
  })

  it('suppression groupée : compteur de demandes supprimées', async () => {
    const user = userEvent.setup()
    adminRgpdAPI.bulkDelete.mockResolvedValue({ supprimees: 2, ids: [1, 2] })

    render(<AdminRgpdDemandes />)
    await screen.findByText('Jean Dupont')

    await selectionner(user, [1, 2])
    await confirmer(user, 'Supprimer')

    expect(adminRgpdAPI.bulkDelete).toHaveBeenCalledWith([1, 2])
    expect(
      await screen.findByText('✓ 2 demandes supprimées définitivement'),
    ).toBeInTheDocument()
  })

  it('purge des clôturées : message de purge terminée', async () => {
    const user = userEvent.setup()
    adminRgpdAPI.list.mockResolvedValue(DEMANDES_AVEC_CLOTUREE)
    adminRgpdAPI.purgeCloturees.mockResolvedValue({ supprimees: 3, ids: [3] })

    render(<AdminRgpdDemandes />)
    await screen.findByText('Alex Terne')

    await user.click(
      screen.getByRole('button', { name: /Purger les demandes traitées\/rejetées \(1\)/ }),
    )
    await user.type(screen.getByLabelText(/votre nom/i), 'Admin')
    await user.click(screen.getByRole('button', { name: 'Confirmer' }))

    expect(adminRgpdAPI.purgeCloturees).toHaveBeenCalledTimes(1)
    expect(
      await screen.findByText('✓ Purge terminée : 3 demandes clôturées supprimées'),
    ).toBeInTheDocument()
  })
})
