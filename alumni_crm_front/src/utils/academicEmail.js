export const ACADEMIC_EMAIL_DOMAIN = 'ionis-stm.com';

/**
 * Normalise un prénom ou nom en slug pour l'email académique
 * (même règle que le backend dans utils.normalize_academic_slug) :
 * - minuscules ;
 * - retrait des accents (é -> e, à -> a, ç -> c, …) ;
 * - suppression des espaces et apostrophes (« O'Brien » -> « obrien ») ;
 * - conservation des tirets (« Jean-Paul » -> « jean-paul ») ;
 * - suppression de tout autre caractère non [a-z0-9-].
 */
const normalizePart = (value = '') =>
  String(value)
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/['\u2019 ]/g, '')
    .replace(/[^a-z0-9-]/g, '')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');

/**
 * Construit l'email académique "prenom.nom@ionis-stm.com" à partir du prénom
 * et du nom. Retourne une chaîne vide si l'un des deux est manquant.
 */
export const buildAcademicEmail = (firstName = '', lastName = '') => {
  const first = normalizePart(firstName);
  const last = normalizePart(lastName);
  if (!first || !last) return '';
  return `${first}.${last}@${ACADEMIC_EMAIL_DOMAIN}`;
};
