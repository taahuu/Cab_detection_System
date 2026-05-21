# 🚖 AI-Powered Cab Detection & Booking System

An intelligent cab booking and driver allocation system built using modern AI technologies including LangChain, LangGraph, OpenAI models, and location-based services.

This project automates the complete ride-booking workflow, from collecting pickup and destination details to calculating fare estimates, locating nearby drivers, assigning rides, and managing ride completion verification.

---

## 🌟 Features

### 📍 Smart Location Processing
- Detects and validates pickup locations
- Resolves destination addresses
- Calculates route distance automatically
- Supports GPS-based location inputs

### 🤖 AI Agent Workflow
- LangGraph-powered multi-agent architecture
- Intelligent ride booking flow
- Automated decision making between workflow nodes
- State management across ride lifecycle

### 🚕 Driver Detection & Allocation
- Finds nearby available drivers
- Distance-based driver ranking
- Automatic ride assignment
- Retry mechanism when no driver is available

### 💰 Fare Estimation Engine
- Distance-based fare calculation
- Dynamic pricing support
- Estimated ride cost generation

### 🔐 Ride Verification System
- Generates secure ride verification code
- Driver validates code before trip starts
- Prevents unauthorized ride initiation

### 💳 Payment Management
- Cash payment support
- UPI payment support
- Payment collection after ride completion

### 🎙️ Voice-Based Booking
- Voice-to-text ride booking
- Natural language ride requests
- Conversational AI experience

---

# 🏗️ System Architecture

```text
Customer Input
      │
      ▼
Pickup Location Agent
      │
      ▼
Destination Resolver Agent
      │
      ▼
Distance Calculation Agent
      │
      ▼
Fare Estimation Agent
      │
      ▼
Driver Search Agent
      │
      ▼
Driver Assignment Agent
      │
      ▼
Verification Code Generator
      │
      ▼
Ride Started
      │
      ▼
Ride Completed
      │
      ▼
Payment Collection
```

---

## 🛠️ Technology Stack

### AI & Agent Frameworks
- LangChain
- LangGraph
- OpenAI GPT Models

### Backend
- Python
- FastAPI

### Database
- PostgreSQL

### Location Services
- OpenStreetMap
- Nominatim API
- Geopy

### Voice Processing
- Speech Recognition
- Whisper API (Optional)

### Development Tools
- Git
- GitHub
- VS Code

---

## 📂 Project Structure

```text
Cab_detection_System/
│
├── agents/
│   ├── location_agent.py
│   ├── driver_agent.py
│   ├── fare_agent.py
│   └── verification_agent.py
│
├── graph/
│   └── graph.py
│
├── repository/
│   ├── db.py
│   └── models.py
│
├── services/
│   ├── location_service.py
│   ├── driver_service.py
│   └── payment_service.py
│
├── api/
│   └── routes.py
│
├── config/
│   └── settings.py
│
├── main.py
│
├── requirements.txt
│
└── README.md
```

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/taahuu/Cab_detection_System.git

cd Cab_detection_System
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key

DATABASE_URL=postgresql://username:password@localhost:5432/cabdb

MAP_API_KEY=your_map_api_key
```

---

## ▶️ Running The Project

```bash
python main.py
```

or

```bash
uvicorn main:app --reload
```

---

## 🔄 Workflow Example

### User Request

```text
Book a cab from Vijay Nagar to Airport
```

### AI Processing

1. Detect Pickup Location
2. Resolve Destination
3. Calculate Distance
4. Estimate Fare
5. Search Nearby Drivers
6. Assign Driver
7. Generate Verification Code
8. Start Ride
9. Complete Ride
10. Collect Payment

---

## 📊 Future Enhancements

- Live GPS tracking
- Dynamic surge pricing
- Ride history analytics
- Driver rating system
- Customer rating system
- Multi-language support
- Real-time traffic integration
- Advanced route optimization
- Mobile application integration

---

## 🚀 Use Cases

- Smart Cab Booking Platforms
- Ride-Hailing Applications
- Logistics & Delivery Services
- Fleet Management Systems
- AI-Powered Transportation Solutions

---

## 👨‍💻 Author

### Taha Ali

AI/ML Engineer | LangChain | LangGraph | RAG | OpenAI | Python | Computer Vision

GitHub:
https://github.com/taahuu

LinkedIn:
(Add your LinkedIn profile URL here)

---

## ⭐ Support

If you found this project useful:

⭐ Star the repository

🍴 Fork the repository

🛠️ Contribute improvements

📢 Share with the developer community

---

### Built with AI, Automation, and Modern Agentic Workflows 🚖🤖
