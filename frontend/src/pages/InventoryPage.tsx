import { useState } from 'react'
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
        <Group justify="center" mt="xl">
          <Loader size="lg" />
        </Group>
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

  const handleAddToCartConfirm = () => {
    if (selectedItem) {
      addToCart(selectedItem, purchaseQuantity)
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
        <Title order={1}>Candy Bowl Inventory</Title>
        <Button
          variant="outline"
          onClick={() => navigate('/checkout')}
          leftSection={<span>🛒</span>}
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
          {availableItems.map((item) => (
            <Grid.Col key={item.item_id} span={{ base: 12, sm: 6, md: 4 }}>
              <Card shadow="sm" padding="lg" radius="md" withBorder h="100%">
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
                      <Badge color="blue" variant="light">
                        {item.quantity} in stock
                      </Badge>
                      <Text fw={700} size="lg" c="green">
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
                    onClick={() => handleAddToCart(item)}
                    disabled={item.quantity === 0}
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
              <Text fw={700} size="lg" c="green">
                ${(selectedItem.sell_price_usd * purchaseQuantity).toFixed(2)}
              </Text>
            </Group>
            
            <Group justify="flex-end" mt="md">
              <Button variant="outline" onClick={() => setModalOpened(false)}>
                Cancel
              </Button>
              <Button 
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