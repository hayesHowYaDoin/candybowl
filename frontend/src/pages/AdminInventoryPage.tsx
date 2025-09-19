import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Container,
  Title,
  Tabs,
  Stack,
  TextInput,
  NumberInput,
  Textarea,
  Button,
  Group,
  Alert,
  Table,
  ActionIcon,
  Modal,
  Text,
  Card
} from '@mantine/core'
import { notifications } from '@mantine/notifications'
import { api } from '../lib/api'
import type { InventoryItem } from '../lib/api'

interface AddItemForm {
  item_name: string
  link: string
  quantity: number
  purchase_price: number
  sell_price: number
  description: string
}

export default function AdminInventoryPage() {
  const [activeTab, setActiveTab] = useState('add')
  const [addForm, setAddForm] = useState<AddItemForm>({
    item_name: '',
    link: '',
    quantity: 0,
    purchase_price: 0,
    sell_price: 0,
    description: ''
  })
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<InventoryItem | null>(null)
  const [editQuantity, setEditQuantity] = useState(0)
  const [editPrice, setEditPrice] = useState(0)

  const queryClient = useQueryClient()

  // Fetch inventory
  const { data: inventory, isLoading, error } = useQuery({
    queryKey: ['inventory'],
    queryFn: async () => {
      const response = await api.get('/api/inventory')
      return response.data.inventory as InventoryItem[]
    }
  })

  // Add item mutation
  const addItemMutation = useMutation({
    mutationFn: async (item: AddItemForm) => {
      const response = await api.post('/api/inventory', item)
      return response.data
    },
    onSuccess: (data) => {
      notifications.show({
        title: 'Success!',
        message: `Item "${data.item_name}" added successfully`,
        color: 'green'
      })
      queryClient.invalidateQueries({ queryKey: ['inventory'] })
      setAddForm({
        item_name: '',
        link: '',
        quantity: 0,
        purchase_price: 0,
        sell_price: 0,
        description: ''
      })
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error.response?.data?.error || 'Failed to add item',
        color: 'red'
      })
    }
  })

  // Update item mutation
  const updateItemMutation = useMutation({
    mutationFn: async ({ item_id, quantity, sell_price }: { item_id: string, quantity?: number, sell_price?: number }) => {
      const updateData: any = {}
      if (quantity !== undefined) updateData.quantity = quantity
      if (sell_price !== undefined) updateData.sell_price = sell_price
      
      const response = await api.put(`/api/inventory/${item_id}`, updateData)
      return response.data
    },
    onSuccess: (data) => {
      notifications.show({
        title: 'Success!',
        message: data.message,
        color: 'green'
      })
      queryClient.invalidateQueries({ queryKey: ['inventory'] })
      setEditModalOpen(false)
      setEditingItem(null)
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error.response?.data?.error || 'Failed to update item',
        color: 'red'
      })
    }
  })

  // Delete item mutation
  const deleteItemMutation = useMutation({
    mutationFn: async (item_id: string) => {
      const response = await api.delete(`/api/inventory/${item_id}`)
      return response.data
    },
    onSuccess: (data) => {
      notifications.show({
        title: 'Success!',
        message: data.message,
        color: 'green'
      })
      queryClient.invalidateQueries({ queryKey: ['inventory'] })
    },
    onError: (error: any) => {
      notifications.show({
        title: 'Error',
        message: error.response?.data?.error || 'Failed to delete item',
        color: 'red'
      })
    }
  })

  const handleAddItem = () => {
    addItemMutation.mutate(addForm)
  }

  const handleEditItem = (item: InventoryItem) => {
    setEditingItem(item)
    setEditQuantity(item.quantity)
    setEditPrice(item.sell_price_usd)
    setEditModalOpen(true)
  }

  const handleUpdateItem = () => {
    if (!editingItem) return
    
    const updates: any = {}
    if (editQuantity !== editingItem.quantity) updates.quantity = editQuantity
    if (editPrice !== editingItem.sell_price_usd) updates.sell_price = editPrice
    
    if (Object.keys(updates).length > 0) {
      updateItemMutation.mutate({ item_id: editingItem.item_id, ...updates })
    } else {
      setEditModalOpen(false)
    }
  }

  const handleDeleteItem = (item: InventoryItem) => {
    if (confirm(`Are you sure you want to remove "${item.item_name}" from inventory?`)) {
      deleteItemMutation.mutate(item.item_id)
    }
  }

  if (error) {
    return (
      <Container>
        <Alert color="red" title="Error">
          Failed to load inventory data. Please try again later.
        </Alert>
      </Container>
    )
  }

  return (
    <Container size="xl">
      <Title order={1} mb="xl">Inventory Management</Title>
      
      <Tabs value={activeTab} onChange={(value) => setActiveTab(value || 'add')}>
        <Tabs.List>
          <Tabs.Tab value="add">Add Items</Tabs.Tab>
          <Tabs.Tab value="manage">Manage Items</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="add" pt="md">
          <Card withBorder p="xl">
            <Title order={2} mb="md">Add New Item</Title>
            
            <Stack>
              <TextInput
                label="Item Name"
                placeholder="Enter item name"
                value={addForm.item_name}
                onChange={(e) => setAddForm(prev => ({ ...prev, item_name: e.target.value }))}
                required
              />

              <TextInput
                label="Product Link"
                placeholder="Enter product URL"
                value={addForm.link}
                onChange={(e) => setAddForm(prev => ({ ...prev, link: e.target.value }))}
                required
              />

              <Group grow>
                <NumberInput
                  label="Quantity"
                  placeholder="Enter quantity"
                  value={addForm.quantity}
                  onChange={(value) => setAddForm(prev => ({ ...prev, quantity: Number(value) || 0 }))}
                  min={0}
                  required
                />

                <NumberInput
                  label="Purchase Price ($)"
                  placeholder="Enter purchase price"
                  value={addForm.purchase_price}
                  onChange={(value) => setAddForm(prev => ({ ...prev, purchase_price: Number(value) || 0 }))}
                  min={0}
                  decimalScale={2}
                  required
                />

                <NumberInput
                  label="Sell Price ($)"
                  placeholder="Enter sell price"
                  value={addForm.sell_price}
                  onChange={(value) => setAddForm(prev => ({ ...prev, sell_price: Number(value) || 0 }))}
                  min={0}
                  decimalScale={2}
                  required
                />
              </Group>

              <Textarea
                label="Description"
                placeholder="Enter item description"
                value={addForm.description}
                onChange={(e) => setAddForm(prev => ({ ...prev, description: e.target.value }))}
                minRows={3}
                required
              />

              <Button
                onClick={handleAddItem}
                loading={addItemMutation.isPending}
                disabled={!addForm.item_name || !addForm.link || !addForm.description || addForm.sell_price <= addForm.purchase_price}
              >
                Add Item
              </Button>
            </Stack>
          </Card>
        </Tabs.Panel>

        <Tabs.Panel value="manage" pt="md">
          <Card withBorder>
            <Title order={2} mb="md">Current Inventory</Title>
            
            {isLoading ? (
              <Text>Loading inventory...</Text>
            ) : inventory && inventory.length > 0 ? (
              <Table striped highlightOnHover>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Item Name</Table.Th>
                    <Table.Th>Unit Info</Table.Th>
                    <Table.Th>Quantity</Table.Th>
                    <Table.Th>Purchase Price</Table.Th>
                    <Table.Th>Sell Price</Table.Th>
                    <Table.Th>Profit Margin</Table.Th>
                    <Table.Th>Actions</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {inventory.map((item) => {
                    const profitMargin = ((item.sell_price_usd - item.total_purchase_price_usd) / item.total_purchase_price_usd * 100).toFixed(1)
                    return (
                      <Table.Tr key={item.item_id}>
                        <Table.Td>
                          <div>
                            <Text fw={500}>{item.item_name}</Text>
                            <Text size="sm" c="dimmed" truncate>
                              {item.description}
                            </Text>
                          </div>
                        </Table.Td>
                        <Table.Td>
                          <Text size="sm">
                            {item.selling_unit || 'No unit info'}
                          </Text>
                        </Table.Td>
                        <Table.Td>{item.quantity}</Table.Td>
                        <Table.Td>${item.total_purchase_price_usd.toFixed(2)}</Table.Td>
                        <Table.Td>${item.sell_price_usd.toFixed(2)}</Table.Td>
                        <Table.Td>
                          <Text c={parseFloat(profitMargin) > 0 ? 'green' : 'red'}>
                            {profitMargin}%
                          </Text>
                        </Table.Td>
                        <Table.Td>
                          <Group gap="xs">
                            <ActionIcon
                              variant="outline"
                              onClick={() => handleEditItem(item)}
                            >
                              ✏️
                            </ActionIcon>
                            <ActionIcon
                              variant="outline"
                              color="red"
                              onClick={() => handleDeleteItem(item)}
                            >
                              🗑️
                            </ActionIcon>
                          </Group>
                        </Table.Td>
                      </Table.Tr>
                    )
                  })}
                </Table.Tbody>
              </Table>
            ) : (
              <Text c="dimmed">No items in inventory</Text>
            )}
          </Card>
        </Tabs.Panel>
      </Tabs>

      {/* Edit Modal */}
      <Modal
        opened={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        title="Edit Item"
        centered
      >
        {editingItem && (
          <Stack>
            <Text fw={500}>{editingItem.item_name}</Text>
            
            <NumberInput
              label="Quantity"
              value={editQuantity}
              onChange={(value) => setEditQuantity(Number(value) || 0)}
              min={0}
            />
            
            <NumberInput
              label="Sell Price ($)"
              value={editPrice}
              onChange={(value) => setEditPrice(Number(value) || 0)}
              min={0}
              decimalScale={2}
            />
            
            <Group justify="flex-end">
              <Button variant="outline" onClick={() => setEditModalOpen(false)}>
                Cancel
              </Button>
              <Button
                onClick={handleUpdateItem}
                loading={updateItemMutation.isPending}
              >
                Update
              </Button>
            </Group>
          </Stack>
        )}
      </Modal>
    </Container>
  )
}