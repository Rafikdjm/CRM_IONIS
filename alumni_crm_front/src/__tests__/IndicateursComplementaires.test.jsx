import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import AdminDashboard from '../components/admin/AdminDashboard'
import { statsAPI } from '../services/api'

vi.mock('../services/api', () => ({
  statsAPI: {
    getKPIs: vi.fn(),
    getBySector: vi.fn(),
    getByPromotion: vi.fn(),
    getKpiTags: vi.fn(),
    getIndicateursComplementaires: vi.fn(),
    getTypesContrat: vi.fn(),
  },
}))

// Payload = reponse reelle de l'API (donnees actuelles de la base).
const REAL = {
  kpis: {
    total_alumni: 1,
    employment_rate_6m: 100,
    employment_rate_brut: 100,
    avg_response_rate: 100,
    active_alumni: 1,
    recent_updates: 0,
  },
  complement: {
    data: {
      salaire_moyen: 42000.0,
      salaires_renseignes: 1,
      salaire_min: 42000.0,
      salaire_max: 42000.0,
      taux_emploi_6mois_par_promotion: [{
        nom_promotion: 'Data & IA',
        annee_diplome: 2025,
        date_reference: '2025-12-01',
        statut_maturite: 'mature',
        total_diplomes: 1,
        emplois_6_mois: 1,
        taux_emploi_6mois_pourcentage: 100.0,
        taux_couverture: 100.0,
      }],
      total_alumni: 1,
      alumni_actifs: 1,
      taux_couverture: 100,
    },
  },
  types: { data: [{ type_contrat: 'CDI', count: 1, nonRenseigne: false }] },
}

beforeEach(() => {
  statsAPI.getKPIs.mockResolvedValue({ data: REAL.kpis })
  statsAPI.getBySector.mockResolvedValue({ data: [] })
  statsAPI.getByPromotion.mockResolvedValue({
    data: [{ promotion: 'Data & IA', count: 1, percentage: 100 }],
  })
  statsAPI.getKpiTags.mockResolvedValue({ data: [] })
  statsAPI.getIndicateursComplementaires.mockResolvedValue(REAL.complement)
  statsAPI.getTypesContrat.mockResolvedValue(REAL.types)
})

describe('Indicateurs complémentaires (donnees reelles)', () => {
  it('affiche les 4 nouvelles cartes avec les bonnes valeurs', async () => {
    render(<AdminDashboard />)
    await waitFor(() => {
      expect(screen.getByText('Indicateurs complémentaires')).toBeInTheDocument()
    })
    expect(screen.getByText('Salaire moyen')).toBeInTheDocument()
    // format fr-FR : 42 000 €
    expect(screen.getByText(/42\s?000\s?€/)).toBeInTheDocument()
    expect(screen.getByText(/1 salaire brut annuel/)).toBeInTheDocument()
    expect(screen.getByText('Taux de couverture')).toBeInTheDocument()
    expect(screen.getByText(/1 avec expérience/)).toBeInTheDocument()
    // 100% apparait deja pour le taux d'emploi : au moins 2 occurrences
    expect(screen.getAllByText('100%').length).toBeGreaterThanOrEqual(2)
    expect(screen.getByText('Types de contrat')).toBeInTheDocument()
    expect(screen.getByText('CDI')).toBeInTheDocument()
    expect(screen.getByText('Maturité des cohortes')).toBeInTheDocument()
    expect(screen.getByText(/Diplômés 2025/)).toBeInTheDocument()
    expect(screen.getByText(/Mature · 100%/)).toBeInTheDocument()
  })

  it('n affiche pas le taux de maturite quand la cohorte est en_attente', async () => {
    statsAPI.getIndicateursComplementaires.mockResolvedValue({
      data: {
        ...REAL.complement.data,
        taux_emploi_6mois_par_promotion: [{
          ...REAL.complement.data.taux_emploi_6mois_par_promotion[0],
          annee_diplome: 2026,
          date_reference: '2026-12-01',
          statut_maturite: 'en_attente',
          taux_emploi_6mois_pourcentage: null,
        }],
      },
    })
    render(<AdminDashboard />)
    await waitFor(() => {
      expect(screen.getByText(/En attente/)).toBeInTheDocument()
    })
    expect(screen.getByText(/réf\. 12\/2026/)).toBeInTheDocument()
    expect(screen.queryByText(/Mature ·/)).not.toBeInTheDocument()
  })
})

describe('Fourchette de la jauge salaire (dynamique, issue du CRM)', () => {
  // La fourchette DOIT être dérivée des salaires réels en base (min/max),
  // jamais d'une valeur codée en dur ni d'une référence de marché externe.

  it('echantillon limite (1 salaire) : elargit de +/-30% et affiche la mention', async () => {
    render(<AdminDashboard />)
    await waitFor(() => {
      expect(screen.getByText('Salaire moyen')).toBeInTheDocument()
    })
    // 1 seul salaire -> fourchette indicative 42 000 € +/- 30 % -> 29K / 55K.
    // La mention d'echantillon limite doit apparaitre explicitement.
    expect(screen.getByText(/Fourchette indicative/)).toBeInTheDocument()
    expect(screen.getByText(/chantillon limit/)).toBeInTheDocument()
    expect(screen.getByText(/1 salaire renseign/)).toBeInTheDocument()
    // Borne inf -30% : 42 000 * 0.7 = 29 400 -> 29K ; borne sup +30% : 54 600 -> 55K.
    expect(screen.getByText('29K €')).toBeInTheDocument()
    expect(screen.getByText('55K €')).toBeInTheDocument()
  })

  it('echantillon suffisant (>=5) : fourchette min/max reels +/-10% sans mention limite', async () => {
    statsAPI.getIndicateursComplementaires.mockResolvedValue({
      data: {
        ...REAL.complement.data,
        salaire_moyen: 40000.0,
        salaires_renseignes: 6,
        salaire_min: 30000.0,
        salaire_max: 50000.0,
      },
    })
    render(<AdminDashboard />)
    await waitFor(() => {
      expect(screen.getByText('Salaire moyen')).toBeInTheDocument()
    })
    // 6 salaires -> marge standard -10%/+10% autour du min/max reels :
    // 30 000 * 0.9 = 27 000 -> 27K ; 50 000 * 1.1 = 55 000 -> 55K.
    expect(screen.getByText('27K €')).toBeInTheDocument()
    expect(screen.getByText('55K €')).toBeInTheDocument()
    expect(screen.getByText(/min\/max des salaires renseignés/)).toBeInTheDocument()
    // Seuil depasse : plus aucune mention d'echantillon limite.
    expect(screen.queryByText(/chantillon limit/)).not.toBeInTheDocument()
  })
})
