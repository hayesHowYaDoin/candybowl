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
import './styles/animations.css'

const queryClient = new QueryClient()
const theme = createTheme({
  primaryColor: 'candy',
  colors: {
    candy: [
      '#fef7ff',
      '#fdeeff',
      '#f9dcff',
      '#f3b8ff',
      '#ec8bff',
      '#e550ff',
      '#d716ff',
      '#b80ae6',
      '#9406bf',
      '#70049a'
    ]
  },
  primaryShade: { light: 6, dark: 7 },
  fontFamily: 'Inter, system-ui, Avenir, Helvetica, Arial, sans-serif',
  headings: {
    fontFamily: 'Nunito, system-ui, Avenir, Helvetica, Arial, sans-serif',
    fontWeight: '700',
    sizes: {
      h1: { fontSize: '2.125rem', lineHeight: '1.3' },
      h2: { fontSize: '1.625rem', lineHeight: '1.35' },
      h3: { fontSize: '1.375rem', lineHeight: '1.4' },
      h4: { fontSize: '1.125rem', lineHeight: '1.45' },
      h5: { fontSize: '1rem', lineHeight: '1.5' },
      h6: { fontSize: '0.875rem', lineHeight: '1.5' },
    }
  }
})

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
