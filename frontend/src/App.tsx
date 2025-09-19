import { Routes, Route } from 'react-router-dom'
import { AppShell, Text, Group, Button } from '@mantine/core'
import { Link, useLocation } from 'react-router-dom'
import InventoryPage from './pages/InventoryPage'
import ChatPage from './pages/ChatPage'

function App() {
  const location = useLocation()

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 200, breakpoint: 'sm' }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Text size="xl" fw={700}>Candy Bowl Store</Text>
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
          to="/chat" 
          variant={location.pathname === '/chat' ? 'filled' : 'subtle'}
          fullWidth
        >
          Chat with AI
        </Button>
      </AppShell.Navbar>

      <AppShell.Main>
        <Routes>
          <Route path="/" element={<InventoryPage />} />
          <Route path="/chat" element={<ChatPage />} />
        </Routes>
      </AppShell.Main>
    </AppShell>
  )
}

export default App
