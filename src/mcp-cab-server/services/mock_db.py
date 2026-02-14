MOCK_CAB_DB = {
    # ============== DELHI ROUTES ==============
    
    # Delhi Airport - High Traffic Routes
    ("igi airport", "connaught place"): [
        {"cab_type": "mini", "price": 450},
        {"cab_type": "sedan", "price": 650},
        {"cab_type": "suv", "price": 900},
    ],
    ("delhi airport", "connaught place"): [
        {"cab_type": "mini", "price": 450},
        {"cab_type": "sedan", "price": 650},
        {"cab_type": "suv", "price": 900},
    ],
    ("connaught place", "delhi airport"): [
        {"cab_type": "mini", "price": 450},
        {"cab_type": "sedan", "price": 650},
        {"cab_type": "suv", "price": 900},
    ],
    
    ("igi airport", "gurgaon"): [
        {"cab_type": "mini", "price": 600},
        {"cab_type": "sedan", "price": 850},
        {"cab_type": "suv", "price": 1200},
    ],
    ("delhi airport", "cyber city"): [
        {"cab_type": "mini", "price": 600},
        {"cab_type": "sedan", "price": 850},
        {"cab_type": "suv", "price": 1200},
    ],
    ("gurgaon", "delhi airport"): [
        {"cab_type": "mini", "price": 600},
        {"cab_type": "sedan", "price": 850},
        {"cab_type": "suv", "price": 1200},
    ],
    
    ("igi airport", "noida"): [
        {"cab_type": "mini", "price": 700},
        {"cab_type": "sedan", "price": 950},
        {"cab_type": "suv", "price": 1300},
    ],
    ("delhi airport", "noida sector 62"): [
        {"cab_type": "mini", "price": 700},
        {"cab_type": "sedan", "price": 950},
        {"cab_type": "suv", "price": 1300},
    ],
    ("noida", "delhi airport"): [
        {"cab_type": "mini", "price": 700},
        {"cab_type": "sedan", "price": 950},
        {"cab_type": "suv", "price": 1300},
    ],
    
    ("igi airport", "new delhi railway station"): [
        {"cab_type": "mini", "price": 500},
        {"cab_type": "sedan", "price": 700},
        {"cab_type": "suv", "price": 950},
    ],
    ("delhi airport", "railway station"): [
        {"cab_type": "mini", "price": 500},
        {"cab_type": "sedan", "price": 700},
        {"cab_type": "suv", "price": 950},
    ],
    
    # Delhi Railway Station Routes
    ("new delhi railway station", "connaught place"): [
        {"cab_type": "auto", "price": 150},
        {"cab_type": "mini", "price": 250},
        {"cab_type": "sedan", "price": 400},
    ],
    
    # Delhi Intra-city
    ("connaught place", "gurgaon"): [
        {"cab_type": "mini", "price": 500},
        {"cab_type": "sedan", "price": 700},
        {"cab_type": "suv", "price": 1000},
    ],
    ("delhi", "noida"): [
        {"cab_type": "mini", "price": 450},
        {"cab_type": "sedan", "price": 650},
        {"cab_type": "suv", "price": 900},
    ],
    ("delhi", "delhi"): [
        {"cab_type": "auto", "price": 180},
        {"cab_type": "mini", "price": 300},
        {"cab_type": "sedan", "price": 500},
    ],
    
    # ============== BANGALORE ROUTES ==============
    
    # Bangalore Airport - High Traffic Routes
    ("kempegowda airport", "electronic city"): [
        {"cab_type": "mini", "price": 800},
        {"cab_type": "sedan", "price": 1100},
        {"cab_type": "suv", "price": 1500},
    ],
    ("bangalore airport", "electronic city"): [
        {"cab_type": "mini", "price": 800},
        {"cab_type": "sedan", "price": 1100},
        {"cab_type": "suv", "price": 1500},
    ],
    ("electronic city", "bangalore airport"): [
        {"cab_type": "mini", "price": 800},
        {"cab_type": "sedan", "price": 1100},
        {"cab_type": "suv", "price": 1500},
    ],
    
    ("kempegowda airport", "whitefield"): [
        {"cab_type": "mini", "price": 650},
        {"cab_type": "sedan", "price": 900},
        {"cab_type": "suv", "price": 1250},
    ],
    ("bangalore airport", "itpl"): [
        {"cab_type": "mini", "price": 650},
        {"cab_type": "sedan", "price": 900},
        {"cab_type": "suv", "price": 1250},
    ],
    ("whitefield", "bangalore airport"): [
        {"cab_type": "mini", "price": 650},
        {"cab_type": "sedan", "price": 900},
        {"cab_type": "suv", "price": 1250},
    ],
    
    ("kempegowda airport", "koramangala"): [
        {"cab_type": "mini", "price": 750},
        {"cab_type": "sedan", "price": 1000},
        {"cab_type": "suv", "price": 1400},
    ],
    ("bangalore airport", "koramangala"): [
        {"cab_type": "mini", "price": 750},
        {"cab_type": "sedan", "price": 1000},
        {"cab_type": "suv", "price": 1400},
    ],
    ("koramangala", "bangalore airport"): [
        {"cab_type": "mini", "price": 750},
        {"cab_type": "sedan", "price": 1000},
        {"cab_type": "suv", "price": 1400},
    ],
    
    ("kempegowda airport", "mg road"): [
        {"cab_type": "mini", "price": 700},
        {"cab_type": "sedan", "price": 950},
        {"cab_type": "suv", "price": 1300},
    ],
    ("bangalore airport", "indiranagar"): [
        {"cab_type": "mini", "price": 700},
        {"cab_type": "sedan", "price": 950},
        {"cab_type": "suv", "price": 1300},
    ],
    
    # Bangalore Railway Station Routes
    ("bangalore city railway station", "electronic city"): [
        {"cab_type": "mini", "price": 500},
        {"cab_type": "sedan", "price": 700},
        {"cab_type": "suv", "price": 950},
    ],
    
    # Bangalore Intra-city
    ("electronic city", "whitefield"): [
        {"cab_type": "mini", "price": 600},
        {"cab_type": "sedan", "price": 850},
        {"cab_type": "suv", "price": 1150},
    ],
    ("koramangala", "indiranagar"): [
        {"cab_type": "auto", "price": 120},
        {"cab_type": "mini", "price": 250},
        {"cab_type": "sedan", "price": 400},
    ],
    ("bangalore", "bangalore"): [
        {"cab_type": "auto", "price": 150},
        {"cab_type": "mini", "price": 280},
        {"cab_type": "sedan", "price": 450},
    ],
    
    # ============== KOLKATA ROUTES ==============
    
    # Kolkata Airport - High Traffic Routes
    ("netaji subhas airport", "salt lake sector v"): [
        {"cab_type": "mini", "price": 350},
        {"cab_type": "sedan", "price": 500},
        {"cab_type": "suv", "price": 700},
    ],
    ("kolkata airport", "salt lake"): [
        {"cab_type": "mini", "price": 350},
        {"cab_type": "sedan", "price": 500},
        {"cab_type": "suv", "price": 700},
    ],
    ("salt lake", "kolkata airport"): [
        {"cab_type": "mini", "price": 350},
        {"cab_type": "sedan", "price": 500},
        {"cab_type": "suv", "price": 700},
    ],
    
    ("netaji subhas airport", "park street"): [
        {"cab_type": "mini", "price": 400},
        {"cab_type": "sedan", "price": 550},
        {"cab_type": "suv", "price": 750},
    ],
    ("kolkata airport", "park street"): [
        {"cab_type": "mini", "price": 400},
        {"cab_type": "sedan", "price": 550},
        {"cab_type": "suv", "price": 750},
    ],
    ("park street", "kolkata airport"): [
        {"cab_type": "mini", "price": 400},
        {"cab_type": "sedan", "price": 550},
        {"cab_type": "suv", "price": 750},
    ],
    
    ("kolkata airport", "howrah station"): [
        {"cab_type": "mini", "price": 450},
        {"cab_type": "sedan", "price": 600},
        {"cab_type": "suv", "price": 800},
    ],
    ("howrah station", "kolkata airport"): [
        {"cab_type": "mini", "price": 450},
        {"cab_type": "sedan", "price": 600},
        {"cab_type": "suv", "price": 800},
    ],
    
    # Kolkata Railway Station Routes
    ("howrah station", "salt lake"): [
        {"cab_type": "mini", "price": 350},
        {"cab_type": "sedan", "price": 500},
        {"cab_type": "suv", "price": 700},
    ],
    ("sealdah station", "park street"): [
        {"cab_type": "auto", "price": 120},
        {"cab_type": "mini", "price": 250},
        {"cab_type": "sedan", "price": 400},
    ],
    
    # Kolkata Intra-city
    ("salt lake", "park street"): [
        {"cab_type": "mini", "price": 300},
        {"cab_type": "sedan", "price": 450},
        {"cab_type": "suv", "price": 650},
    ],
    ("kolkata", "kolkata"): [
        {"cab_type": "auto", "price": 130},
        {"cab_type": "mini", "price": 250},
        {"cab_type": "sedan", "price": 400},
    ],
    
    # ============== HYDERABAD ROUTES ==============
    
    # Hyderabad Airport - High Traffic Routes
    ("rajiv gandhi airport", "hitec city"): [
        {"cab_type": "mini", "price": 650},
        {"cab_type": "sedan", "price": 900},
        {"cab_type": "suv", "price": 1250},
    ],
    ("hyderabad airport", "gachibowli"): [
        {"cab_type": "mini", "price": 650},
        {"cab_type": "sedan", "price": 900},
        {"cab_type": "suv", "price": 1250},
    ],
    ("hitec city", "hyderabad airport"): [
        {"cab_type": "mini", "price": 650},
        {"cab_type": "sedan", "price": 900},
        {"cab_type": "suv", "price": 1250},
    ],
    ("gachibowli", "hyderabad airport"): [
        {"cab_type": "mini", "price": 650},
        {"cab_type": "sedan", "price": 900},
        {"cab_type": "suv", "price": 1250},
    ],
    
    ("rajiv gandhi airport", "banjara hills"): [
        {"cab_type": "mini", "price": 600},
        {"cab_type": "sedan", "price": 850},
        {"cab_type": "suv", "price": 1200},
    ],
    ("hyderabad airport", "banjara hills"): [
        {"cab_type": "mini", "price": 600},
        {"cab_type": "sedan", "price": 850},
        {"cab_type": "suv", "price": 1200},
    ],
    ("banjara hills", "hyderabad airport"): [
        {"cab_type": "mini", "price": 600},
        {"cab_type": "sedan", "price": 850},
        {"cab_type": "suv", "price": 1200},
    ],
    
    ("rajiv gandhi airport", "secunderabad station"): [
        {"cab_type": "mini", "price": 550},
        {"cab_type": "sedan", "price": 800},
        {"cab_type": "suv", "price": 1100},
    ],
    ("hyderabad airport", "secunderabad"): [
        {"cab_type": "mini", "price": 550},
        {"cab_type": "sedan", "price": 800},
        {"cab_type": "suv", "price": 1100},
    ],
    
    ("rajiv gandhi airport", "madhapur"): [
        {"cab_type": "mini", "price": 650},
        {"cab_type": "sedan", "price": 900},
        {"cab_type": "suv", "price": 1250},
    ],
    ("hyderabad airport", "madhapur"): [
        {"cab_type": "mini", "price": 650},
        {"cab_type": "sedan", "price": 900},
        {"cab_type": "suv", "price": 1250},
    ],
    
    # Hyderabad Railway Station Routes
    ("secunderabad station", "hitec city"): [
        {"cab_type": "mini", "price": 400},
        {"cab_type": "sedan", "price": 600},
        {"cab_type": "suv", "price": 850},
    ],
    ("secunderabad", "gachibowli"): [
        {"cab_type": "mini", "price": 400},
        {"cab_type": "sedan", "price": 600},
        {"cab_type": "suv", "price": 850},
    ],
    
    # Hyderabad Intra-city
    ("hitec city", "kukatpally"): [
        {"cab_type": "mini", "price": 350},
        {"cab_type": "sedan", "price": 500},
        {"cab_type": "suv", "price": 700},
    ],
    ("banjara hills", "hitec city"): [
        {"cab_type": "mini", "price": 300},
        {"cab_type": "sedan", "price": 450},
        {"cab_type": "suv", "price": 650},
    ],
    ("hyderabad", "hyderabad"): [
        {"cab_type": "auto", "price": 140},
        {"cab_type": "mini", "price": 270},
        {"cab_type": "sedan", "price": 450},
    ],
    
    # ============== INTER-CITY ROUTES ==============
    
    ("delhi", "jaipur"): [
        {"cab_type": "sedan", "price": 3500},
        {"cab_type": "suv", "price": 4500},
        {"cab_type": "prime sedan", "price": 5000},
    ],
    ("jaipur", "delhi"): [
        {"cab_type": "sedan", "price": 3500},
        {"cab_type": "suv", "price": 4500},
        {"cab_type": "prime sedan", "price": 5000},
    ],
    
    ("delhi", "agra"): [
        {"cab_type": "sedan", "price": 3000},
        {"cab_type": "suv", "price": 4000},
        {"cab_type": "prime sedan", "price": 4500},
    ],
    ("agra", "delhi"): [
        {"cab_type": "sedan", "price": 3000},
        {"cab_type": "suv", "price": 4000},
        {"cab_type": "prime sedan", "price": 4500},
    ],
    
    ("bangalore", "mysore"): [
        {"cab_type": "sedan", "price": 2200},
        {"cab_type": "suv", "price": 3000},
        {"cab_type": "prime sedan", "price": 3500},
    ],
    ("mysore", "bangalore"): [
        {"cab_type": "sedan", "price": 2200},
        {"cab_type": "suv", "price": 3000},
        {"cab_type": "prime sedan", "price": 3500},
    ],
    
    ("hyderabad", "vijayawada"): [
        {"cab_type": "sedan", "price": 3200},
        {"cab_type": "suv", "price": 4200},
        {"cab_type": "prime sedan", "price": 4800},
    ],
    ("vijayawada", "hyderabad"): [
        {"cab_type": "sedan", "price": 3200},
        {"cab_type": "suv", "price": 4200},
        {"cab_type": "prime sedan", "price": 4800},
    ],
    
    # ============== GENERIC FALLBACK ROUTES ==============
    
    ("airport", "city"): [
        {"cab_type": "mini", "price": 500},
        {"cab_type": "sedan", "price": 700},
        {"cab_type": "suv", "price": 1000},
    ],
    
    ("airport", "railway station"): [
        {"cab_type": "mini", "price": 450},
        {"cab_type": "sedan", "price": 650},
        {"cab_type": "suv", "price": 900},
    ],
    
    ("airport", "hotel"): [
        {"cab_type": "mini", "price": 400},
        {"cab_type": "sedan", "price": 550},
        {"cab_type": "suv", "price": 800},
    ],
    
    ("railway station", "hotel"): [
        {"cab_type": "auto", "price": 180},
        {"cab_type": "mini", "price": 300},
        {"cab_type": "sedan", "price": 450},
    ],
}