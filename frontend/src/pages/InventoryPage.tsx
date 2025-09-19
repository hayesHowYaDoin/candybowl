import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
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
  Stack
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { getInventory, purchaseItem, type InventoryItem } from '../lib/api'

function InventoryPage() {
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null)
  const [purchaseQuantity, setPurchaseQuantity] = useState(1)
  const [modalOpened, setModalOpened] = useState(false)
  
  const queryClient = useQueryClient()

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

  return (
    <Container size="lg">
      <Title order={1} mb="xl">Candy Bowl Inventory</Title>
      
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
                    <Text size="sm" c="dimmed" mb="md">{item.description}</Text>
                    
                    <Group justify="space-between" mb="md">
                      <Badge color="blue" variant="light">
                        {item.quantity} in stock
                      </Badge>
                      <Text fw={700} size="lg" c="green">
                        ${item.sell_price_usd.toFixed(2)}
                      </Text>
                    </Group>
                  </div>
                  
                  <Button 
                    fullWidth 
                    mt="md" 
                    radius="md"
                    onClick={() => handlePurchaseClick(item)}
                    disabled={item.quantity === 0}
                  >
                    Buy Now
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
        title="Purchase Item"
        centered
      >
        {selectedItem && (
          <Stack>
            <Text size="lg" fw={500}>{selectedItem.item_name}</Text>
            <Text size="sm" c="dimmed">{selectedItem.description}</Text>
            
            <NumberInput
              label="Quantity"
              value={purchaseQuantity}
              onChange={(value) => setPurchaseQuantity(Number(value) || 1)}
              min={1}
              max={selectedItem.quantity}
            />
            
            <Group justify="space-between">
              <Text>Unit Price:</Text>
              <Text fw={500}>${selectedItem.sell_price_usd.toFixed(2)}</Text>
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
                onClick={handlePurchaseConfirm}
                loading={purchaseMutation.isPending}
              >
                Confirm Purchase
              </Button>
            </Group>
          </Stack>
        )}
      </Modal>
    </Container>
  )
}

export default InventoryPage