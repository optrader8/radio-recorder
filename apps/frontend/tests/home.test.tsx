import type { AnchorHTMLAttributes } from 'react'

import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import HomePage from '../src/routes/index'

vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, ...props }: AnchorHTMLAttributes<HTMLAnchorElement> & { to?: string }) => (
    <a href={typeof to === 'string' ? to : undefined} {...props} />
  ),
  createFileRoute: vi.fn(),
}))

describe('HomePage', () => {
  it('shows the primary headline and call to action', () => {
    render(<HomePage />)

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Radio Recorder')
    expect(screen.getByRole('link', { name: /get started/i })).toHaveAttribute('href', '/dashboard')
  })
})
