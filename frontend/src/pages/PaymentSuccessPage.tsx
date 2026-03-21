import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Stack,
  Title,
  Text,
  Button,
  Card,
  Group
} from '@mantine/core'

export default function PaymentSuccessPage() {
  const navigate = useNavigate()

  useEffect(() => {
    // Auto-redirect after 10 seconds
    const timer = setTimeout(() => {
      navigate('/')
    }, 10000)

    return () => clearTimeout(timer)
  }, [navigate])

  return (
    <Container size="sm">
      <Stack align="center" mt="xl">
        <Card shadow="lg" padding="xl" radius="md" withBorder w="100%">
          <Stack align="center">
            <div style={{ fontSize: '4rem' }}>✅</div>
            
            <Title order={2} ta="center" c="green">
              Payment Successful!
            </Title>
            
            <Text ta="center" c="dimmed" mb="md">
              Thank you for your purchase. Your order has been confirmed and your items will be available for pickup.
            </Text>

            <Text size="sm" ta="center" c="dimmed" mb="xl">
              A confirmation email has been sent to your registered email address.
            </Text>

            <Group>
              <Button
                variant="outline"
                onClick={() => navigate('/')}
              >
                Continue Shopping
              </Button>
              
              <Button
                onClick={() => navigate('/')}
              >
                Back to Inventory
              </Button>
            </Group>

            <Text size="xs" c="dimmed" ta="center" mt="md">
              You will be automatically redirected in 10 seconds
            </Text>
          </Stack>
        </Card>
      </Stack>
    </Container>
  )
}