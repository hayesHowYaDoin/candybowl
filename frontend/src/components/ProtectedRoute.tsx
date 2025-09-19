import type { ReactNode } from 'react'
import { Alert, Container, Button, Group } from '@mantine/core'
import { useAuth } from '../contexts/AuthContext'

interface ProtectedRouteProps {
  children: ReactNode
  requireAdmin?: boolean
}

export default function ProtectedRoute({ children, requireAdmin = false }: ProtectedRouteProps) {
  const { isAuthenticated, isAdmin, user, logout } = useAuth()

  if (!isAuthenticated()) {
    return (
      <Container size="sm" mt="xl">
        <Alert color="red" title="Authentication Required">
          You need to be logged in to access this page.
        </Alert>
      </Container>
    )
  }

  if (requireAdmin && !isAdmin()) {
    return (
      <Container size="sm" mt="xl">
        <Alert color="orange" title="Admin Access Required">
          <p>You need admin permissions to access this page.</p>
          <p>Current role: <strong>{user?.role}</strong></p>
          <Group mt="md">
            <Button variant="outline" onClick={logout}>
              Switch Account
            </Button>
          </Group>
        </Alert>
      </Container>
    )
  }

  return <>{children}</>
}