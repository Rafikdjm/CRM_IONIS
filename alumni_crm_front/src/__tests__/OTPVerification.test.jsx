import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import OTPVerification from '../components/OTPVerification'
import { ThemeProvider } from '../contexts/ThemeContext'

const otpEffectsCss = readFileSync(
  join(dirname(fileURLToPath(import.meta.url)), '../components/otpEffects.css'),
  'utf8',
)

function renderOTP(props) {
  return render(
    <ThemeProvider>
      <OTPVerification {...props} />
    </ThemeProvider>
  )
}

beforeEach(() => {
  vi.restoreAllMocks()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('OTPVerification - success checkmark SVG', () => {
  it('renders a hand-drawn checkmark path with two line segments', () => {
    renderOTP({ success: true })

    const path = document.querySelector('.otp-check-path')
    expect(path).toBeInTheDocument()
    expect(path.getAttribute('d')).toBe('M19 33 L28 42 L45 24')

    const commands = path.getAttribute('d').match(/[LM]/g) || []
    expect(commands.filter((c) => c === 'L')).toHaveLength(2)

    expect(path.getAttribute('pathLength')).toBe('100')
  })

  it('has no clock or loader icon path', () => {
    renderOTP({ success: true })

    const path = document.querySelector('.otp-check-path')
    const d = path.getAttribute('d')
    expect(d).not.toMatch(/circle|ellipse|clock/i)
  })

  it('keeps the stroke-dashoffset draw animation CSS', () => {
    const checkPathBlock = otpEffectsCss.match(/\.otp-check-path\s*\{[^}]*\}/)?.[0] || ''
    const keyframes = otpEffectsCss.match(/@keyframes otp-draw\s*\{[^}]*\}/)?.[0] || ''

    expect(checkPathBlock).toContain('stroke-dasharray: 100')
    expect(checkPathBlock).toContain('stroke-dashoffset: 100')
    expect(checkPathBlock).toContain('animation: otp-draw')
    expect(keyframes).toContain('stroke-dashoffset: 0')
  })
})

describe('OTPVerification - particle burst', () => {
  it('mounts the particle layer with 22 particles on success', () => {
    renderOTP({ success: true })

    const layer = document.querySelector('.otp-particle-layer')
    expect(layer).toBeInTheDocument()
    expect(layer.querySelectorAll('.otp-particle')).toHaveLength(22)
  })

  it('does not render particles when prefers-reduced-motion is active', () => {
    const realMatchMedia = window.matchMedia
    window.matchMedia = vi.fn().mockImplementation((query) => ({
      matches: query === '(prefers-reduced-motion: reduce)',
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }))

    renderOTP({ success: true })

    expect(document.querySelector('.otp-particle-layer')).not.toBeInTheDocument()
    expect(document.querySelector('.otp-check-path')).toBeInTheDocument()

    window.matchMedia = realMatchMedia
  })
})

describe('OTPVerification - success UI', () => {
  it('renders the success title', () => {
    renderOTP({ success: true })

    expect(screen.getByText('E-mail vérifié')).toBeInTheDocument()
  })
})
