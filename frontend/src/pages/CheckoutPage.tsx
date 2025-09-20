import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Title,
  Card,
  Stack,
  Group,
  Text,
  Button,
  NumberInput,
  ActionIcon,
  Badge,
  Divider,
  Alert
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { useCart } from '../contexts/CartContext'

function CheckoutPage() {
  const navigate = useNavigate()
  const { items, updateQuantity, removeFromCart, getTotalPrice, clearCart } = useCart()

  const handleQuantityChange = (itemId: string, quantity: number) => {
    updateQuantity(itemId, quantity)
  }

  const handleRemoveItem = (itemId: string, itemName: string) => {
    removeFromCart(itemId)
    notifications.show({
      title: 'Item Removed',
      message: `${itemName} removed from cart`,
      color: 'orange'
    })
  }

  const handleContinueToPayment = () => {
    navigate('/payment')
  }

  if (items.length === 0) {
    return (
      <Container size="md">
        <Stack align="center" mt="xl">
          <Title order={2}>🛒 Your Cart is Empty</Title>
          <Text c="dimmed" mb="xl">Add some sweet treats from the inventory to get started!</Text>
          <Button color="candy" onClick={() => navigate('/')}>
            Continue Shopping
          </Button>
        </Stack>
      </Container>
    )
  }

  return (
    <Container size="md">
      <Group justify="space-between" align="center" mb="xl">
        <Title order={1} c="candy.7">🛒 Checkout</Title>
        <Button variant="subtle" onClick={() => navigate('/')}>
          ← Continue Shopping
        </Button>
      </Group>

      <Stack gap="md">
        {items.map((item) => (
          <Card key={item.item_id} shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" align="flex-start">
              <div style={{ flex: 1 }}>
                <Group justify="space-between" align="flex-start" mb="xs">
                  <div>
                    <Text fw={500} size="lg">{item.item_name}</Text>
                    <Text size="sm" c="dimmed" mb="xs">{item.description}</Text>
                    {item.selling_unit && (
                      <Badge variant="light" size="sm">{item.selling_unit}</Badge>
                    )}
                  </div>
                  <ActionIcon
                    variant="subtle"
                    color="red"
                    onClick={() => handleRemoveItem(item.item_id, item.item_name)}
                  >
                    🗑️
                  </ActionIcon>
                </Group>

                <Group justify="space-between" align="center">
                  <Group align="center">
                    <Text size="sm">Quantity:</Text>
                    <NumberInput
                      value={item.cartQuantity}
                      onChange={(value) => handleQuantityChange(item.item_id, Number(value) || 1)}
                      min={1}
                      max={item.quantity}
                      size="sm"
                      style={{ width: 80 }}
                    />
                    <Text size="xs" c="dimmed">
                      (max: {item.quantity})
                    </Text>
                  </Group>

                  <div style={{ textAlign: 'right' }}>
                    <Text size="sm" c="dimmed">
                      ${item.sell_price_usd.toFixed(2)} each
                    </Text>
                    <Text fw={700} size="lg" c="candy.8">
                      ${(item.sell_price_usd * item.cartQuantity).toFixed(2)}
                    </Text>
                  </div>
                </Group>
              </div>
            </Group>
          </Card>
        ))}

        <Divider my="md" />

        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Stack>
            <Group justify="space-between">
              <Text size="lg" fw={500}>Order Summary</Text>
            </Group>
            
            <Group justify="space-between">
              <Text>Total Items:</Text>
              <Text>{items.reduce((total, item) => total + item.cartQuantity, 0)}</Text>
            </Group>
            
            <Group justify="space-between">
              <Text size="lg" fw={700}>Total Price:</Text>
              <Text size="xl" fw={700} c="candy.8">
                ${getTotalPrice().toFixed(2)}
              </Text>
            </Group>

            <Group justify="space-between" mt="md">
              <Button
                variant="outline"
                color="red"
                onClick={() => {
                  clearCart()
                  notifications.show({
                    title: 'Cart Cleared',
                    message: 'All items removed from cart',
                    color: 'orange'
                  })
                }}
              >
                Clear Cart
              </Button>
              
              <Button
                size="lg"
                color="candy"
                onClick={handleContinueToPayment}
              >
                Continue to Payment
              </Button>
            </Group>
          </Stack>
        </Card>
      </Stack>
    </Container>
  )
}

export default CheckoutPage