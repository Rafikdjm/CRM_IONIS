export const isIOSDevice = () =>
  /iPad|iPhone|iPod/.test(navigator.userAgent) ||
  (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

const getBlobURL = (blob) => {
  try {
    return window.URL.createObjectURL(blob);
  } catch {
    return null;
  }
};

const triggerClick = (href, filename, targetBlank) => {
  const link = document.createElement('a');
  link.href = href;
  link.download = filename;
  link.rel = 'noopener noreferrer';
  link.style.display = 'none';
  if (targetBlank) link.target = '_blank';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const downloadBlob = (blob, filename) => {
  const url = getBlobURL(blob);
  if (!url) return false;

  if (isIOSDevice()) {
    // iOS Safari ignore `download` lors d'un clic programmatique hors du
    // geste utilisateur (à cause des `await` précédents) et l'attribut
    // target="_blank" ouvrirait un onglet vide au lieu de télécharger.
    // On évite donc _blank : sans download honoré, Safari affiche/ouvre le
    // blob (QuickLook) ou le télécharge selon la config. On garde aussi le
    // blob vivant longtemps pour laisser le gestionnaire de téléchargement
    // le lire, et on relance après un délai pour couvrir iOS 15+.
    triggerClick(url, filename, false);
    setTimeout(() => triggerClick(url, filename, false), 150);
    setTimeout(() => window.URL.revokeObjectURL(url), 30000);
    return true;
  }

  triggerClick(url, filename, false);
  setTimeout(() => window.URL.revokeObjectURL(url), 30000);
  return true;
};

export default downloadBlob;
