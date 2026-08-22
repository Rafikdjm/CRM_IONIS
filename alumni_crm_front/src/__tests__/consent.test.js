import { describe, it, expect, vi, beforeEach } from 'vitest'

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

describe('mapBackendConsent', () => {
  let mapBackendConsent

  beforeEach(async () => {
    vi.resetModules()
    const api = await import('../services/api.js')
    mapBackendConsent = api.mapBackendConsent
  })

  it('retourne les valeurs par défaut pour un tableau vide', () => {
    const out = mapBackendConsent([])
    expect(out).toEqual({
      contact_allowed: false,
      data_sharing: false,
      survey_participation: false,
      newsletter: false,
      last_updated: null,
    })
  })

  it('retourne les valeurs par défaut si pas un tableau', () => {
    expect(mapBackendConsent(null).contact_allowed).toBe(false)
    expect(mapBackendConsent({}).contact_allowed).toBe(false)
  })

  it('garde le consentement le PLUS RÉCENT par type (ancien bug: le plus ancien gagnait)', () => {
    const items = [
      { id_consentement: 1, type_consentement: 'prise_de_contact', statut: 'actif', date_consentement: '2026-07-25' },
      { id_consentement: 2, type_consentement: 'prise_de_contact', statut: 'refuse', date_consentement: '2026-08-01' },
      { id_consentement: 3, type_consentement: 'prise_de_contact', statut: 'actif', date_consentement: '2026-08-08' },
    ]
    const out = mapBackendConsent(items)
    expect(out.contact_allowed).toBe(true) // le plus récent est 'actif'
    expect(out.last_updated).toBe('2026-08-08')
  })

  it('tranche par id_consentement en cas de même date', () => {
    const items = [
      { id_consentement: 5, type_consentement: 'newsletter', statut: 'actif', date_consentement: '2026-08-08' },
      { id_consentement: 9, type_consentement: 'newsletter', statut: 'refuse', date_consentement: '2026-08-08' },
    ]
    const out = mapBackendConsent(items)
    expect(out.newsletter).toBe(false) // id le plus grand = le plus récent
  })

  it('mappe indépendamment chaque type', () => {
    const items = [
      { id_consentement: 1, type_consentement: 'partage_donnees', statut: 'actif', date_consentement: '2026-08-01' },
      { id_consentement: 2, type_consentement: 'enquetes', statut: 'refuse', date_consentement: '2026-08-02' },
    ]
    const out = mapBackendConsent(items)
    expect(out.data_sharing).toBe(true)
    expect(out.survey_participation).toBe(false)
    expect(out.newsletter).toBe(false)
    expect(out.contact_allowed).toBe(false)
    expect(out.last_updated).toBe('2026-08-02')
  })
})
