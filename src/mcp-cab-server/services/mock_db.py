MOCK_CAB_DB = {
    # Airport routes - various naming patterns
    ("mumbai airport", "mumbai central"): [
        {
            "cab_type": "mini",
            "price": 350,
        },
        {
            "cab_type": "sedan",
            "price": 500,
        },
        {
            "cab_type": "suv",
            "price": 700,
        },
    ],
    
    ("airport", "mumbai"): [
        {
            "cab_type": "mini",
            "price": 350,
        },
        {
            "cab_type": "sedan",
            "price": 500,
        },
        {
            "cab_type": "suv",
            "price": 700,
        },
    ],
    
    # Inter-city routes
    ("mumbai", "pune"): [
        {
            "cab_type": "hatchback",
            "price": 1000,
        },
        {
            "cab_type": "sedan",
            "price": 1500,
        },
        {
            "cab_type": "suv",
            "price": 2000,
        },
        {
            "cab_type": "prime sedan",
            "price": 2500,
        },
    ],
    
    ("mumbai central", "pune railway station"): [
        {
            "cab_type": "sedan",
            "price": 1600,
        },
        {
            "cab_type": "suv",
            "price": 2100,
        },
    ],
    
    ("pune", "mumbai"): [
        {
            "cab_type": "hatchback",
            "price": 1000,
        },
        {
            "cab_type": "sedan",
            "price": 1500,
        },
        {
            "cab_type": "suv",
            "price": 2000,
        },
    ],
    
    # Temple routes
    ("siddhivinayak temple", "mumbai airport"): [
        {
            "cab_type": "mini",
            "price": 400,
        },
        {
            "cab_type": "sedan",
            "price": 550,
        },
    ],
    
    ("temple", "airport"): [
        {
            "cab_type": "mini",
            "price": 400,
        },
        {
            "cab_type": "sedan",
            "price": 550,
        },
    ],
    
    # Local routes within Mumbai
    ("mumbai central", "siddhivinayak temple"): [
        {
            "cab_type": "auto",
            "price": 150,
        },
        {
            "cab_type": "mini",
            "price": 250,
        },
    ],
    
    ("gateway india", "mumbai airport"): [
        {
            "cab_type": "mini",
            "price": 450,
        },
        {
            "cab_type": "sedan",
            "price": 600,
        },
        {
            "cab_type": "suv",
            "price": 800,
        },
    ],
    
    # Railway station routes
    ("railway station", "hotel"): [
        {
            "cab_type": "auto",
            "price": 180,
        },
        {
            "cab_type": "mini",
            "price": 300,
        },
    ],
    
    ("station", "airport"): [
        {
            "cab_type": "mini",
            "price": 350,
        },
        {
            "cab_type": "sedan",
            "price": 500,
        },
    ],
    
    # Generic patterns for common places
    ("airport", "office"): [
        {
            "cab_type": "mini",
            "price": 350,
        },
        {
            "cab_type": "sedan",
            "price": 500,
        },
    ],
    
    ("hotel", "airport"): [
        {
            "cab_type": "mini",
            "price": 400,
        },
        {
            "cab_type": "sedan",
            "price": 550,
        },
    ],
    
    # Intra-city Mumbai routes (catch-all for within city)
    ("mumbai", "mumbai"): [
        {
            "cab_type": "auto",
            "price": 150,
        },
        {
            "cab_type": "mini",
            "price": 250,
        },
        {
            "cab_type": "sedan",
            "price": 400,
        },
    ],
    
    # Intra-city Pune routes
    ("pune", "pune"): [
        {
            "cab_type": "auto",
            "price": 120,
        },
        {
            "cab_type": "mini",
            "price": 200,
        },
        {
            "cab_type": "sedan",
            "price": 350,
        },
    ],
}