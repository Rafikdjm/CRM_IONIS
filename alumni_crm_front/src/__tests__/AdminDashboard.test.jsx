import { describe, it, expect, vi, beforeEach } from 'vitest'
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

const BASE_KPIS = {
  data: {
    total_alumni: 120,
    employment_rate_6m: 78,
    employment_rate_brut: 85,
    avg_response_rate: 62,
    active_alumni: 90,
    recent_updates: 0,
  },
}

const TROIS_TAGS = [
  { tag: 'adequation_formation', libelle: 'Adéquation formation/emploi', pourcentage: 88.0, nb_repondants: 25 },
  { tag: 'statut_professionnel', libelle: 'Statut professionnel', pourcentage: 70.5, nb_repondants: 20 },
  { tag: 'taux_recommandation', libelle: 'Taux de recommandation', pourcentage: 92.0, nb_repondants: 30 },
]

beforeEach(() => {
  vi.clearAllMocks()
  statsAPI.getKPIs.mockReset().mockResolvedValue(BASE_KPIS)
  statsAPI.getBySector.mockReset().mockResolvedValue({ data: [] })
  statsAPI.getByPromotion.mockReset().mockResolvedValue({ data: [] })
  statsAPI.getIndicateursComplementaires.mockReset().mockResolvedValue({
    data: {
      salaire_moyen: null,
      salaires_renseignes: 0,
      taux_emploi_6mois_par_promotion: [],
      total_alumni: BASE_KPIS.data.total_alumni,
      alumni_actifs: BASE_KPIS.data.active_alumni,
      taux_couverture: BASE_KPIS.data.avg_response_rate,
      salaire_moyen_promotions: [],
    },
  })
  statsAPI.getTypesContrat.mockReset().mockResolvedValue({ data: [] })
})

describe('AdminDashboard - indicateurs dynamiques des enquêtes', () => {
  it('affiche une carte pour chaque tag KPI retourné par l API', async () => {
    statsAPI.getKpiTags.mockResolvedValue({ data: TROIS_TAGS })

    render(<AdminDashboard />)

    await waitFor(() => {
      expect(screen.getByText('Indicateurs des enquêtes')).toBeInTheDocument()
    })

    expect(screen.getByText('Adéquation formation/emploi')).toBeInTheDocument()
    expect(screen.getByText('Statut professionnel')).toBeInTheDocument()
    expect(screen.getByText('Taux de recommandation')).toBeInTheDocument()

    expect(screen.getByText('88%')).toBeInTheDocument()
    expect(screen.getByText('25 répondants concernés')).toBeInTheDocument()

    expect(statsAPI.getKpiTags).toHaveBeenCalledTimes(1)
  })

  it('n affiche aucune zone KPI dynamique quand aucun tag n existe', async () => {
    statsAPI.getKpiTags.mockResolvedValue({ data: [] })

    render(<AdminDashboard />)

    await waitFor(() => {
      expect(screen.getByText('Tableau de bord')).toBeInTheDocument()
    })

    expect(screen.queryByText('Indicateurs des enquêtes')).not.toBeInTheDocument()
  })

  it('affiche un nouveau tag ajouté à la volée sans modification de code', async () => {
    const tagSupplementaire = {
      tag: 'satisfaction_globale',
      libelle: 'Satisfaction globale',
      pourcentage: 100.0,
      nb_repondants: 3,
    }
    statsAPI.getKpiTags.mockResolvedValue({ data: [...TROIS_TAGS, tagSupplementaire] })

    render(<AdminDashboard />)

    await waitFor(() => {
      expect(screen.getByText('Satisfaction globale')).toBeInTheDocument()
    })
    expect(screen.getByText('100%')).toBeInTheDocument()
    expect(screen.getByText('3 répondants concernés')).toBeInTheDocument()
  })

  describe('RatingVisual - nombre d étoiles pleines', () => {
    const ratingTag = (valeur) => ({
      tag: 'taux_recommandation',
      libelle: 'Taux de recommandation',
      question_type: 'rating',
      valeur,
      unite: '/5',
      nb_repondants: 10,
    })

    const compterEtoilesPleines = async (valeur) => {
      render(<AdminDashboard />)
      const titre = `${valeur}/5`
      await waitFor(() => {
        expect(screen.getByTitle(titre)).toBeInTheDocument()
      })
      return screen.getByTitle(titre).querySelector('.text-amber-400').children.length
    }

    it('3/5 affiche 3 étoiles pleines', async () => {
      statsAPI.getKpiTags.mockResolvedValue({ data: [ratingTag(3)] })
      expect(await compterEtoilesPleines(3)).toBe(3)
    })

    it('4/5 affiche 4 étoiles pleines', async () => {
      statsAPI.getKpiTags.mockResolvedValue({ data: [ratingTag(4)] })
      expect(await compterEtoilesPleines(4)).toBe(4)
    })

    it('2.5/5 affiche 2 étoiles pleines (arrondi inférieur)', async () => {
      statsAPI.getKpiTags.mockResolvedValue({ data: [ratingTag(2.5)] })
      expect(await compterEtoilesPleines(2.5)).toBe(2)
    })
  })

  it('inclut un segment Non renseigné dans le camembert des secteurs', async () => {
    statsAPI.getKPIs.mockResolvedValue({
      data: { ...BASE_KPIS.data, total_alumni: 2 },
    })
    statsAPI.getBySector.mockResolvedValue({
      data: [
        { sector: 'Technologie', count: 1, percentage: 50, nonRenseigne: false },
        { sector: 'Non renseigné', count: 1, percentage: 50, nonRenseigne: true },
      ],
    })

    render(<AdminDashboard />)

    await waitFor(() => {
      expect(screen.getByText('Technologie')).toBeInTheDocument()
    })
    expect(screen.getByText('Non renseigné')).toBeInTheDocument()
    expect(screen.getAllByText('2')).toHaveLength(2)
    expect(screen.getAllByText('50%')).toHaveLength(2)
  })
})
