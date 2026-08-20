import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ExcelImport from '../components/admin/ExcelImport'
import { importAPI, alumniAPI } from '../services/api'
import { downloadBlob } from '../utils/downloadBlob'

vi.mock('../utils/downloadBlob', () => ({
  downloadBlob: vi.fn(),
  prepareIOSWindow: vi.fn(),
}))

vi.mock('../services/api', () => ({
  importAPI: {
    uploadExcel: vi.fn(),
    downloadTemplate: vi.fn(),
    exportData: vi.fn(),
  },
  alumniAPI: { getAll: vi.fn() },
  careerAPI: { getByAlumni: vi.fn() },
}))

vi.mock('xlsx', async () => {
  const actual = await vi.importActual('xlsx')
  return {
    ...actual,
    // Dans le navigateur, write(..., { type: 'blob' }) est supporté. En Node (jsdom),
    // la lib ne reconnaît pas le type 'blob', on le simule pour tester la logique.
    write: vi.fn(() => new Blob(['mock-xlsx'])),
  }
})

beforeEach(() => {
  vi.clearAllMocks()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('ExcelImport - bouton "Exporter les données"', () => {
  it('déclenche le téléchargement via le backend (importAPI.exportData)', async () => {
    importAPI.exportData.mockResolvedValue({ data: new Blob(['xlsx-content']) })
    const user = userEvent.setup()

    render(<ExcelImport />)
    const button = screen.getByRole('button', { name: /Exporter les données/i })
    expect(button).toBeEnabled()

    await user.click(button)

    await waitFor(() => {
      expect(importAPI.exportData).toHaveBeenCalledTimes(1)
    })
    expect(downloadBlob).toHaveBeenCalledTimes(1)

    const [blob, filename] = downloadBlob.mock.calls[0]
    expect(blob).toBeInstanceOf(Blob)
    expect(filename).toMatch(/^alumni_export_\d{4}-\d{2}-\d{2}\.xlsx$/)

    expect(screen.queryByText(/Erreur lors de l'export des données/)).not.toBeInTheDocument()
  })

  it('basculer sur l\'export côté client si le backend échoue, sans erreur console', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    importAPI.exportData.mockRejectedValue(new Error('network down'))
    alumniAPI.getAll.mockResolvedValue({ data: [] })
    const user = userEvent.setup()

    render(<ExcelImport />)
    const button = screen.getByRole('button', { name: /Exporter les données/i })
    await user.click(button)

    await waitFor(() => {
      expect(alumniAPI.getAll).toHaveBeenCalledTimes(1)
    })
    expect(downloadBlob).toHaveBeenCalledTimes(1)

    const [blob, filename] = downloadBlob.mock.calls[0]
    expect(blob).toBeInstanceOf(Blob)
    expect(filename).toMatch(/^alumni_export_\d{4}-\d{2}-\d{2}\.xlsx$/)

    expect(screen.queryByText(/Erreur lors de l'export des données/)).not.toBeInTheDocument()
    expect(consoleErrorSpy).not.toHaveBeenCalled()
  })

  it('affiche une erreur si backend ET fallback échouent', async () => {
    importAPI.exportData.mockRejectedValue(new Error('network down'))
    alumniAPI.getAll.mockRejectedValue(new Error('backend down'))
    const user = userEvent.setup()

    render(<ExcelImport />)
    const button = screen.getByRole('button', { name: /Exporter les données/i })
    await user.click(button)

    await waitFor(() => {
      expect(screen.getByText(/Erreur lors de l'export des données/)).toBeInTheDocument()
    })
  })
})

describe('ExcelImport - zone tactile du bouton export (standard 44x44px)', () => {
  it('le bouton "Exporter les données" respecte la hauteur minimale tactile de 44px', () => {
    render(<ExcelImport />)
    const button = screen.getByRole('button', { name: /Exporter les données/i })

    const py = 2.5 * 4 // py-2.5 = 10px de padding haut/bas
    const lineHeight = 20 // text-sm line-height = 1.25rem = 20px
    const border = 2 // border = 1px haut + 1px bas
    const naturalHeight = py + py + lineHeight + border

    const minHMatch = button.className.match(/min-h-\[(\d+)px\]/)
    const enforcedMin = minHMatch ? Number(minHMatch[1]) : 0
    const effectiveHeight = Math.max(naturalHeight, enforcedMin)

    expect(effectiveHeight).toBeGreaterThanOrEqual(44)
  })
})
