import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn('🔐 Received 401 - clearing invalid token')
      localStorage.removeItem('auth_token')
      delete api.defaults.headers.common['Authorization']
      // Force page reload to trigger re-authentication
      window.location.href = '/auth'
    }
    return Promise.reject(error)
  }
)

export interface InventoryItem {
  item_id: string
  item_name: string
  link: string
  quantity: number
  total_purchase_price_usd: number
  sell_price_usd: number
  description: string
  unit_type?: string
  unit_size?: string
  package_count?: number
  selling_unit?: string
}

export interface PurchaseRequest {
  item_id: string
  quantity: number
}

export interface PurchaseResponse {
  message: string
  item_id: string
  quantity_purchased: number
  total_price: number
  remaining_quantity: number
}

export interface ChatSession {
  chat_id: string
  response?: string
}

export interface ChatMessage {
  chat_id: string
  message: string
}

export interface ChatResponse {
  response: string
}

// API functions
export const getInventory = async (): Promise<InventoryItem[]> => {
  try {
    console.log('🔍 Fetching inventory...')
    const response = await api.get<{ inventory: InventoryItem[] }>('/api/inventory')
    console.log('✅ Inventory response:', response.status, response.data)
    return response.data.inventory
  } catch (error: any) {
    console.error('❌ Inventory fetch error:', error.response?.status, error.response?.data, error.message)
    throw error
  }
}

export const purchaseItem = async (request: PurchaseRequest): Promise<PurchaseResponse> => {
  const response = await api.post<PurchaseResponse>('/api/purchase', request)
  return response.data
}

export const startRequestChat = async (): Promise<ChatSession> => {
  const response = await api.get<ChatSession>('/chat/request')
  console.log('Request chat response:', response.data)
  return response.data
}

export const startHaggleChat = async (): Promise<ChatSession> => {
  const response = await api.get<ChatSession>('/chat/haggle')
  console.log('Haggle chat response:', response.data)
  return response.data
}

export const startRestockChat = async (): Promise<ChatSession> => {
  const response = await api.get<ChatSession>('/chat/restock')
  return response.data
}

export const sendChatMessage = async (request: ChatMessage): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>('/chat/message', request)
  return response.data
}

export const closeChatSession = async (chatId: string): Promise<void> => {
  await api.delete(`/chat/${chatId}/close`)
}