import { Routes, Route } from 'react-router-dom'
import { AppShell, Text, Group, Button, ActionIcon, Loader, Center } from '@mantine/core'
import { Link, useLocation } from 'react-router-dom'
import { useColorScheme } from './hooks/useColorScheme'
import { useAuth } from './contexts/AuthContext'
import AuthPage from './pages/AuthPage'
import InventoryPage from './pages/InventoryPage'
import CheckoutPage from './pages/CheckoutPage'
import RequestChatPage from './pages/RequestChatPage'
import HaggleChatPage from './pages/HaggleChatPage'
import RestockChatPage from './pages/RestockChatPage'
import AdminInventoryPage from './pages/AdminInventoryPage'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  const location = useLocation()
  const { colorScheme, toggleColorScheme } = useColorScheme()
  const { isAuthenticated, isAdmin, user, logout, loading } = useAuth()

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <Center h="100vh">
        <Loader size="lg" />
      </Center>
    )
  }

  // Show auth page if not authenticated
  if (!isAuthenticated()) {
    return <AuthPage />
  }

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 200, breakpoint: 'sm' }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Text size="xl" fw={700}>Candy Bowl Store</Text>
          
          <Group>
            <Text size="sm">
              Welcome, <strong>{user?.username}</strong>
              {isAdmin() && (
                <Text component="span" c="blue" ml="xs">(Admin)</Text>
              )}
            </Text>
            
            <ActionIcon
              variant="outline"
              size="lg"
              onClick={toggleColorScheme}
              title={`Switch to ${colorScheme === 'dark' ? 'light' : 'dark'} mode`}
            >
              {colorScheme === 'dark' ? '☀️' : '🌙'}
            </ActionIcon>
            
            <Button variant="outline" size="sm" onClick={logout}>
              Logout
            </Button>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <Button 
          component={Link} 
          to="/" 
          variant={location.pathname === '/' ? 'filled' : 'subtle'}
          fullWidth
          mb="sm"
        >
          Inventory
        </Button>
        
        <Button 
          component={Link} 
          to="/chat/request" 
          variant={location.pathname === '/chat/request' ? 'filled' : 'subtle'}
          fullWidth
          mb="xs"
        >
          Request Items
        </Button>
        
        <Button 
          component={Link} 
          to="/chat/haggle" 
          variant={location.pathname === '/chat/haggle' ? 'filled' : 'subtle'}
          fullWidth
          mb="xs"
        >
          Haggle Prices
        </Button>
        
        {isAdmin() && (
          <>
            <Button 
              component={Link} 
              to="/chat/restock" 
              variant={location.pathname === '/chat/restock' ? 'filled' : 'subtle'}
              fullWidth
              mb="xs"
            >
              Auto Restock
            </Button>
            
            <Button 
              component={Link} 
              to="/admin/inventory" 
              variant={location.pathname === '/admin/inventory' ? 'filled' : 'subtle'}
              fullWidth
            >
              Manage Inventory
            </Button>
          </>
        )}
      </AppShell.Navbar>

      <AppShell.Main>
        <Routes>
          <Route path="/" element={<InventoryPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/chat/request" element={<RequestChatPage />} />
          <Route path="/chat/haggle" element={<HaggleChatPage />} />
          <Route path="/chat/restock" element={
            <ProtectedRoute requireAdmin>
              <RestockChatPage />
            </ProtectedRoute>
          } />
          <Route path="/admin/inventory" element={
            <ProtectedRoute requireAdmin>
              <AdminInventoryPage />
            </ProtectedRoute>
          } />
        </Routes>
      </AppShell.Main>
    </AppShell>
  )
}

export default App
