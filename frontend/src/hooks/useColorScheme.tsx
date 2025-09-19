import { createContext, useContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'

type ColorScheme = 'light' | 'dark'

interface ColorSchemeContextType {
  colorScheme: ColorScheme
  toggleColorScheme: () => void
}

const ColorSchemeContext = createContext<ColorSchemeContextType | undefined>(undefined)

interface ColorSchemeProviderProps {
  children: ReactNode
}

export function ColorSchemeProvider({ children }: ColorSchemeProviderProps) {
  const [colorScheme, setColorScheme] = useState<ColorScheme>('dark')

  // Load saved theme from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('mantine-color-scheme') as ColorScheme
    if (saved && (saved === 'light' || saved === 'dark')) {
      setColorScheme(saved)
    }
  }, [])

  // Save theme to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('mantine-color-scheme', colorScheme)
  }, [colorScheme])

  const toggleColorScheme = () => {
    setColorScheme(prev => prev === 'dark' ? 'light' : 'dark')
  }

  return (
    <ColorSchemeContext.Provider value={{ colorScheme, toggleColorScheme }}>
      {children}
    </ColorSchemeContext.Provider>
  )
}

export function useColorScheme() {
  const context = useContext(ColorSchemeContext)
  if (!context) {
    throw new Error('useColorScheme must be used within a ColorSchemeProvider')
  }
  return context
}