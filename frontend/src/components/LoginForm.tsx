import { useState } from 'react'
import {
  Container,
  Paper,
  Title,
  TextInput,
  PasswordInput,
  Button,
  Text,
  Group,
  Alert,
  Stack
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { useAuth } from '../contexts/AuthContext'

interface LoginFormProps {
  onToggleMode: () => void
}

export default function LoginForm({ onToggleMode }: LoginFormProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const { login } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(username, password)
      notifications.show({
        title: 'Welcome back!',
        message: 'You have successfully logged in.',
        color: 'green'
      })
    } catch (error: any) {
      setError(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container size={420} my={40}>
      <Title ta="center" mb="xl">
        Candy Bowl Store
      </Title>
      
      <Paper withBorder shadow="md" p={30} radius="md">
        <Title order={2} ta="center" mb="md">
          Sign In
        </Title>

        {error && (
          <Alert color="red" mb="md">
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <Stack>
            <TextInput
              label="Username"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />

            <PasswordInput
              label="Password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <Button
              type="submit"
              fullWidth
              loading={loading}
              disabled={!username || !password}
            >
              Sign In
            </Button>
          </Stack>
        </form>

        <Group justify="center" mt="md">
          <Text size="sm">
            Don't have an account?{' '}
            <Button variant="subtle" size="sm" onClick={onToggleMode}>
              Sign up
            </Button>
          </Text>
        </Group>
      </Paper>
    </Container>
  )
}