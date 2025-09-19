import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { MantineProvider, createTheme } from '@mantine/core'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { Notifications } from '@mantine/notifications'
import { ColorSchemeProvider, useColorScheme } from './hooks/useColorScheme'
import { AuthProvider } from './contexts/AuthContext'
import { CartProvider } from './contexts/CartContext'
import App from './App.tsx'
import '@mantine/core/styles.css'
import '@mantine/notifications/styles.css'

const queryClient = new QueryClient()
const theme = createTheme({})

function AppWithTheme() {
  const { colorScheme } = useColorScheme()
  
  return (
    <MantineProvider theme={theme} forceColorScheme={colorScheme}>
      <Notifications />
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </MantineProvider>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ColorSchemeProvider>
        <AuthProvider>
          <CartProvider>
            <AppWithTheme />
          </CartProvider>
        </AuthProvider>
      </ColorSchemeProvider>
    </QueryClientProvider>
  </StrictMode>,
)
