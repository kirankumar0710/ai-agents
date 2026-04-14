window.SAMPLES = window.SAMPLES || {};
window.SAMPLES['lg_trip'] = `🌍 Trip Planner Agent
==================================================
Type your travel request. Type 'quit' to exit.

You: Find flights from Delhi to Tokyo in June 2026

Agent: I'd be happy to help you find flights from Delhi to Tokyo in June 2026! However, I need a specific date to search for flights. June 2026 has many possible dates.

Could you please let me know:
- What specific date in June 2026 would you prefer to travel?

You: june 29th , 2026
  🔧 mock_search_flights({'origin': 'Delhi', 'destination': 'Tokyo', 'date': '2026-06-29'})

Agent: Great! I found several flight options from Delhi to Tokyo on June 29th, 2026:

**Available Flights:**

1. **Air India AI-307** - Direct Flight
   - Departure: 08:30 from Delhi
   - Arrival: 22:45 same day in Tokyo
   - Price: ₹45,000

2. **JAL JL-752** - Direct Flight
   - Departure: 14:20 from Delhi
   - Arrival: 05:30+1 (next day) in Tokyo
   - Price: ₹52,000

3. **IndiGo 6E-4521** - One Stop
   - Departure: 06:00 from Delhi
   - Arrival: 18:30 same day in Tokyo
   - Price: ₹38,000
   - 🔄 1 stop in Bangkok

Which flight would you prefer to book?

You: but you didn't ask me enter which fligh

Agent: You're absolutely right! I got ahead of myself.

**Which flight would you prefer?**
1. Air India AI-307 - ₹45,000 (Direct, 08:30-22:45)
2. JAL JL-752 - ₹52,000 (Direct, 14:20-05:30+1)
3. IndiGo 6E-4521 - ₹38,000 (1 stop, 06:00-18:30)

You: 3

Agent: Perfect! You've chosen the IndiGo 6E-4521 flight:
- June 29th, 2026 | 06:00 Delhi → 18:30 Tokyo | ₹38,000

To proceed with booking, I'll need your full name as it appears on your passport.

You: yes

Agent: I still need your actual full name to book the flight. "Yes" confirms you want to proceed, but I need your name exactly as it appears on your passport.

You: Kiran K Saravana

⏸️  BOOKING APPROVAL REQUIRED
-----------------------------------
  Action: mock_book_flight
  flight_id: 6E-4521
  passenger_name: Kiran K Saravana
-----------------------------------
Approve booking? (y/n): y
▶ Proceeding with booking...

  🔧 mock_book_flight({'flight_id': '6E-4521', 'passenger_name': 'Kiran K Saravana'})

Agent: ✅ Flight Successfully Booked!
- Flight: IndiGo 6E-4521 | Delhi → Tokyo (via Bangkok) | June 29, 2026
- Confirmation: TRP40296

Would you also like to search for hotels in Tokyo?

You: yes,  chec in date June 29th , 2026;  checkout date July 7th, 2026

Agent: What's your budget per night for the hotel? (in INR)

You: 10000/-
  🔧 mock_search_hotels({'city': 'Tokyo', 'check_in': '2026-06-29', 'check_out': '2026-07-07', 'budget_inr': 10000})

Agent: Available Hotels (June 29 - July 7, 2026):

1. **Shinjuku Granbell Hotel** - ₹8,500/night | 4★ | Near metro | Total: ₹68,000
2. **Dormy Inn Asakusa** - ₹6,200/night | 3★ | Onsen | Total: ₹49,600
3. **Citadines Shinjuku** - ₹11,000/night | 4★ | Serviced apt | Total: ₹88,000 (over budget)

Which hotel would you prefer?

You:  Shinjuku Granbell

⏸️  BOOKING APPROVAL REQUIRED
-----------------------------------
  Action: mock_book_hotel
  hotel_name: Shinjuku Granbell Hotel
  guest_name: Kiran K Saravana
  check_in: 2026-06-29
  check_out: 2026-07-07
-----------------------------------
Approve booking? (y/n): y
▶ Proceeding with booking...

  🔧 mock_book_hotel({'hotel_name': 'Shinjuku Granbell Hotel', 'guest_name': 'Kiran K Saravana', 'check_in': '2026-06-29', 'check_out': '2026-07-07'})

Agent: ✅ Complete Trip Booked!

🛫 FLIGHT:  IndiGo 6E-4521 | Delhi → Tokyo | June 29, 06:00-18:30 | ₹38,000 | Ref: TRP40296
🏨 HOTEL:   Shinjuku Granbell Hotel (4★) | June 29 - July 7, 2026 | 8 nights | ₹68,000 | Ref: HTL94063

💰 TOTAL TRIP COST: ₹1,06,000

Have a wonderful journey! 🎌

You: quit`;
