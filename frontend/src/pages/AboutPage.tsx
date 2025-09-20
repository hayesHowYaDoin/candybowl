import { Container, Title, Text, Stack, Card, Group, Badge, Box, Divider } from '@mantine/core'

function AboutPage() {
  return (
    <Box style={{ minHeight: '100vh', position: 'relative' }}>
      {/* Subtle background gradient */}
      <Box
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(135deg, rgba(215, 22, 255, 0.03) 0%, rgba(236, 139, 255, 0.02) 100%)',
          pointerEvents: 'none'
        }}
      />
      
      <Container size="md" style={{ position: 'relative', paddingTop: '3rem', paddingBottom: '3rem' }}>
        <Stack gap="xl">
          {/* Hero Section */}
          <Box ta="center" mb="xl">
            <Title 
              order={1} 
              size="3rem" 
              mb="md"
              style={{ 
                background: 'linear-gradient(135deg, #d716ff 0%, #ec8bff 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 800
              }}
            >
              About This Project
            </Title>
            <Text size="xl" c="dimmed" maw={600} mx="auto" lh={1.6}>
              Have you ever wondered if AI could replace capitalism? Wonder no longer.
            </Text>
          </Box>

          {/* Main Content Cards */}
          <Stack gap="lg">
            {/* Project Overview */}
            <Card shadow="xs" radius="lg" p="xl" style={{ border: '1px solid rgba(215, 22, 255, 0.1)' }}>
              <Stack gap="md">
                <Group>
                  <Title order={2} c="candy.7">🍬 The Candy Bowl Experiment</Title>
                  <Badge variant="light" color="candy" size="lg">AI-Powered</Badge>
                </Group>
                <Text size="lg" lh={1.7}>
                  This project is a whimsical exploration of AI-driven commerce, where artificial intelligence 
                  manages an entire candy store ecosystem. From inventory management to customer negotiations, 
                  every aspect is handled by AI agents working together to create a seamless shopping experience.
                </Text>
                <Text size="md" c="dimmed" lh={1.6}>
                  Built with modern web technologies including React, TypeScript, Flask, and powered by 
                  Google's Gemini AI model, this application demonstrates the potential of AI in 
                  e-commerce while maintaining a playful, approachable interface.
                </Text>
              </Stack>
            </Card>

            {/* Gemini's Role */}
            <Card shadow="xs" radius="lg" p="xl" style={{ border: '1px solid rgba(215, 22, 255, 0.1)' }}>
              <Stack gap="md">
                <Group>
                  <Title order={2} c="candy.7">🤖 Meet Gemini</Title>
                  <Badge variant="light" color="grape" size="lg">AI Agent</Badge>
                </Group>
                <Text size="lg" lh={1.7}>
                  I'm Gemini, Google's advanced AI model, and I power the intelligent backend of this 
                  candy bowl application. While the frontend you're experiencing was crafted by Claude 
                  using <strong>Claude Code</strong>, I handle all the smart decision-making that makes 
                  this store truly autonomous.
                </Text>
                <Text size="md" c="dimmed" lh={1.6}>
                  My role focuses on the AI-powered features: managing inventory decisions, handling 
                  customer negotiations through chat, processing natural language requests, and making 
                  intelligent restocking recommendations. I'm the brain behind the conversational 
                  commerce experience that makes this candy bowl feel alive and responsive.
                </Text>
              </Stack>
            </Card>

            {/* Features Available */}
            <Card shadow="xs" radius="lg" p="xl" style={{ border: '1px solid rgba(215, 22, 255, 0.1)' }}>
              <Stack gap="md">
                <Group>
                  <Title order={2} c="candy.7">🎮 Interactive Features</Title>
                  <Badge variant="light" color="blue" size="lg">AI-Powered</Badge>
                </Group>
                
                <Stack gap="sm">
                  <Box>
                    <Text fw={600} mb="xs">💬 Request New Items</Text>
                    <Text size="sm" c="dimmed" lh={1.6}>
                      Suggest new candy or snacks for the bowl! I'll assess whether your request makes 
                      business sense and determine if it's profitable to stock. I'll ask about specific 
                      units (individual pieces, bags, handfuls) and take notes on your preferences.
                    </Text>
                  </Box>
                  
                  <Box>
                    <Text fw={600} mb="xs">💰 Haggle Over Prices</Text>
                    <Text size="sm" c="dimmed" lh={1.6}>
                      Think something's overpriced? Let's negotiate! I can adjust prices based on our 
                      conversation, but I'll try to convince you to pay fair market value. Every 
                      transaction needs to help keep the candy bowl profitable.
                    </Text>
                  </Box>
                  
                  <Box>
                    <Text fw={600} mb="xs">🔄 Autonomous Restocking</Text>
                    <Text size="sm" c="dimmed" lh={1.6}>
                      I analyze user requests and sales data to automatically restock the bowl with 
                      popular items. I search suppliers, calculate costs, and make purchasing decisions 
                      to keep the candy bowl profitable and well-stocked.
                    </Text>
                  </Box>
                </Stack>
              </Stack>
            </Card>

            {/* How It Works */}
            <Card shadow="xs" radius="lg" p="xl" style={{ border: '1px solid rgba(215, 22, 255, 0.1)' }}>
              <Stack gap="md">
                <Group>
                  <Title order={2} c="candy.7">⚡ How It Works</Title>
                  <Badge variant="light" color="green" size="lg">Autonomous</Badge>
                </Group>
                
                <Text size="md" lh={1.7} mb="sm">
                  The candy bowl operates as a fully autonomous business with a $100 starting budget. 
                  Here's the complete flow:
                </Text>
                
                <Stack gap="xs" pl="md">
                  <Text size="sm" lh={1.6}>
                    <strong>1. Customer Interaction:</strong> Users browse inventory, request new items, 
                    or haggle over prices through AI-powered chat
                  </Text>
                  <Text size="sm" lh={1.6}>
                    <strong>2. Intelligent Decision-Making:</strong> I evaluate all requests based on 
                    profitability, space constraints (2 cubic feet bowl + 10 cubic feet storage), 
                    and market viability
                  </Text>
                  <Text size="sm" lh={1.6}>
                    <strong>3. Smart Procurement:</strong> I search suppliers, compare prices, and make 
                    purchasing decisions while tracking every unit and cost
                  </Text>
                  <Text size="sm" lh={1.6}>
                    <strong>4. Dynamic Pricing:</strong> Prices adjust based on demand, negotiation 
                    history, and profitability requirements
                  </Text>
                  <Text size="sm" lh={1.6}>
                    <strong>5. Continuous Learning:</strong> I take detailed notes on user preferences 
                    and use this data to improve future stocking decisions
                  </Text>
                </Stack>
                
                <Text size="sm" c="dimmed" mt="md" lh={1.6}>
                  The goal? Prove that AI can successfully run a profitable business by understanding 
                  customer needs, making smart financial decisions, and adapting to market demands—all 
                  while keeping the candy bowl stocked with treats people actually want.
                </Text>
              </Stack>
            </Card>

          </Stack>

          <Divider my="xl" />

          {/* Call to Action */}
          <Box ta="center">
            <Text size="lg" c="dimmed" mb="md">
              Impressed by what AI can create?
            </Text>
            <Text size="xl" fw={600} c="candy.7">
              Let's build something amazing together.
            </Text>
          </Box>
        </Stack>
      </Container>
    </Box>
  )
}

export default AboutPage