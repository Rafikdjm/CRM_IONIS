import { describe, it, expect } from 'vitest'
import { ACADEMIC_EMAIL_DOMAIN, buildAcademicEmail } from '../utils/academicEmail'

describe('buildAcademicEmail', () => {
  it('génère prenom.nom@ionis-stm.com en minuscules', () => {
    expect(buildAcademicEmail('Jean', 'Dupont')).toBe(`jean.dupont@${ACADEMIC_EMAIL_DOMAIN}`)
  })

  it('retire les accents', () => {
    expect(buildAcademicEmail('Élodie', 'Noël')).toBe(`elodie.noel@${ACADEMIC_EMAIL_DOMAIN}`)
    expect(buildAcademicEmail('François', 'çaëlle')).toBe(`francois.caelle@${ACADEMIC_EMAIL_DOMAIN}`)
  })

  it('supprime les espaces et apostrophes', () => {
    expect(buildAcademicEmail("O'Brien", 'Martin')).toBe(`obrien.martin@${ACADEMIC_EMAIL_DOMAIN}`)
    expect(buildAcademicEmail('Jean Pierre', 'Dupont')).toBe(`jeanpierre.dupont@${ACADEMIC_EMAIL_DOMAIN}`)
  })

  it('conserve les tirets des noms composés', () => {
    expect(buildAcademicEmail('Jean-Paul', 'De La Croix')).toBe(`jean-paul.delacroix@${ACADEMIC_EMAIL_DOMAIN}`)
  })

  it('retire les caractères non alphanumériques restants', () => {
    expect(buildAcademicEmail('Aïcha@2', 'K!eïta')).toBe(`aicha2.keita@${ACADEMIC_EMAIL_DOMAIN}`)
  })

  it('retourne une chaîne vide si prénom ou nom manque', () => {
    expect(buildAcademicEmail('Jean', '')).toBe('')
    expect(buildAcademicEmail('', 'Dupont')).toBe('')
    expect(buildAcademicEmail('', '')).toBe('')
  })
})
