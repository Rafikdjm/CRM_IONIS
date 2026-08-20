export const isIOSDevice = () =>
  /iPad|iPhone|iPod/.test(navigator.userAgent) ||
  (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

export const prepareIOSWindow = () => {
  if (!isIOSDevice()) return null;
  return window.open('', '_blank');
};

export const downloadBlob = (blob, filename, preOpenedWindow) => {
  console.log('[downloadBlob] userAgent:', navigator.userAgent);
  console.log('[downloadBlob] platform:', navigator.platform, '- maxTouchPoints:', navigator.maxTouchPoints);
  console.log('[downloadBlob] isIOSDevice:', isIOSDevice());

  const url = window.URL.createObjectURL(blob);
  const cleanup = () => window.URL.revokeObjectURL(url);

  if (isIOSDevice()) {
    const win = preOpenedWindow || window.open(url, '_blank');
    if (win) {
      win.location.href = url;
      setTimeout(cleanup, 1000);
      return;
    }
  }

  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.rel = 'noopener';
  link.style.display = 'none';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  setTimeout(cleanup, 1000);
};

export default downloadBlob;
