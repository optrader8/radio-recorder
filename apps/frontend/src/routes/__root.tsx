import { Outlet, createRootRoute } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/router-devtools'

function RootComponent() {
  return (
    <>
      <div className="min-h-screen bg-background font-sans antialiased">
        <Outlet />
      </div>
      <TanStackRouterDevtools />
    </>
  )
}

export default RootComponent