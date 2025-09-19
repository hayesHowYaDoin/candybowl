import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import type { InventoryItem } from '../lib/api'

interface CartItem extends InventoryItem {
  cartQuantity: number
}

interface CartContextType {
  items: CartItem[]
  addToCart: (item: InventoryItem, quantity: number) => void
  removeFromCart: (itemId: string) => void
  updateQuantity: (itemId: string, quantity: number) => void
  getTotalItems: () => number
  getTotalPrice: () => number
  clearCart: () => void
}

const CartContext = createContext<CartContextType | undefined>(undefined)

interface CartProviderProps {
  children: ReactNode
}

export function CartProvider({ children }: CartProviderProps) {
  const [items, setItems] = useState<CartItem[]>([])

  // Load cart from localStorage on mount
  useEffect(() => {
    const savedCart = localStorage.getItem('candybowl-cart')
    if (savedCart) {
      try {
        setItems(JSON.parse(savedCart))
      } catch (error) {
        console.error('Failed to load cart from localStorage:', error)
      }
    }
  }, [])

  // Save cart to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('candybowl-cart', JSON.stringify(items))
  }, [items])

  const addToCart = (item: InventoryItem, quantity: number) => {
    setItems(prev => {
      const existingItem = prev.find(cartItem => cartItem.item_id === item.item_id)
      
      if (existingItem) {
        // Update quantity if item already in cart
        return prev.map(cartItem =>
          cartItem.item_id === item.item_id
            ? { ...cartItem, cartQuantity: Math.min(cartItem.cartQuantity + quantity, item.quantity) }
            : cartItem
        )
      } else {
        // Add new item to cart
        return [...prev, { ...item, cartQuantity: Math.min(quantity, item.quantity) }]
      }
    })
  }

  const removeFromCart = (itemId: string) => {
    setItems(prev => prev.filter(item => item.item_id !== itemId))
  }

  const updateQuantity = (itemId: string, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(itemId)
      return
    }

    setItems(prev =>
      prev.map(item =>
        item.item_id === itemId
          ? { ...item, cartQuantity: Math.min(quantity, item.quantity) }
          : item
      )
    )
  }

  const getTotalItems = () => {
    return items.reduce((total, item) => total + item.cartQuantity, 0)
  }

  const getTotalPrice = () => {
    return items.reduce((total, item) => total + (item.sell_price_usd * item.cartQuantity), 0)
  }

  const clearCart = () => {
    setItems([])
  }

  return (
    <CartContext.Provider value={{
      items,
      addToCart,
      removeFromCart,
      updateQuantity,
      getTotalItems,
      getTotalPrice,
      clearCart
    }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const context = useContext(CartContext)
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider')
  }
  return context
}