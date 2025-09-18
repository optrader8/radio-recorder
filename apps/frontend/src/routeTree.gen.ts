// Route tree definition for TanStack Router.

import { createRoute, createRootRoute } from '@tanstack/react-router'

// Import route components
import RootComponent from './routes/__root'
import IndexComponent from './routes/index'
import DashboardComponent from './routes/dashboard'
import LoginComponent from './routes/login'
import RegisterComponent from './routes/register'
import SchedulesComponent from './routes/schedules'

// Create file routes
const rootRoute = createRootRoute({
  component: RootComponent,
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: IndexComponent,
})

const dashboardRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'dashboard',
  component: DashboardComponent,
})

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'login',
  component: LoginComponent,
})

const registerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'register',
  component: RegisterComponent,
})

const schedulesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'schedules',
  component: SchedulesComponent,
})

// Build route tree
export const routeTree = rootRoute.addChildren([
  indexRoute,
  dashboardRoute,
  loginRoute,
  registerRoute,
  schedulesRoute,
])
