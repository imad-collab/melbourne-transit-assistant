# 🤖 Melbourne Transit Assistant - Telegram Commands Guide

## Complete List of Available Commands

Your Telegram bot is now **ONLINE** and ready to use! Here are all the commands you can perform:

---

## 🚆 **TRANSIT COMMANDS**

### `/start`
**What it does:** Welcome message with introduction to the bot
```
Example: /start
Response: Welcome message explaining what the bot can do
```

---

### `/help`
**What it does:** Shows list of all available commands with descriptions
```
Example: /help
Response: Displays all 10 commands with usage examples
```

---

### `/departures <stop_id> [route_type] [max_results]`
**What it does:** Get real upcoming transit departures from Melbourne stations

**Parameters:**
- `<stop_id>` - Melbourne station ID (required)
- `[route_type]` - Optional: 0=Tram, 1=Train, 2=Bus, 3=V/Line (default: all)
- `[max_results]` - Optional: Number of departures to show (default: 5)

**Examples:**
```
/departures 1071
  → Shows next 5 departures from Southern Cross Station

/departures 1071 1
  → Shows next 5 train departures only

/departures 1071 1 10
  → Shows next 10 train departures

/departures 1049 0
  → Shows next 5 tram departures from Flinders Street
```

**Common Station IDs:**
- 1071 = Southern Cross Station
- 1049 = Flinders Street Station
- 1181 = Melbourne Central Station
- 1256 = Parliament Station
- 1105 = Flagstaff Station

**Common Route Types:**
- 0 = Tram
- 1 = Train
- 2 = Bus
- 3 = V/Line

---

## 🅿️ **PARKING COMMANDS**

### `/parking [area_key]`
**What it does:** Find parking in pre-configured Melbourne areas

**Available Areas:**
- `melbourne_cbd` - Melbourne CBD parking
- `geelong_cbd` - Geelong CBD parking
- `easypark_spencer` - EasyPark Spencer Street
- `easypark_flinders` - EasyPark Flinders Street
- `easypark_collins` - EasyPark Collins Street

**Examples:**
```
/parking
  → Shows all parking areas configured

/parking melbourne_cbd
  → Shows parking near Melbourne CBD

/parking easypark_spencer
  → Shows parking near Spencer Street Station
```

---

### `/find_parking <location>`
**What it does:** Find parking near ANY location in Melbourne

**Parameters:**
- `<location>` - Any Melbourne address, landmark, or station name

**Examples:**
```
/find_parking Southern Cross Station
  → Finds parking within 1km of Southern Cross Station
  ✓ Returns: Up to 10 nearby parking spots
  ✓ Shows: Name, distance, coordinates, directions button

/find_parking Flinders Street
  → Finds parking near Flinders Street

/find_parking Queen Victoria Market
  → Finds parking near Queen Vic Market

/find_parking 138 Spencer St Melbourne
  → Finds parking near specific address

/find_parking Melbourne Central
  → Finds parking near Melbourne Central Station
```

**Response includes:**
- 🅿️ Parking facility name
- 📏 Distance from location
- 📍 GPS coordinates
- 🗺️ Google Maps navigation button

---

### `/bays [location]` ⭐ **NEW FEATURE**
**What it does:** Show parking BAY occupancy status (like Parkbuddy!)

**Features:**
- 🟢 Green = Free/Unoccupied bay
- 🔴 Red = Occupied bay
- ⚪ Gray = Unknown status
- 📊 Occupancy statistics
- 🗺️ Individual navigation buttons for each bay

**Examples:**
```
/bays
  → Shows bay occupancy for Southern Cross (default)

/bays Southern Cross Station
  → Shows bay occupancy near Southern Cross

/bays Flinders Street
  → Shows bay occupancy near Flinders Street

/bays Spencer Street
  → Shows bay occupancy near Spencer Street
```

**Response includes:**
- Bay number and status (Free/Occupied)
- GPS coordinates for each bay
- Distance from search location
- Overall occupancy rate (e.g., "83.3% occupied")
- Availability forecast
- Navigation button for each bay

---

### `/parking_areas`
**What it does:** List all pre-configured parking areas

**Example:**
```
/parking_areas
  → Shows: Melbourne CBD, Geelong CBD, EasyPark locations
  → Displays: Coordinates and search radius for each
```

---

## 🤖 **AI ASSISTANT COMMANDS**

### `/ask <question>`
**What it does:** Ask AI questions about transit, parking, or Melbourne

**Examples:**
```
/ask Where can I park near Southern Cross?
  → AI response with parking suggestions

/ask What's the best way to get to Melbourne Central?
  → AI response about transit options

/ask How many buses go to Queen Victoria Market?
  → AI response about available routes

/ask Tell me about parking in Melbourne CBD
  → AI explains parking options
```

**What it can answer:**
- ✓ Transit route questions
- ✓ Parking location questions
- ✓ Travel directions
- ✓ Melbourne landmark information
- ✓ General travel advice

---

### `/analyze <text>` 📊 **AI TEXT ANALYSIS**
**What it does:** Analyze any text with AI (sentiment, summary, key points)

**Examples:**
```
/analyze Climate change is a serious global issue that needs immediate action
  → AI analyzes: Sentiment (concern), Key topics, Summary

/analyze I love visiting Melbourne! The weather is great and the coffee is amazing.
  → AI analyzes: Positive sentiment, Key points, Summary

/analyze The public transport system is unreliable and frustrating.
  → AI analyzes: Negative sentiment, Issues identified, Suggestions
```

**Analysis includes:**
- **Sentiment Analysis**: Positive/Negative/Neutral
- **Key Points**: Main topics identified
- **Summary**: Concise summary of text
- **Confidence Score**: How confident the AI is
- **Tone**: Formal/Casual/Urgent/etc.

---

### `/validate <text>` ✅ **INPUT VALIDATION**
**What it does:** Validate user input with AI confidence scoring

**Parameters:**
- `<text>` - Any text to validate

**Examples:**
```
/validate Find parking near Flinders Street
  → Validates: Meaningful? Safe? Confidence level?

/validate Hello world random text xyz
  → AI determines: Not meaningful for bot tasks

/validate Show me transit departures from Southern Cross
  → AI validates: Good input, high confidence (95%+)
```

**Validation checks:**
- ✓ Is the input meaningful?
- ✓ Is it safe (no malicious content)?
- ✓ Does it relate to transit/parking?
- ✓ Confidence percentage (0-100%)
- ✓ Suggested improvements

---

## 📱 **INTERACTIVE FEATURES**

### Navigation Buttons 🗺️
All parking results include **clickable Google Maps buttons**:
- Click any parking spot button
- Opens Google Maps with:
  - Your current location (origin)
  - Parking spot (destination)
  - Driving directions
  - Estimated time & distance

### Bay Navigation 🅿️
Each parking bay includes:
- Individual "Navigate" button
- Takes you to that specific bay
- Real-time directions with current location

---

## 💡 **QUICK START EXAMPLES**

### Example 1: Finding Parking Near Southern Cross
```
User: /find_parking Southern Cross Station
Bot Response:
  🅿️ PARKING NEAR SOUTHERN CROSS STATION
  
  1. Wilson Parking - 150m away
     📍 (-37.8174, 144.9537)
     🗺️ [Navigate] button
  
  2. EasyPark Spencer Street - 200m away
     📍 (-37.8183, 144.9549)
     🗺️ [Navigate] button
```

### Example 2: Checking Bay Availability
```
User: /bays Spencer Street
Bot Response:
  🅿️ FREE PARKING BAYS - Spencer Street
  
  ✅ Found 2 free bays
  
  1. 🟢 Bay 1
     Status: Unoccupied
     📍 (-37.8183, 144.9549)
     🗺️ [Navigate]
  
  📊 Occupancy: 66.7%
```

### Example 3: Getting Transit Departures
```
User: /departures 1071 1 5
Bot Response:
  🚂 DEPARTURES FROM SOUTHERN CROSS STATION
  
  1. Platform 1 → Flinders Street
     Departs: In 5 minutes
```

---

## ⚙️ **QUICK START**

**Try these commands in order:**

1. `/start` - Get introduction
2. `/help` - See all commands
3. `/departures 1071` - Get real transit data
4. `/find_parking Southern Cross Station` - Find parking
5. `/bays Spencer Street` - See bay occupancy
6. `/ask Where can I park?` - Ask AI

---

## 🎯 **ALL 10 COMMANDS AVAILABLE**

| # | Command | Purpose |
|---|---------|---------|
| 1️⃣ | `/start` | Welcome message |
| 2️⃣ | `/help` | List all commands |
| 3️⃣ | `/departures` | Transit departures |
| 4️⃣ | `/parking` | Configured areas |
| 5️⃣ | `/find_parking` | Find parking anywhere |
| 6️⃣ | `/bays` | Bay occupancy |
| 7️⃣ | `/parking_areas` | Show all areas |
| 8️⃣ | `/ask` | AI questions |
| 9️⃣ | `/analyze` | Text analysis |
| 🔟 | `/validate` | Input validation |

---

## 🚀 **BOT IS NOW LIVE!**

**Your Melbourne Transit Assistant is online and ready to use.**

- ✅ Connected to Telegram
- ✅ Listening for commands
- ✅ All 10 features operational
- ✅ Real-time data from APIs
- ✅ AI-powered responses

**Send any command above to start!**

---

Happy traveling! 🚆🅿️🤖
