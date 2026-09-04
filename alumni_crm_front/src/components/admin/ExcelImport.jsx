import { useState, useRef } from 'react';
import { importAPI } from '../../services/api';
import ErrorMessage from '../shared/ErrorMessage';
import { downloadFileByUrl } from '../../utils/downloadUrl';

let xlsxModulePromise = null;
const loadXlsx = () => {
  if (!xlsxModulePromise) xlsxModulePromise = import('xlsx');
  return xlsxModulePromise;
};

const EXPECTED_COLUMNS = [
  'prenom', 'nom', 'email', 'telephone', 'promotion', 'annee_diplome',
  'entreprise', 'poste', 'secteur', 'entreprise_pays', 'entreprise_ville',
  'linkedin', 'adresse', 'ville', 'pays',
  'statut_disponibilite', 'competences', 'date_naissance', 'date_inscription',
  'email_academique', 'parcours_anterieur', 'type_contrat', 'date_debut',
  'date_fin', 'poste_actuel',
];

export default function ExcelImport() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState([]);
  const [columns, setColumns] = useState([]);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFile = (selectedFile) => {
    setError(null);
    setImportResult(null);
    setFile(selectedFile);

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const { read, utils } = await loadXlsx();
        const workbook = read(e.target.result, { type: 'array' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = utils.sheet_to_json(worksheet, { defval: '' });

        if (jsonData.length === 0) {
          setError('Le fichier est vide ou ne contient pas de données valides.');
          return;
        }

        setColumns(Object.keys(jsonData[0]));
        setPreview(jsonData.slice(0, 10));
      } catch {
        setError('Impossible de lire le fichier. Assurez-vous qu\'il s\'agit d\'un fichier Excel (.xlsx) ou CSV valide.');
      }
    };
    reader.readAsArrayBuffer(selectedFile);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) handleFile(droppedFile);
  };

  const handleImport = async () => {
    if (!file) return;
    setImporting(true);
    setError(null);
    setImportResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await importAPI.uploadExcel(formData);
      setImportResult({
        success: true,
        message: response.data?.message || 'Import terminé avec succès.',
        imported: response.data?.imported || 0,
        errors: response.data?.errors || [],
      });
      setFile(null);
      setPreview([]);
      setColumns([]);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setImportResult({
          success: false,
          message: `${detail.length} erreur(s) lors de l'import.`,
          errors: detail,
        });
      } else {
        setError(detail || 'Erreur lors de l\'import du fichier.');
      }
    } finally {
      setImporting(false);
    }
  };

  const handleExport = async () => {
    downloadFileByUrl('/import/export/alumni');
  };

  const handleDownloadTemplate = async () => {
    downloadFileByUrl('/import/template');
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="mb-3 inline-flex h-1 w-12 rounded-full bg-gradient-to-r from-blue-600 to-indigo-500" />
          <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-slate-100 sm:text-3xl">Import / Export</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-slate-400">
            Importez une liste d'admis ou exportez les données
          </p>
        </div>
        <button
          onClick={handleExport}
          className="inline-flex w-full shrink-0 items-center justify-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 min-h-[44px] sm:w-auto"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
          </svg>
          Exporter les données
        </button>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-800 sm:p-6">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-slate-100">Importer un fichier</h2>
          <button
            onClick={handleDownloadTemplate}
            className="inline-flex w-full min-h-[44px] items-center justify-center rounded-lg border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 transition hover:bg-blue-100 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-300 dark:hover:bg-blue-900 sm:w-auto"
          >
            <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
            Télécharger le modèle Excel
          </button>
        </div>

        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-6 transition sm:p-8 ${
            dragOver
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-950'
              : 'border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50/50 dark:border-slate-600 dark:bg-slate-700/50'
          }`}
        >
          <svg className="mb-3 h-10 w-10 text-gray-400 dark:text-slate-500" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
          </svg>
          <p className="mb-1 text-sm font-medium text-gray-700 dark:text-slate-300">
            {dragOver ? 'Déposez le fichier ici' : 'Glissez-déposez votre fichier ici'}
          </p>
          <p className="text-xs text-gray-500 dark:text-slate-400">ou cliquez pour sélectionner un fichier (.xlsx, .csv)</p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls,.csv"
            onChange={(e) => e.target.files[0] && handleFile(e.target.files[0])}
            className="hidden"
          />
        </div>

        {file && (
          <div className="mt-4 flex items-center gap-3 rounded-lg bg-blue-50 px-4 py-3">
            <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-900 dark:text-blue-200">{file.name}</p>
              <p className="text-xs text-blue-700 dark:text-blue-300">{preview.length} ligne(s) détectée(s)</p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setFile(null);
                setPreview([]);
                setColumns([]);
              }}
              className="text-blue-600 hover:text-blue-800 min-h-[44px] min-w-[44px] inline-flex items-center justify-center"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {preview.length > 0 && (
          <div className="mt-6">
            <h3 className="mb-2 text-sm font-medium text-gray-700 dark:text-slate-300">
              Aperçu (10 premières lignes)
            </h3>
            <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-slate-700">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700 text-xs">
                <thead className="bg-gray-50 dark:bg-slate-700/50">
                  <tr>
                    {columns.map((col) => (
                      <th
                        key={col}
                        className={`whitespace-nowrap px-3 py-2 text-left font-medium ${
                          EXPECTED_COLUMNS.includes(col.toLowerCase().replace(/\s/g, '_'))
                            ? 'text-green-700 dark:text-green-400'
                            : 'text-amber-700 dark:text-amber-400'
                        }`}
                      >
                        {col}
                        {!EXPECTED_COLUMNS.includes(col.toLowerCase().replace(/\s/g, '_')) && (
                          <span className="ml-1 text-amber-500 dark:text-amber-400" title="Colonne non reconnue">
                            ?
                          </span>
                        )}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 bg-white dark:divide-slate-700/50 dark:bg-slate-800">
                  {preview.map((row, idx) => (
                    <tr key={idx}>
                      {columns.map((col) => (
                        <td key={col} className="whitespace-nowrap px-3 py-2 text-gray-700 dark:text-slate-300">
                          {String(row[col] ?? '')}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-2 text-xs text-gray-500 dark:text-slate-400">
              Vert : colonne attendue · Orange : colonne non reconnue (ignorée)
            </p>
          </div>
        )}

        {file && preview.length > 0 && (
          <div className="mt-6 flex justify-end">
            <button
              onClick={handleImport}
              disabled={importing}
              className="inline-flex w-full min-h-[44px] items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
            >
              {importing ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  Import en cours...
                </>
              ) : (
                <>
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
                  </svg>
                  Lancer l'import
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {importResult && (
        <div className={`rounded-xl border p-6 shadow-sm ${
          importResult.success
            ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950'
            : 'border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950'
        }`}>
          <div className="flex items-start gap-3">
            {importResult.success ? (
              <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
            ) : (
              <svg className="h-5 w-5 text-amber-600" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
              </svg>
            )}
            <div className="flex-1">
              <h3 className={`text-sm font-medium ${
                importResult.success ? 'text-green-800 dark:text-green-200' : 'text-amber-800 dark:text-amber-200'
              }`}>
                {importResult.message}
              </h3>
              {importResult.imported > 0 && (
                <p className="mt-1 text-sm text-green-700 dark:text-green-300">
                  {importResult.imported} alumni importé(s) avec succès.
                </p>
              )}
              {importResult.errors.length > 0 && (
                <div className="mt-3 space-y-1">
                  {importResult.errors.slice(0, 10).map((err, idx) => (
                    <p key={idx} className="text-xs text-amber-700 dark:text-amber-300">
                      Ligne {err.row || '?'}: {err.message || err}
                    </p>
                  ))}
                  {importResult.errors.length > 10 && (
                    <p className="text-xs text-amber-600 dark:text-amber-400">
                      ... et {importResult.errors.length - 10} autre(s) erreur(s)
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}
    </div>
  );
}
