import { useState } from 'react'
import {
  PaymentElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js'
import {
  Stack,
  Button,
  Text,
  Alert,
  Group,
  Card
} from '@mantine/core'
import { notifications } from '@mantine/notifications'

interface PaymentFormProps {
  clientSecret: string
  amount: number
  onSuccess: () => void
  onCancel: () => void
}

export default function PaymentForm({ 
  clientSecret, 
  amount, 
  onSuccess, 
  onCancel 
}: PaymentFormProps) {
  const stripe = useStripe()
  const elements = useElements()
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()

    if (!stripe || !elements) {
      return
    }

    setIsLoading(true)
    setMessage(null)

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/payment-success`,
      },
      redirect: 'if_required',
    })

    if (error) {
      setMessage(error.message || 'An unexpected error occurred.')
      notifications.show({
        title: 'Payment Failed',
        message: error.message || 'Please try again',
        color: 'red',
      })
    } else {
      notifications.show({
        title: 'Payment Successful!',
        message: `Payment of $${amount.toFixed(2)} completed`,
        color: 'green',
      })
      onSuccess()
    }

    setIsLoading(false)
  }

  return (
    <Card shadow="sm" padding="xl" radius="md" withBorder>
      <form onSubmit={handleSubmit}>
        <Stack>
          <Text size="lg" fw={500} mb="md">
            Payment Details
          </Text>
          
          <Text size="sm" c="dimmed" mb="md">
            Total: ${amount.toFixed(2)}
          </Text>

          <PaymentElement 
            options={{
              layout: 'tabs'
            }}
          />

          {message && (
            <Alert color="red" mt="md">
              {message}
            </Alert>
          )}

          <Group justify="space-between" mt="xl">
            <Button
              variant="outline"
              onClick={onCancel}
              disabled={isLoading}
            >
              Cancel
            </Button>
            
            <Button
              type="submit"
              loading={isLoading}
              disabled={!stripe || !elements}
              size="lg"
            >
              Pay ${amount.toFixed(2)}
            </Button>
          </Group>

          <Text size="xs" c="dimmed" ta="center" mt="md">
            🔒 Payments are secured by Stripe
          </Text>
          
          {import.meta.env.DEV && (
            <Alert color="blue" variant="light" mt="md">
              <Text size="sm" fw={500}>Test Mode</Text>
              <Text size="xs">
                Use card number: 4242 4242 4242 4242
                <br />
                Any future expiry date and CVC
              </Text>
            </Alert>
          )}
        </Stack>
      </form>
    </Card>
  )
}