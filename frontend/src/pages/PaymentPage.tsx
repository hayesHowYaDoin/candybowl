import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Elements } from '@stripe/react-stripe-js'
import {
  Container,
  Title,
  Stack,
  Card,
  Text,
  Group,
  Button,
  Loader,
  Alert,
  Divider
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { stripePromise } from '../lib/stripe'
import { useCart } from '../contexts/CartContext'
import { api } from '../lib/api'
import PaymentForm from '../components/PaymentForm'

interface PaymentIntent {
  client_secret: string
  payment_intent_id: string
}

export default function PaymentPage() {
  const navigate = useNavigate()
  const { items, getTotalPrice, clearCart } = useCart()
  const [clientSecret, setClientSecret] = useState<string>('')
  const [paymentIntentId, setPaymentIntentId] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const totalAmount = getTotalPrice()

  useEffect(() => {
    if (items.length === 0) {
      navigate('/checkout')
      return
    }

    createPaymentIntent()
  }, [items.length])

  const createPaymentIntent = async () => {
    try {
      setIsLoading(true)
      setError(null)

      const cartItems = items.map(item => ({
        item_id: item.item_id,
        item_name: item.item_name,
        quantity: item.cartQuantity,
        unit_price: item.sell_price_usd,
        total_price: item.sell_price_usd * item.cartQuantity
      }))

      const response = await api.post<PaymentIntent>('/api/payments/create-intent', {
        amount: totalAmount,
        cart_items: cartItems
      })

      setClientSecret(response.data.client_secret)
      setPaymentIntentId(response.data.payment_intent_id)
    } catch (error: any) {
      console.error('Failed to create payment intent:', error)
      setError(error.response?.data?.error || 'Failed to initialize payment')
      notifications.show({
        title: 'Payment Error',
        message: 'Failed to initialize payment. Please try again.',
        color: 'red'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handlePaymentSuccess = async () => {
    try {
      const cartItems = items.map(item => ({
        item_id: item.item_id,
        item_name: item.item_name,
        quantity: item.cartQuantity,
        unit_price: item.sell_price_usd,
        total_price: item.sell_price_usd * item.cartQuantity
      }))

      await api.post('/api/payments/confirm', {
        payment_intent_id: paymentIntentId,
        cart_items: cartItems
      })

      clearCart()
      navigate('/payment-success')
    } catch (error: any) {
      console.error('Failed to confirm payment:', error)
      notifications.show({
        title: 'Payment Confirmation Error',
        message: 'Payment succeeded but confirmation failed. Please contact support.',
        color: 'orange'
      })
    }
  }

  const handleCancel = () => {
    navigate('/checkout')
  }

  if (items.length === 0) {
    return null // Will redirect in useEffect
  }

  return (
    <Container size="md">
      <Group justify="space-between" align="center" mb="xl">
        <Title order={1}>Payment</Title>
        <Button variant="subtle" onClick={() => navigate('/checkout')}>
          ← Back to Checkout
        </Button>
      </Group>

      <Stack>
        {/* Order Summary */}
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Stack>
            <Text size="lg" fw={500}>Order Summary</Text>
            
            {items.map((item) => (
              <Group key={item.item_id} justify="space-between">
                <div>
                  <Text size="sm" fw={500}>{item.item_name}</Text>
                  <Text size="xs" c="dimmed">
                    {item.cartQuantity} × ${item.sell_price_usd.toFixed(2)}
                    {item.selling_unit && ` (${item.selling_unit})`}
                  </Text>
                </div>
                <Text size="sm" fw={500}>
                  ${(item.sell_price_usd * item.cartQuantity).toFixed(2)}
                </Text>
              </Group>
            ))}
            
            <Divider />
            
            <Group justify="space-between">
              <Text size="lg" fw={700}>Total</Text>
              <Text size="xl" fw={700} c="green">
                ${totalAmount.toFixed(2)}
              </Text>
            </Group>
          </Stack>
        </Card>

        {/* Payment Form */}
        {isLoading && (
          <Card shadow="sm" padding="xl" radius="md" withBorder>
            <Stack align="center">
              <Loader />
              <Text>Initializing payment...</Text>
            </Stack>
          </Card>
        )}

        {error && (
          <Alert color="red" title="Payment Error">
            {error}
            <Button
              variant="outline"
              size="sm"
              mt="md"
              onClick={createPaymentIntent}
            >
              Try Again
            </Button>
          </Alert>
        )}

        {clientSecret && !isLoading && !error && (
          <Elements
            stripe={stripePromise}
            options={{
              clientSecret,
              appearance: {
                theme: 'stripe',
              },
            }}
          >
            <PaymentForm
              clientSecret={clientSecret}
              amount={totalAmount}
              onSuccess={handlePaymentSuccess}
              onCancel={handleCancel}
            />
          </Elements>
        )}
      </Stack>
    </Container>
  )
}