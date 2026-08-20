import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { downloadBlob, isIOSDevice, prepareIOSWindow } from '../utils/downloadBlob'

const REAL_UA = navigator.userAgent
const REAL_PLATFORM = navigator.platform

function stubURL() {
  const createObjectURL = vi.fn(() => 'blob:mock-url')
  const revokeObjectURL = vi.fn()
  Object.defineProperty(window.URL, 'createObjectURL', {
    configurable: true,
    writable: true,
    value: createObjectURL,
  })
  Object.defineProperty(window.URL, 'revokeObjectURL', {
    configurable: true,
    writable: true,
    value: revokeObjectURL,
  })
  return { createObjectURL, revokeObjectURL }
}

function setUA(ua, platform = '') {
  Object.defineProperty(navigator, 'userAgent', { configurable: true, value: ua })
  Object.defineProperty(navigator, 'platform', { configurable: true, value: platform })
}

beforeEach(() => {
  vi.useFakeTimers()
  vi.spyOn(console, 'log').mockImplementation(() => {})
})

afterEach(() => {
  vi.useRealTimers()
  vi.restoreAllMocks()
  setUA(REAL_UA, REAL_PLATFORM)
})

describe('isIOSDevice', () => {
  it('détecte iPhone/iPad via userAgent', () => {
    setUA('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148')
    expect(isIOSDevice()).toBe(true)
  })

  it('détecte un iPad (tablette) qui se fait passer pour un Mac', () => {
    setUA('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15', 'MacIntel')
    Object.defineProperty(navigator, 'maxTouchPoints', { configurable: true, value: 5 })
    expect(isIOSDevice()).toBe(true)
  })

  it('renvoie false sur desktop / Android', () => {
    setUA('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36', 'Win32')
    expect(isIOSDevice()).toBe(false)
  })

  it('détecte Chrome iOS (WebKit) comme un appareil iOS', () => {
    setUA('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148', 'iPhone')
    expect(isIOSDevice()).toBe(true)
  })
})

describe('prepareIOSWindow', () => {
  it('sur iOS : ouvre une fenêtre vide de façon synchrone', () => {
    setUA('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148', 'iPhone')
    const openSpy = vi.spyOn(window, 'open').mockReturnValue({ location: {} })
    expect(prepareIOSWindow()).toEqual({ location: {} })
    expect(openSpy).toHaveBeenCalledWith('', '_blank')
  })

  it('sur non-iOS : ne tente pas d\'ouvrir de fenêtre', () => {
    setUA('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36', 'Win32')
    const openSpy = vi.spyOn(window, 'open')
    expect(prepareIOSWindow()).toBeNull()
    expect(openSpy).not.toHaveBeenCalled()
  })
})

describe('downloadBlob', () => {
  it('non-iOS : ancre ajoutée au DOM puis retirée, clic déclenché, revoke différé', () => {
    setUA('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36', 'Win32')
    const { createObjectURL, revokeObjectURL } = stubURL()
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
    const appendSpy = vi.spyOn(document.body, 'appendChild').mockImplementation((el) => el)
    const removeSpy = vi.spyOn(document.body, 'removeChild').mockImplementation((el) => el)

    downloadBlob(new Blob(['x']), 'alumni_export_2026-08-01.xlsx')

    expect(createObjectURL).toHaveBeenCalledTimes(1)

    const link = appendSpy.mock.calls.map((c) => c[0]).find((el) => el.tagName === 'A')
    expect(link).not.toBeNull()
    expect(link.href).toBe('blob:mock-url')
    expect(link.getAttribute('download')).toBe('alumni_export_2026-08-01.xlsx')
    expect(clickSpy).toHaveBeenCalledTimes(1)
    expect(removeSpy).toHaveBeenCalledTimes(1)

    expect(revokeObjectURL).not.toHaveBeenCalled()
    vi.advanceTimersByTime(1000)
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:mock-url')
  })

  it('iOS : ouvre le blob dans un nouvel onglet au lieu du download direct', () => {
    setUA('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148', 'iPhone')
    const { revokeObjectURL } = stubURL()
    const openSpy = vi.spyOn(window, 'open').mockReturnValue({ location: {} })
    const appendSpy = vi.spyOn(document.body, 'appendChild')

    downloadBlob(new Blob(['x']), 'alumni_export_2026-08-01.xlsx')

    expect(openSpy).toHaveBeenCalledWith('blob:mock-url', '_blank')
    expect(appendSpy).not.toHaveBeenCalled()

    expect(revokeObjectURL).not.toHaveBeenCalled()
    vi.advanceTimersByTime(1000)
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:mock-url')
  })

  it('iOS : si window.open est bloqué, bascule sur la méthode <a download>', () => {
    setUA('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148', 'iPhone')
    const { revokeObjectURL } = stubURL()
    vi.spyOn(window, 'open').mockReturnValue(null)
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
    const appendSpy = vi.spyOn(document.body, 'appendChild')

    downloadBlob(new Blob(['x']), 'alumni_export_2026-08-01.xlsx')

    expect(clickSpy).toHaveBeenCalledTimes(1)
    expect(appendSpy).toHaveBeenCalled()

    vi.advanceTimersByTime(1000)
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:mock-url')
  })

  it('iOS : avec une fenêtre pré-ouverte, il la redirige sans ré-ouvrir de popup', () => {
    setUA('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148', 'iPhone')
    const { revokeObjectURL } = stubURL()
    const openSpy = vi.spyOn(window, 'open')
    const win = { location: { href: '' } }

    downloadBlob(new Blob(['x']), 'alumni_export_2026-08-01.xlsx', win)

    expect(openSpy).not.toHaveBeenCalled()
    expect(win.location.href).toBe('blob:mock-url')
    expect(revokeObjectURL).not.toHaveBeenCalled()
    vi.advanceTimersByTime(1000)
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:mock-url')
  })
})
