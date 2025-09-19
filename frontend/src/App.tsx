import { Routes, Route } from 'react-router-dom'
import { AppShell, Text, Group, Button, ActionIcon } from '@mantine/core'
import { Link, useLocation } from 'react-router-dom'
import { useColorScheme } from './hooks/useColorScheme'
import InventoryPage from './pages/InventoryPage'
import RequestChatPage from './pages/RequestChatPage'
import HaggleChatPage from './pages/HaggleChatPage'
import RestockChatPage from './pages/RestockChatPage'

function App() {
  const location = useLocation()
  const { colorScheme, toggleColorScheme } = useColorScheme()

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 200, breakpoint: 'sm' }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Text size="xl" fw={700}>Candy Bowl Store</Text>
          <ActionIcon
            variant="outline"
            size="lg"
            onClick={toggleColorScheme}
            title={`Switch to ${colorScheme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {colorScheme === 'dark' ? '☀️' : '🌙'}
          </ActionIcon>
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
        <Button 
          component={Link} 
          to="/chat/restock" 
          variant={location.pathname === '/chat/restock' ? 'filled' : 'subtle'}
          fullWidth
        >
          Auto Restock
        </Button>
      </AppShell.Navbar>

      <AppShell.Main>
        <Routes>
          <Route path="/" element={<InventoryPage />} />
          <Route path="/chat/request" element={<RequestChatPage />} />
          <Route path="/chat/haggle" element={<HaggleChatPage />} />
          <Route path="/chat/restock" element={<RestockChatPage />} />
        </Routes>
      </AppShell.Main>
    </AppShell>
  )
}

export default App
