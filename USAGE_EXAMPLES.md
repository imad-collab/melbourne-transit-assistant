# Melbourne Transit Assistant - Usage Examples

## 🎯 Quick Start

### Starting the Bot
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token"
export PTV_DEV_ID="your_ptv_dev_id"
export PTV_API_KEY="your_ptv_api_key"
export HERE_API_KEY="your_here_api_key"
export OPENAI_API_KEY="your_openai_api_key"

# Run the bot
python -m src.telegram_bot
```

Bot is now listening for messages on Telegram!

---

## 📋 All Commands Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `/start` | Welcome message | `/start` |
| `/help` | Show all commands | `/help` |
| `/departures` | Check train/tram/bus schedule | `/departures 1181` |
| `/parking` | Find parking in configured areas | `/parking melbourne_cbd` |
| `/find_parking` | Find parking near any location | `/find_parking Flinders Street` |
| `/ask` | Ask about transit/parking | `/ask When is the next train to Frankston?` |
| `/analyze` | Analyze text | `/analyze The quick brown fox...` |
| `/validate` | Validate user input | `/validate Find parking nearby` |
| `/parking_areas` | List all parking areas | `/parking_areas` |

---

## 🚆 Transit Commands

### Example 1: Check Next Train Departures

**Command:**
```
/departures 1181
```

**Expected Output:**
```
🚆 Upcoming Departures from Flinders Street Station

📍 Stop: Flinders Street Station (ID: 1181)
🚂 Route Type: Train (0)
⏱️ Max Results: 5

🚂 Frankston Line
   ├─ 14:35 (Departing Now)
   ├─ 14:45 (In 10 mins)
   ├─ 14:55 (In 20 mins)
   ├─ 15:05 (In 30 mins)
   └─ 15:15 (In 45 mins)

ℹ️ Data from PTV (Public Transport Victoria)
🔄 Last updated: 2:25 PM
```

**Parameters:**
- `1181` = Flinders Street Station ID
- Optional: `[route_type]` - 0=trains, 1=trams, 2=buses, 3=coaches
- Optional: `[max_results]` - Number of departures to show (default 5)

### Example 2: Check Tram Schedule

**Command:**
```
/departures 1071 1
```

**Expected Output:**
```
🚆 Upcoming Departures from Bourke Street

📍 Stop: Bourke Street (ID: 1071)
🚊 Route Type: Tram (1)
⏱️ Max Results: 5

🚊 Route 3 (East Melbourne)
   ├─ 14:20 (Departing Now)
   ├─ 14:30 (In 10 mins)
   ├─ 14:40 (In 20 mins)
   └─ 14:50 (In 30 mins)

🚊 Route 15 (North Coburg)
   ├─ 14:25 (In 5 mins)
   ├─ 14:40 (In 20 mins)
   └─ 14:55 (In 35 mins)

ℹ️ Data from PTV (Public Transport Victoria)
🔄 Last updated: 2:25 PM
```

**Parameters:**
- `1071` = Bourke Street Stop ID
- `1` = Tram route type
- Max results default to 5

### Example 3: Bus Schedule

**Command:**
```
/departures 30392 2 3
```

**Expected Output:**
```
🚆 Upcoming Departures from Collins Street

📍 Stop: Collins Street (ID: 30392)
🚌 Route Type: Bus (2)
⏱️ Max Results: 3

🚌 Route 200 (City Loop)
   ├─ 14:15 (Departing Now)
   ├─ 14:35 (In 20 mins)
   └─ 14:55 (In 40 mins)

ℹ️ Data from PTV (Public Transport Victoria)
🔄 Last updated: 2:25 PM
```

---

## 🅿️ Parking Commands

### Example 1: Find Parking in Melbourne CBD

**Command:**
```
/parking melbourne_cbd
```

**Expected Output:**
```
🅿️ Parking Availability - Melbourne CBD

📍 Location: Melbourne CBD
⏰ Last Updated: 2:25 PM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏢 Collins Street Parking
   Total Spaces: 450 spaces
   Available: 127 spaces (28%)
   Vacancy Rate: ▓▓▓░░░░░░ 30%

🏢 Bourke Street Parking
   Total Spaces: 380 spaces
   Available: 89 spaces (23%)
   Vacancy Rate: ▓▓░░░░░░░ 20%

🏢 Lonsdale Street Parking
   Total Spaces: 520 spaces
   Available: 156 spaces (30%)
   Vacancy Rate: ▓▓▓░░░░░░ 30%

💡 Best Available: Lonsdale Street (30% vacancy)
```

### Example 2: Find Parking Near Location

**Command:**
```
/find_parking Southern Cross
```

**Expected Output:**
```
🅿️ Parking Near Southern Cross

📍 Location: Southern Cross Station, Melbourne CBD
🚗 Car Parking Only
📏 Distance Filter: < 1 km

🅿️ Spot 1: 📍 Collins Street Parking
   Distance: 0.2 km away
   Location: Collins St, Melbourne VIC 3000
   GPS: -37.8149, 144.9542
   🗺️ Get Directions: [Google Maps Button]

🅿️ Spot 2: 📍 Spencer Street Parking
   Distance: 0.4 km away
   Location: Spencer St, Melbourne VIC 3000
   GPS: -37.8201, 144.9511
   🗺️ Get Directions: [Google Maps Button]

🅿️ Spot 3: 📍 Lonsdale Street Parking
   Distance: 0.6 km away
   Location: Lonsdale St, Melbourne VIC 3000
   GPS: -37.8089, 144.9628
   🗺️ Get Directions: [Google Maps Button]

📊 Summary:
  Total Spots Found: 3
  Average Distance: 0.4 km
  All spots within 1 km radius
```

### Example 3: Find Parking (Ambiguous Location)

**Command:**
```
/find_parking Queen Victoria Market
```

**Expected Output:**
```
🅿️ Parking Near Queen Victoria Market

📍 Location: Queen Victoria Market, Melbourne CBD
🚗 Car Parking Only
📏 Distance Filter: < 1 km

ℹ️ NOTE: Resolved "Queen Victoria Market" to Melbourne CBD
(Rejected Sydney result - enforcing Victoria geographic bounds)

🅿️ Spot 1: 📍 Victoria Street Parking
   Distance: 0.1 km away
   Location: Victoria St, Melbourne VIC 3000
   GPS: -37.8065, 144.9612
   🗺️ Get Directions: [Google Maps Button]

🅿️ Spot 2: 📍 Peel Street Parking
   Distance: 0.3 km away
   Location: Peel St, Melbourne VIC 3000
   GPS: -37.8092, 144.9689
   🗺️ Get Directions: [Google Maps Button]

📊 Summary:
  Total Spots Found: 2
  Average Distance: 0.2 km
  All spots within 1 km radius
```

**Key Feature:** Bot automatically rejects Sydney results and returns Melbourne!

### Example 4: List All Parking Areas

**Command:**
```
/parking_areas
```

**Expected Output:**
```
📍 Available Parking Areas

1️⃣ Melbourne CBD
   Key: melbourne_cbd
   Location: -37.8136, 144.9631
   Usage: /parking melbourne_cbd

2️⃣ Geelong CBD
   Key: geelong_cbd
   Location: -38.1499, 144.3617
   Usage: /parking geelong_cbd

💡 Tip: Use /find_parking <location> to search any location!
```

---

## 🤖 AI Assistant Commands

### Example 1: Ask About Transit

**Command:**
```
/ask When is the next train to Frankston?
```

**Expected Output:**
```
🤖 AI Transit Assistant

Question: When is the next train to Frankston?

🔍 Understanding your question...

✅ Next Train to Frankston:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

From: Flinders Street Station
To: Frankston Station
Next Departure: 14:35 (Departing Now)
Following: 14:45 (In 10 mins)
Then: 14:55 (In 20 mins)

📊 Trip Duration: ~50 minutes
🚂 Route: Frankston Line (Direct)

💡 Tip: Use /departures 1181 to see more details
```

### Example 2: Ask About Parking

**Command:**
```
/ask Is there parking near Flinders Street?
```

**Expected Output:**
```
🤖 AI Transit Assistant

Question: Is there parking near Flinders Street?

🔍 Understanding your question...

✅ Parking Near Flinders Street:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Yes, there is available parking near Flinders Street!

🅿️ Nearest Parking Spots:
1. Collins Street Parking - 0.2 km away
2. Spencer Street Parking - 0.4 km away
3. Lonsdale Street Parking - 0.6 km away

📊 Average Availability: 25-30%
⏱️ Typical Wait Time: 5-10 minutes

🗺️ For detailed information, use:
   /find_parking Flinders Street
```

### Example 3: Ask General Question

**Command:**
```
/ask What are the main train lines in Melbourne?
```

**Expected Output:**
```
🤖 AI Transit Assistant

Question: What are the main train lines in Melbourne?

🔍 Understanding your question...

✅ Melbourne Train Lines:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Melbourne's metropolitan train network includes:

🚂 Metro Lines:
• Belgrave/Lilydale Line
• Glen Waverley Line
• Sandringham Line
• Dandenong Line
• Frankston Line
• Werribee/Williamstown Line
• Sunbury Line
• Craigieburn Line
• Upfield Line
• South Morang Line

📊 Total: 10 major metropolitan lines
🔗 Interchange Hub: Flinders Street Station

💡 Ask specific questions like:
   /ask When is the next train to [destination]?
```

---

## 📊 Text Analysis Commands

### Example 1: Analyze News Article

**Command:**
```
/analyze Climate change is increasingly affecting global weather patterns. Rising temperatures cause more extreme weather events. Sea levels are rising, threatening coastal communities. We must reduce carbon emissions immediately.
```

**Expected Output:**
```
📊 Text Analysis Results:

📌 Summary:
Climate change is driving more severe weather globally, with rising temperatures causing extreme events and sea level rise. Urgent action on carbon emissions is critical.

🔑 Key Points:
  • Climate change affects global weather patterns
  • Rising temperatures cause extreme weather events
  • Sea levels are rising
  • Threatening coastal communities
  • Need to reduce carbon emissions

😊 Sentiment: 😞 NEGATIVE
   (The text discusses serious concerns)

💭 Main Topics:
  - Climate change
  - Weather patterns
  - Rising temperatures
  - Sea level rise
  - Environmental action
```

### Example 2: Analyze Product Review

**Command:**
```
/analyze This product is amazing! The quality is excellent and it arrived quickly. Highly recommended!
```

**Expected Output:**
```
📊 Text Analysis Results:

📌 Summary:
A highly positive product review praising excellent quality and fast delivery.

🔑 Key Points:
  • Product quality is excellent
  • Fast delivery
  • Highly recommended
  • Overall satisfaction

😊 Sentiment: 😊 POSITIVE
   (Very enthusiastic and satisfied)

💭 Main Topics:
  - Product quality
  - Delivery speed
  - Recommendation
  - Customer satisfaction
```

### Example 3: Analyze Mixed Sentiment

**Command:**
```
/analyze The movie was okay. Some parts were interesting but it was too long. I'd watch it again but probably not immediately.
```

**Expected Output:**
```
📊 Text Analysis Results:

📌 Summary:
A mixed review of a movie that had some interesting moments but felt overly long, with moderate viewer interest in future viewing.

🔑 Key Points:
  • Movie had interesting parts
  • Movie was too long
  • Moderate satisfaction
  • May watch again

😊 Sentiment: 😐 NEUTRAL
   (Mixed feelings with both positive and negative points)

💭 Main Topics:
  - Movie quality
  - Pacing/length
  - Re-watch intent
  - Entertainment value
```

---

## ✅ Input Validation Commands

### Example 1: Validate Good Input

**Command:**
```
/validate Find parking near Flinders Street Station
```

**Expected Output:**
```
✅ Input Validation Results:

✅ Valid: True
✅ Safe: True
🎯 Confidence: 92.0%

📝 Assessment:
This is a clear, meaningful request about finding parking near a specific Melbourne location. The input is specific and actionable.

💡 Suggestions:
You could optionally mention your parking preferences (e.g., "Find covered parking" or "Find free parking"). This would help narrow down results.

✨ This input is ready to process!

💬 You can now use commands like:
  /find_parking - Find parking near locations
  /ask - Ask questions about it
  /departures - Check train/tram schedules
```

### Example 2: Validate Spam Input

**Command:**
```
/validate aaaa 12341234 xxxx
```

**Expected Output:**
```
✅ Input Validation Results:

❌ Valid: False
✅ Safe: True
🎯 Confidence: 88.5%

📝 Assessment:
This appears to be random text or gibberish. It doesn't contain meaningful content that the bot can process meaningfully.

💡 Suggestions:
Please provide a clear question or request related to:
  • Transit schedules and departures
  • Parking availability
  • Route information
  • Travel planning

Example format:
  "Find parking near [location]"
  "When is the next train to [destination]?"
  "Show me parking in [area]"

⚠️ This input may need refinement before processing.
```

### Example 3: Validate Vague Input

**Command:**
```
/validate parking
```

**Expected Output:**
```
✅ Input Validation Results:

✅ Valid: True
⚠️ Safe: True
🎯 Confidence: 75.0%

📝 Assessment:
While this is a valid word, it's quite vague. The bot can work with this, but more specific details would help produce better results.

💡 Suggestions:
Be more specific by adding:
  • Location: "parking near Flinders Street"
  • Action: "find parking" or "show parking"
  • Preferences: "covered parking" or "free parking"

Better format examples:
  /find_parking Flinders Street
  /parking melbourne_cbd
  /ask Is there parking nearby?

✨ This input is ready to process!

💬 With more specifics, results will be better!
```

### Example 4: Validate Unsafe Input

**Command:**
```
/validate I hate all [offensive term] people
```

**Expected Output:**
```
✅ Input Validation Results:

❌ Valid: True
⚠️ Safe: False
🎯 Confidence: 95.0%

📝 Assessment:
This input contains inappropriate and hateful language. The bot cannot process requests that include offensive content or hateful statements toward any group.

💡 Suggestions:
Please rephrase your request without offensive language. The bot is designed to help with:
  • Transit schedules
  • Parking availability
  • Travel information
  • Text analysis

Keep interactions respectful and constructive.

⚠️ This input may need refinement before processing.
```

---

## 🆘 Help and Info Commands

### Example 1: Get Help

**Command:**
```
/help
```

**Expected Output:**
```
Available commands:

🚆 Transit:
/departures <stop_id> [route_type] [max_results] - Upcoming departures

🅿️ Parking:
/parking [area_key] - Parking in configured areas (melbourne_cbd, geelong_cbd)
/find_parking <location> - Find parking near any location
/parking_areas - List all configured parking areas

🤖 AI Assistant:
/ask <question> - Ask about transit/parking
/analyze <text> - Analyze text (summary, sentiment, key points)
/validate <text> - Validate input (meaningfulness, safety, confidence)

ℹ️ Info:
/start - Welcome message
/help - This help

💡 Examples:
  /ask Where can I park near Southern Cross?
  /analyze Climate change is a serious global issue
  /validate Find parking near Flinders Street
```

### Example 2: Get Started

**Command:**
```
/start
```

**Expected Output:**
```
👋 Welcome to Melbourne Transit Assistant!

I can help you with:
  🚆 Check train/tram/bus schedules
  🅿️ Find parking near any location
  🤖 Ask questions about transit
  📊 Analyze text
  ✅ Validate your input

🚀 Quick Start:
  • /departures 1181 - Check next trains
  • /find_parking Flinders Street - Find parking
  • /ask When is the next train to Frankston?

📚 For more info, type /help

Let's get started! 🎉
```

---

## 🔍 Stop ID Reference

Common Melbourne stops for `/departures` command:

```
🚆 Train Stations:
  1181 = Flinders Street Station
  1036 = Southern Cross Station
  1028 = Parliament Station
  1000 = Melbourne Central Station
  1002 = Flagstaff Station

🚊 Tram Stops:
  1071 = Bourke Street
  1072 = Collins Street
  1073 = Elizabeth Street
  1074 = Swanston Street

🚌 Bus Stops:
  30392 = Collins Street
  30393 = Spencer Street
  30394 = La Trobe Street

💡 For your local area, visit:
   https://www.ptv.vic.gov.au/
```

---

## 📈 Advanced Usage Scenarios

### Scenario 1: Complete Journey Planning

**User wants to visit a friend at Southern Cross Station and park nearby**

```
Step 1: Ask about parking
/ask Is there parking near Southern Cross?

Step 2: Find specific parking location
/find_parking Southern Cross

Step 3: Check train schedule from current location
/departures 1181

Step 4: Plan entire trip
/ask How do I get from Flinders Street to Southern Cross?
```

### Scenario 2: Event Navigation

**User is going to an event at Queen Victoria Market**

```
Step 1: Validate your question
/validate I need parking near Queen Vic Market

Step 2: Find parking
/find_parking Queen Victoria Market

Step 3: Check tram schedule to venue
/departures 1071 1

Step 4: Plan return trip
/ask How do I get from Queen Vic Market back to Flinders Street?
```

### Scenario 3: Business Meeting Preparation

**User has meeting at Collins Street and needs information**

```
Step 1: Find parking
/parking melbourne_cbd

Step 2: Find specific nearby parking
/find_parking Collins Street

Step 3: Check transit options
/departures 1181

Step 4: Check weather/conditions
/analyze [news article about conditions]
```

---

## 💡 Tips & Tricks

### Tip 1: Use Natural Language
Instead of cryptic commands, use natural questions:
```
❌ Bad:  /departures 1181 0 5
✅ Good: /ask When is the next train to Frankston?
```

### Tip 2: Validate Unclear Inputs
If unsure about your phrasing, use `/validate` first:
```
/validate Find parking near here
✓ Gets feedback before running command
```

### Tip 3: Use Google Maps Buttons
All parking results include clickable Google Maps buttons:
```
Click the 🗺️ button to open navigation directly in Google Maps
One-tap to start directions!
```

### Tip 4: Analyze Text for Summaries
Got a long article? Analyze it:
```
/analyze [paste entire article]
✓ Get summary + key points + sentiment
```

### Tip 5: Use /help Frequently
Commands are organized by category:
```
/help
✓ See all 9 commands with descriptions
✓ Copy-paste examples from help
```

---

## 🐛 Troubleshooting

### Issue: "No API key configured"

**Solution:**
```bash
# Check your .env file
cat .env

# Should have:
TELEGRAM_BOT_TOKEN=...
PTV_DEV_ID=...
PTV_API_KEY=...
HERE_API_KEY=...
OPENAI_API_KEY=...
```

### Issue: Bot not responding

**Solution:**
```bash
# Check if bot is running
ps aux | grep telegram_bot

# Restart bot
python -m src.telegram_bot
```

### Issue: Wrong location returned

**Solution:**
- Use full location name: `/find_parking Flinders Street Station`
- Add "Melbourne": `/find_parking Collins Street Melbourne`
- The bot now has Melbourne CBD proximity bias

### Issue: Parking too far away

**Solution:**
- Results are filtered to < 1 km automatically
- If still too far, try more specific location
- Use nearby landmark: `/find_parking Southern Cross`

### Issue: No parking found

**Solution:**
- Try different location name
- Try nearby street name
- Use `/parking melbourne_cbd` for area summary
- Check if location is in Victoria (bot requires VIC)

---

## 📱 Mobile Usage

### Best Practices for Mobile Telegram:

1. **Use Command Suggestions**
   - Telegram shows available commands
   - Tap to auto-complete

2. **Copy Examples**
   - Long-press on commands from /help
   - Modify and send

3. **Save Favorite Stops**
   - Note stop IDs of frequent destinations
   - Quickly check departures

4. **Use Buttons**
   - Tap Google Maps buttons for navigation
   - Buttons open maps.google.com in browser

---

## 🎓 Learning Path

### Beginner
1. Start with `/start`
2. Try `/help` to see all commands
3. Test `/departures 1181` (simple command)
4. Try `/parking melbourne_cbd` (area parking)

### Intermediate
1. Use `/find_parking <location>` (location-based)
2. Ask `/ask` questions (natural language)
3. Validate input with `/validate`

### Advanced
1. Analyze complex texts with `/analyze`
2. Ask sophisticated questions with `/ask`
3. Combine multiple commands for journey planning
4. Validate before complex requests

---

## 📞 Support

For issues or feature requests:
- Check `/help` for all available commands
- Use `/validate` to test input quality
- Check USAGE_EXAMPLES.md (this file) for examples
- Review error messages carefully

---

**Last Updated:** November 2024
**Bot Version:** Production Ready
**Features:** 11/11 Complete
