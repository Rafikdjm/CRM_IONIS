const getApiBase = () => {
  const configured = import.meta.env.VITE_API_URL;
  if (configured) {
    return configured.replace(/\/+$/, '');
  }
  return '/api';
};

const getToken = () => localStorage.getItem('token') || '';

const buildExportUrl = (path, params = {}) => {
  const base = getApiBase();
  const query = new URLSearchParams(params);
  const token = getToken();
  if (token) query.set('token', token);
  const queryString = query.toString();
  return `${base}${path}${queryString ? `?${queryString}` : ''}`;
};

export const downloadFileByUrl = (path, params = {}) => {
  const href = buildExportUrl(path, params);
  const link = document.createElement('a');
  link.href = href;
  link.rel = 'noopener noreferrer';
  link.style.display = 'none';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export default downloadFileByUrl;
