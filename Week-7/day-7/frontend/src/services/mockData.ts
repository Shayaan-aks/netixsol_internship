export const propertiesData = [
  {
    id: 'prop_1',
    title: 'Luxury Villa in DHA Phase 6',
    price: 45000000, // 4.5 Crore
    location: 'DHA Phase 6, Lahore',
    beds: 5,
    baths: 6,
    area: '1 Kanal',
    type: 'House',
    status: 'Available',
    image: 'https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&q=80&w=800',
    description: 'Modern beautiful villa with swimming pool, smart home features, and premium imported fittings.'
  },
  {
    id: 'prop_2',
    title: 'Modern Apartment in Gulberg',
    price: 22000000,
    location: 'Gulberg III, Lahore',
    beds: 3,
    baths: 3,
    area: '1800 sq ft',
    type: 'Apartment',
    status: 'Available',
    image: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&q=80&w=800',
    description: 'Luxury high-rise apartment with panoramic city views, gym, and 24/7 security.'
  },
  {
    id: 'prop_3',
    title: 'Commercial Plaza Space',
    price: 85000000,
    location: 'Johar Town, Lahore',
    beds: 0,
    baths: 2,
    area: '10 Marla',
    type: 'Commercial',
    status: 'Sold',
    image: 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=800',
    description: 'Prime location commercial property, perfect for banks or retail brands.'
  },
  {
    id: 'prop_4',
    title: 'Cozy Family House',
    price: 18000000,
    location: 'Bahria Town, Lahore',
    beds: 4,
    baths: 4,
    area: '10 Marla',
    type: 'House',
    status: 'Available',
    image: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=800',
    description: 'Brand new construction in an active community with parks and schools nearby.'
  }
];

export const customersData = [
  {
    id: 'cust_1',
    name: 'Ali Raza',
    phone: '03001234567',
    email: 'ali.raza@example.com',
    leadScore: 85,
    status: 'Hot',
    budget: 50000000,
    preferences: ['DHA', 'House', '5 Beds'],
    lastInteraction: '2026-08-05T10:30:00'
  },
  {
    id: 'cust_2',
    name: 'Sara Khan',
    phone: '03219876543',
    email: 'sara.k@example.com',
    leadScore: 40,
    status: 'Cold',
    budget: 25000000,
    preferences: ['Gulberg', 'Apartment'],
    lastInteraction: '2026-08-01T14:15:00'
  }
];

export const appointmentsData = [
  {
    id: 'apt_1',
    customerName: 'Ali Raza',
    customerPhone: '03001234567',
    date: '2026-08-10',
    time: '14:00',
    propertyId: 'prop_1',
    status: 'Confirmed'
  },
  {
    id: 'apt_2',
    customerName: 'Ahmed Malik',
    customerPhone: '03334567890',
    date: '2026-08-11',
    time: '11:30',
    propertyId: 'prop_2',
    status: 'Pending'
  }
];

export const interactionsData = [
  {
    id: 'int_1',
    customerId: 'cust_1',
    type: 'Call',
    summary: 'Discussed budget and options in DHA Phase 6. Sent 3 property listings.',
    date: '2026-08-05T10:30:00'
  }
];
