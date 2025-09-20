import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { 
  Container, 
  Title, 
  Grid, 
  Card, 
  Text, 
  Badge, 
  Button, 
  NumberInput,
  Group,
  Loader,
  Alert,
  Modal,
  Stack,
  ActionIcon
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { getInventory, purchaseItem } from '../lib/api'
import type { InventoryItem } from '../lib/api'
import { useCart } from '../contexts/CartContext'

function InventoryPage() {
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null)
  const [purchaseQuantity, setPurchaseQuantity] = useState(1)
  const [modalOpened, setModalOpened] = useState(false)
  const cartButtonRef = useRef<HTMLButtonElement>(null)
  
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { addToCart, getTotalItems } = useCart()

  const { data: inventory, isLoading, error } = useQuery({
    queryKey: ['inventory'],
    queryFn: getInventory,
  })

  const purchaseMutation = useMutation({
    mutationFn: purchaseItem,
    onSuccess: (data) => {
      notifications.show({
        title: 'Purchase Successful!',
        message: `Purchased ${data.quantity_purchased} units for $${data.total_price.toFixed(2)}`,
        color: 'green',
      })
      queryClient.invalidateQueries({ queryKey: ['inventory'] })
      setModalOpened(false)
      setPurchaseQuantity(1)
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Purchase Failed',
        message: error.response?.data?.error || 'An error occurred',
        color: 'red',
      })
    },
  })

  const handlePurchaseClick = (item: InventoryItem) => {
    setSelectedItem(item)
    setPurchaseQuantity(1)
    setModalOpened(true)
  }

  const handlePurchaseConfirm = () => {
    if (selectedItem) {
      purchaseMutation.mutate({
        item_id: selectedItem.item_id,
        quantity: purchaseQuantity,
      })
    }
  }

  if (isLoading) {
    return (
      <Container size="lg">
        <Group justify="space-between" align="center" mb="xl">
          <Title order={1} c="candy.7">Inventory</Title>
          <Button
            variant="filled"
            color="candy"
            disabled
            leftSection={<span>🛒</span>}
          >
            Cart (0)
          </Button>
        </Group>
        
        <Grid>
          {[...Array(6)].map((_, index) => (
            <Grid.Col key={index} span={{ base: 12, sm: 6, md: 4 }}>
              <Card shadow="sm" padding="lg" radius="md" withBorder h="100%">
                <Stack justify="space-between" h="100%">
                  <div>
                    <div style={{ 
                      height: '24px', 
                      backgroundColor: '#f0f0f0', 
                      borderRadius: '4px',
                      marginBottom: '8px',
                      animation: 'buttonPulse 1.5s ease-in-out infinite'
                    }} />
                    <div style={{ 
                      height: '60px', 
                      backgroundColor: '#f8f8f8', 
                      borderRadius: '4px',
                      marginBottom: '16px',
                      animation: 'buttonPulse 1.5s ease-in-out infinite 0.2s'
                    }} />
                    <div style={{ 
                      height: '20px', 
                      backgroundColor: '#f0f0f0', 
                      borderRadius: '4px',
                      width: '60%',
                      animation: 'buttonPulse 1.5s ease-in-out infinite 0.4s'
                    }} />
                  </div>
                  <div style={{ 
                    height: '36px', 
                    backgroundColor: '#e8e8e8', 
                    borderRadius: '8px',
                    marginTop: '16px',
                    animation: 'buttonPulse 1.5s ease-in-out infinite 0.6s'
                  }} />
                </Stack>
              </Card>
            </Grid.Col>
          ))}
        </Grid>
      </Container>
    )
  }

  if (error) {
    return (
      <Container size="lg">
        <Alert color="red" title="Error" mt="xl">
          Failed to load inventory. Please try again later.
        </Alert>
      </Container>
    )
  }

  const availableItems = inventory?.filter(item => item.quantity > 0) || []

  const handleAddToCart = (item: InventoryItem) => {
    setSelectedItem(item)
    setPurchaseQuantity(1)
    setModalOpened(true)
  }

  const triggerCartAnimation = () => {
    if (cartButtonRef.current) {
      cartButtonRef.current.style.animation = 'none'
      setTimeout(() => {
        if (cartButtonRef.current) {
          cartButtonRef.current.style.animation = 'cartBounce 0.6s ease'
        }
      }, 10)
    }
  }

  const handleAddToCartConfirm = () => {
    if (selectedItem) {
      addToCart(selectedItem, purchaseQuantity)
      triggerCartAnimation()
      notifications.show({
        title: 'Added to Cart!',
        message: `Added ${purchaseQuantity} ${selectedItem.item_name} to cart`,
        color: 'green',
      })
      setModalOpened(false)
      setPurchaseQuantity(1)
    }
  }

  return (
    <Container size="lg">
      <Group justify="space-between" align="center" mb="xl">
        <Title order={1} c="candy.7">Inventory</Title>
        <Button
          ref={cartButtonRef}
          variant="filled"
          color="candy"
          onClick={() => navigate('/checkout')}
          leftSection={<span>🛒</span>}
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
          Cart ({getTotalItems()})
        </Button>
      </Group>
      
      {availableItems.length === 0 ? (
        <Alert color="yellow" title="No Items Available">
          The candy bowl is currently empty. Check back later!
        </Alert>
      ) : (
        <Grid>
          {availableItems.map((item, index) => (
            <Grid.Col key={item.item_id} span={{ base: 12, sm: 6, md: 4 }}>
              <Card 
                shadow="sm" 
                padding="lg" 
                radius="md" 
                withBorder 
                h="100%"
                style={{
                  transition: 'all 0.2s ease',
                  cursor: 'pointer',
                  animation: `cardSlideIn 0.5s ease ${index * 0.1}s both`,
                  ':hover': {
                    transform: 'translateY(-2px) scale(1.02)',
                    boxShadow: '0 8px 30px rgba(215, 22, 255, 0.15)',
                    borderColor: 'rgba(215, 22, 255, 0.3)'
                  }
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px) scale(1.02)'
                  e.currentTarget.style.boxShadow = '0 8px 30px rgba(215, 22, 255, 0.15)'
                  e.currentTarget.style.borderColor = 'rgba(215, 22, 255, 0.3)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0) scale(1)'
                  e.currentTarget.style.boxShadow = ''
                  e.currentTarget.style.borderColor = ''
                }}
              >
                <Stack justify="space-between" h="100%">
                  <div>
                    <Text fw={500} size="lg" mb="xs">{item.item_name}</Text>
                    <Text size="sm" c="dimmed" mb="xs">{item.description}</Text>
                    
                    {item.selling_unit && (
                      <Text size="sm" fw={500} c="blue" mb="md">
                        Unit: {item.selling_unit}
                      </Text>
                    )}
                    
                    <Group justify="space-between" mb="md">
                      <Badge color="candy" variant="light">
                        {item.quantity} in stock
                      </Badge>
                      <Text fw={700} size="lg" c="candy.8">
                        ${item.sell_price_usd.toFixed(2)}
                        {item.selling_unit && (
                          <Text size="xs" c="dimmed" span> / {item.selling_unit}</Text>
                        )}
                      </Text>
                    </Group>
                  </div>
                  
                  <Button 
                    fullWidth 
                    mt="md" 
                    radius="md"
                    color="candy"
                    onClick={() => handleAddToCart(item)}
                    disabled={item.quantity === 0}
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
                    Add to Cart
                  </Button>
                </Stack>
              </Card>
            </Grid.Col>
          ))}
        </Grid>
      )}

      <Modal
        opened={modalOpened}
        onClose={() => setModalOpened(false)}
        title="Add to Cart"
        centered
      >
        {selectedItem && (
          <Stack>
            <Text size="lg" fw={500}>{selectedItem.item_name}</Text>
            <Text size="sm" c="dimmed">{selectedItem.description}</Text>
            
            {selectedItem.selling_unit && (
              <Group>
                <Text size="sm" fw={500}>You're buying:</Text>
                <Badge variant="light" color="blue">{selectedItem.selling_unit}</Badge>
              </Group>
            )}
            
            <NumberInput
              label={`Quantity${selectedItem.selling_unit ? ` (${selectedItem.selling_unit} each)` : ''}`}
              value={purchaseQuantity}
              onChange={(value) => setPurchaseQuantity(Number(value) || 1)}
              min={1}
              max={selectedItem.quantity}
            />
            
            <Group justify="space-between">
              <Text>Unit Price:</Text>
              <Text fw={500}>
                ${selectedItem.sell_price_usd.toFixed(2)}
                {selectedItem.selling_unit && (
                  <Text size="xs" c="dimmed" span> per {selectedItem.selling_unit}</Text>
                )}
              </Text>
            </Group>
            
            <Group justify="space-between">
              <Text fw={700}>Total:</Text>
              <Text fw={700} size="lg" c="candy.8">
                ${(selectedItem.sell_price_usd * purchaseQuantity).toFixed(2)}
              </Text>
            </Group>
            
            <Group justify="flex-end" mt="md">
              <Button variant="outline" onClick={() => setModalOpened(false)}>
                Cancel
              </Button>
              <Button 
                color="candy"
                onClick={handleAddToCartConfirm}
              >
                Add to Cart
              </Button>
            </Group>
          </Stack>
        )}
      </Modal>
    </Container>
  )
}

export default InventoryPage