import userEvent from '@testing-library/user-event'
import { render, screen, waitFor } from '@testing-library/react'
import { act } from 'react'
import { describe, expect, it, vi } from 'vitest'

import LoginPage from '../src/routes/login'

vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement> & { to?: string }) => (
    <a href={typeof to === 'string' ? to : undefined} {...props}>
      {children}
    </a>
  ),
  useNavigate: () => vi.fn(),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: (selector: any) => selector({ token: null, setToken: vi.fn() }),
}))

vi.mock('@/api/auth', () => ({
  login: vi.fn().mockRejectedValue(new Error('인증에 실패했습니다.')),
}))

describe('LoginPage', () => {
  it('shows error message when login fails', async () => {
    render(<LoginPage />)

    const user = userEvent.setup()
    await act(async () => {
      await user.type(screen.getByLabelText('사용자명'), 'wrong')
      await user.type(screen.getByLabelText('비밀번호'), 'wrongpass')
      await user.click(screen.getByRole('button', { name: '로그인' }))
    })

    await waitFor(() => {
      expect(screen.getByText('인증에 실패했습니다.')).toBeInTheDocument()
    })
  })
})
