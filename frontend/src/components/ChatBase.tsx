import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { 
  Container, 
  Title, 
  Paper, 
  TextInput, 
  Button, 
  Group, 
  Text, 
  Stack,
  Box,
  Alert,
  Loader,
  useMantineColorScheme
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { 
  startRequestChat, 
  startHaggleChat, 
  startRestockChat, 
  sendChatMessage,
  closeChatSession,
  type ChatSession 
} from '../lib/api'

type ChatMode = 'request' | 'haggle' | 'restock'

interface Message {
  id: string
  content: string
  sender: 'user' | 'ai'
  timestamp: Date
}

interface ChatBaseProps {
  mode: ChatMode
  title: string
  description: string
}

export default function ChatBase({ mode, title, description }: ChatBaseProps) {
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { colorScheme } = useMantineColorScheme()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const startChatMutation = useMutation({
    mutationFn: async () => {
      switch (mode) {
        case 'request':
          return startRequestChat()
        case 'haggle':
          return startHaggleChat()
        case 'restock':
          return startRestockChat()
        default:
          throw new Error('Invalid chat mode')
      }
    },
    onSuccess: (data) => {
      console.log('Chat session started:', data)
      setCurrentSession(data)
      setMessages([])
      
      if (data.response) {
        console.log('Adding initial message:', data.response)
        setMessages([{
          id: '1',
          content: data.response,
          sender: 'ai',
          timestamp: new Date()
        }])
      } else {
        console.log('No initial response received')
      }
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Chat Error',
        message: error.response?.data?.error || 'Failed to start chat session',
        color: 'red',
      })
    },
  })

  const sendMessageMutation = useMutation({
    mutationFn: sendChatMessage,
    onSuccess: (data) => {
      const aiMessage: Message = {
        id: Date.now().toString() + '-ai',
        content: data.response,
        sender: 'ai',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMessage])
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Message Error',
        message: error.response?.data?.error || 'Failed to send message',
        color: 'red',
      })
    },
  })

  // Auto-start chat when component mounts
  useEffect(() => {
    if (!currentSession && !startChatMutation.isPending) {
      startChatMutation.mutate()
    }
  }, [])

  // Cleanup chat session when component unmounts
  useEffect(() => {
    return () => {
      if (currentSession?.chat_id) {
        closeChatSession(currentSession.chat_id).catch(() => {
          // Silently handle cleanup errors
        })
      }
    }
  }, [currentSession?.chat_id])

  const handleSendMessage = () => {
    if (!inputValue.trim() || !currentSession) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    
    sendMessageMutation.mutate({
      chat_id: currentSession.chat_id,
      message: inputValue
    })

    setInputValue('')
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSendMessage()
    }
  }

  // Get theme-aware colors for chat bubbles
  const getUserBubbleColor = () => {
    return colorScheme === 'dark' ? 'candy.9' : 'candy.0'
  }

  const getAiBubbleColor = () => {
    return colorScheme === 'dark' ? 'gray.8' : 'gray.1'
  }

  const getUserTextColor = () => {
    return colorScheme === 'dark' ? 'candy.2' : 'candy.9'
  }

  const getAiTextColor = () => {
    return colorScheme === 'dark' ? 'gray.2' : 'gray.9'
  }

  if (startChatMutation.isPending) {
    return (
      <Container size="md">
        <Title order={1} mb="xl">{title}</Title>
        <Group justify="center" mt="xl">
          <Loader size="lg" />
          <Text>Starting chat session...</Text>
        </Group>
      </Container>
    )
  }

  if (startChatMutation.isError) {
    return (
      <Container size="md">
        <Title order={1} mb="xl">{title}</Title>
        <Alert color="red" title="Error" mt="xl">
          Failed to start chat session. Please try again later.
        </Alert>
      </Container>
    )
  }

  return (
    <Container size="md">
      <Title order={1} mb="md">{title}</Title>
      <Text size="sm" c="dimmed" mb="xl">{description}</Text>
      
      <Paper withBorder p="md" style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
        <Box style={{ flex: 1, overflowY: 'auto', marginBottom: '1rem' }}>
          {messages.length === 0 ? (
            <Group justify="center" style={{ height: '100%' }} align="center">
              <Text c="dimmed">🤖 Starting chat session...</Text>
            </Group>
          ) : (
            <Stack gap="md">
              {messages.map((message) => (
                <Box key={message.id}>
                  <Group gap="xs" mb="xs">
                    <Text size="sm" fw={500} c={message.sender === 'user' ? getUserTextColor() : getAiTextColor()}>
                      {message.sender === 'user' ? 'You' : 'Gemini'}
                    </Text>
                    <Text size="xs" c="dimmed">
                      {message.timestamp.toLocaleTimeString()}
                    </Text>
                  </Group>
                  <Paper 
                    p="sm" 
                    bg={message.sender === 'user' ? getUserBubbleColor() : getAiBubbleColor()}
                    style={{ maxWidth: '80%', marginLeft: message.sender === 'user' ? 'auto' : '0' }}
                  >
                    <Text size="sm" c={colorScheme === 'dark' ? 'white' : 'dark'} style={{ whiteSpace: 'pre-wrap' }}>
                      {message.content}
                    </Text>
                  </Paper>
                </Box>
              ))}
              {sendMessageMutation.isPending && (
                <Group justify="center">
                  <Loader size="sm" />
                  <Text size="sm" c="dimmed">AI is thinking...</Text>
                </Group>
              )}
              <div ref={messagesEndRef} />
            </Stack>
          )}
        </Box>
        
        <Group gap="xs">
          <TextInput
            flex={1}
            placeholder="Type your message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={sendMessageMutation.isPending || !currentSession}
          />
          <Button 
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || sendMessageMutation.isPending || !currentSession}
            color="candy"
            style={{
              transition: 'all 0.15s ease',
              transform: 'scale(1)'
            }}
            onMouseDown={(e) => {
              e.currentTarget.style.transform = 'scale(0.95)'
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = 'scale(1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)'
            }}
          >
            Send
          </Button>
        </Group>
      </Paper>

      {mode === 'restock' && (
        <Alert color="blue" title="Auto Restock Mode" mt="md">
          In this mode, the AI will automatically analyze user requests and restock the candy bowl 
          with items it believes will be profitable. The initial message will show its restocking plan.
        </Alert>
      )}
    </Container>
  )
}