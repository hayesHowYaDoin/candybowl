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
  SegmentedControl,
  Alert,
  Loader
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { 
  startRequestChat, 
  startHaggleChat, 
  startRestockChat, 
  sendChatMessage,
  type ChatSession 
} from '../lib/api'

type ChatMode = 'request' | 'haggle' | 'restock'

interface Message {
  id: string
  content: string
  sender: 'user' | 'ai'
  timestamp: Date
}

function ChatPage() {
  const [chatMode, setChatMode] = useState<ChatMode>('request')
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const startChatMutation = useMutation({
    mutationFn: async (mode: ChatMode) => {
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
      setCurrentSession(data)
      setMessages([])
      
      if (data.response) {
        setMessages([{
          id: '1',
          content: data.response,
          sender: 'ai',
          timestamp: new Date()
        }])
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

  const handleModeChange = (mode: ChatMode) => {
    setChatMode(mode)
    setCurrentSession(null)
    setMessages([])
  }

  const handleStartChat = () => {
    startChatMutation.mutate(chatMode)
  }

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

  const getChatModeDescription = (mode: ChatMode) => {
    switch (mode) {
      case 'request':
        return 'Request new items to be added to the candy bowl'
      case 'haggle':
        return 'Negotiate prices for items currently in the bowl'
      case 'restock':
        return 'AI automatically restocks the bowl with profitable items'
      default:
        return ''
    }
  }

  return (
    <Container size="md">
      <Title order={1} mb="xl">Chat with Candy Bowl AI</Title>
      
      <Stack gap="lg">
        <Paper withBorder p="md">
          <Text size="sm" c="dimmed" mb="md">Select a chat mode:</Text>
          <SegmentedControl
            value={chatMode}
            onChange={(value) => handleModeChange(value as ChatMode)}
            data={[
              { label: 'Request Items', value: 'request' },
              { label: 'Haggle Prices', value: 'haggle' },
              { label: 'Auto Restock', value: 'restock' },
            ]}
            fullWidth
          />
          <Text size="sm" c="dimmed" mt="md">
            {getChatModeDescription(chatMode)}
          </Text>
        </Paper>

        {!currentSession ? (
          <Group justify="center">
            <Button 
              size="lg" 
              onClick={handleStartChat}
              loading={startChatMutation.isPending}
            >
              Start {chatMode.charAt(0).toUpperCase() + chatMode.slice(1)} Chat
            </Button>
          </Group>
        ) : (
          <Paper withBorder p="md" style={{ height: '500px', display: 'flex', flexDirection: 'column' }}>
            <Box style={{ flex: 1, overflowY: 'auto', marginBottom: '1rem' }}>
              {messages.length === 0 ? (
                <Group justify="center" style={{ height: '100%' }} align="center">
                  <Text c="dimmed">Start chatting with the AI!</Text>
                </Group>
              ) : (
                <Stack gap="md">
                  {messages.map((message) => (
                    <Box key={message.id}>
                      <Group gap="xs" mb="xs">
                        <Text size="sm" fw={500} c={message.sender === 'user' ? 'blue' : 'green'}>
                          {message.sender === 'user' ? 'You' : 'AI'}
                        </Text>
                        <Text size="xs" c="dimmed">
                          {message.timestamp.toLocaleTimeString()}
                        </Text>
                      </Group>
                      <Paper 
                        p="sm" 
                        bg={message.sender === 'user' ? 'blue.0' : 'green.0'}
                        style={{ maxWidth: '80%', marginLeft: message.sender === 'user' ? 'auto' : '0' }}
                      >
                        <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>
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
                disabled={sendMessageMutation.isPending}
              />
              <Button 
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || sendMessageMutation.isPending}
              >
                Send
              </Button>
            </Group>
          </Paper>
        )}

        {chatMode === 'restock' && (
          <Alert color="blue" title="Auto Restock Mode">
            In this mode, the AI will automatically analyze user requests and restock the candy bowl 
            with items it believes will be profitable. The initial message will show its restocking plan.
          </Alert>
        )}
      </Stack>
    </Container>
  )
}

export default ChatPage