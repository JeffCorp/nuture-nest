# Pregnancy AI Agent

A multi-agent AI system built with Google's Agent Development Kit (ADK) that provides comprehensive pregnancy care support through specialized agents for user onboarding, symptom triage with automatic urgent escalation, and proactive health coaching.

## Problem

Pregnant women need accessible, reliable health guidance and urgent care support, but existing solutions often:

- Lack specialized pregnancy-focused medical information
- Don't provide immediate escalation for urgent symptoms
- Fail to maintain calm, reassuring communication during emergencies
- Don't integrate with healthcare providers and family members
- Expose technical medical details that can cause unnecessary anxiety

## Solution

This system addresses these challenges through a **hierarchical multi-agent architecture** that:

1. **Onboards users securely** with email verification and profile management
2. **Assesses symptoms** using a specialized severity checker (1-6 scale)
3. **Automatically escalates urgent cases** (severity > 4) to both doctor and partner via email
4. **Provides calm, filtered guidance** - users never see technical severity scores
5. **Offers proactive care** with evidence-based preventive guidance
6. **Searches real-time medical information** via Brave Search for current guidelines

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│         Root Agent (PregnancyAssistant)                  │
│         Orchestrator & Query Router                      │
└─────────────────────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
┌──────────┐  ┌──────────────┐  ┌──────────┐
│Introducer│  │SymptomTriage │  │Proactive │
│  Agent   │  │    Agent     │  │  Coach   │
└──────────┘  └──────────────┘  └──────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ CommunicationAgent   │
         │   (SequentialAgent)  │
         └──────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Severity │  │Escalator │  │First Aid │
│ Checker  │  │  Agent   │  │  Agent   │
└──────────┘  └──────────┘  └──────────┘
```

### Agent Responsibilities

| Agent                    | Purpose            | Key Features                            |
| ------------------------ | ------------------ | --------------------------------------- |
| **Root Agent**           | Main orchestrator  | Routes queries, coordinates agents      |
| **IntroducerAgent**      | User onboarding    | Email verification, profile management  |
| **SymptomTriageAgent**   | Symptom assessment | Medical search, severity evaluation     |
| **SeverityCheckerAgent** | Severity scoring   | 1-6 scale assessment (5-6 = urgent)     |
| **EscalatorAgent**       | Urgent escalation  | Auto-emails doctor & partner            |
| **FirstAidAgent**        | Emergency guidance | Calm, reassuring first aid instructions |
| **ProactiveCoachAgent**  | Preventive care    | Evidence-based wellness guidance        |

### Key Flows

#### 1. User Onboarding Flow

```
User → Root Agent → IntroducerAgent
    → Request Email → Send 6-digit Code
    → Verify Code → Check Database
    → [New] Collect Details → Save
    → [Existing] Retrieve Profile
```

#### 2. Urgent Symptom Escalation Flow

```
User: "I have severe bleeding"
    ↓
Root Agent → SymptomTriageAgent
    ↓
CommunicationAgent (Sequential)
    ├─→ SeverityCheckerAgent → Score: 6 (URGENT)
    ├─→ EscalatorAgent
    │   ├─→ Get user details (doctor/partner emails)
    │   └─→ Send urgent alert email
    └─→ FirstAidAgent → Calm guidance
    ↓
User receives: Reassuring guidance (NO severity score shown)
Doctor & Partner receive: Urgent alert email with details
```

## Setup Instructions

### Prerequisites

- Python 3.13+
- Gmail account with App Password
- Brave Search API key (optional, for web search)
- Google ADK access

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/JeffCorp/nuture-nest.git
   cd nuture-nest
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create `config/.env` file:

   ```env
   # Gmail Configuration
   GMAIL_EMAIL=your-email@gmail.com
   GMAIL_APP_PASSWORD=your-16-character-app-password

   # Brave Search API (optional)
   BRAVE_API_KEY=your-brave-api-key
   ```

   **To get Gmail App Password:**

   1. Go to Google Account → Security
   2. Enable 2-Step Verification
   3. Generate App Password for "Mail"
   4. Use the 16-character password

5. **Initialize databases**

   Databases are created automatically on first run:

   - `db/user_details.db` - User profiles and authentication
   - `db/memory.db` - Session storage

### Running the Application

**Option 1: Using main.py**

```bash
python main.py
```

**Option 2: Using root_agent.py directly**

```python
from agents.root_agent import root_runner
from utils import Utils
import asyncio

async def main():
    await Utils.run_session(
        root_runner,
        user_queries="Hello, I'm 28 weeks pregnant",
        session_name="test_session"
    )

asyncio.run(main())
```

## Usage Examples

### Example 1: New User Onboarding

```
User: "Hi, I'm new here"
→ IntroducerAgent requests email
→ Sends verification code
→ User provides code
→ Collects: name, pregnancy details, partner info, doctor info
→ Saves to database
```

### Example 2: Symptom Assessment (Normal)

```
User: "I have mild headaches"
→ SymptomTriageAgent searches medical info
→ SeverityCheckerAgent: Score 2 (Low)
→ FirstAidAgent provides guidance
→ User receives: Reassuring advice (no severity score)
```

### Example 3: Urgent Symptom (Automatic Escalation)

```
User: "I'm bleeding heavily"
→ SeverityCheckerAgent: Score 6 (URGENT)
→ EscalatorAgent:
   - Retrieves doctor & partner emails
   - Sends urgent alert email
   - Returns: "Email sent successfully"
→ FirstAidAgent: Calm first aid guidance
→ User receives: Reassuring guidance (NO technical details)
→ Doctor & Partner receive: Urgent alert email
```

## Project Structure

```
pregnancy-ai-agent/
├── agents/                  # AI agents
│   ├── root_agent.py       # Main orchestrator
│   ├── introducer.py       # User onboarding
│   ├── symptom_triage.py   # Symptom assessment
│   ├── severity_checker.py # Severity evaluation
│   ├── escalator.py        # Urgent escalation
│   ├── first_aid.py        # First aid guidance
│   └── proactive_coach.py  # Preventive care
├── tools/                   # Function tools
│   ├── introducer.py       # Database operations
│   └── email_tool.py       # Email functionality
├── utils/                   # Utilities
│   └── index.py            # Session management
├── db/                      # SQLite databases
│   ├── user_details.db     # User data
│   └── memory.db           # Session storage
├── config/                  # Configuration
│   └── .env                # Environment variables
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Key Features

### 🔒 Security & Privacy

- Email verification with 6-digit codes
- SQL injection protection (parameterized queries)
- Case-insensitive email matching
- Session isolation

### 🚨 Urgent Case Handling

- Automatic escalation for severity > 4
- Multi-recipient alerts (doctor + partner)
- **Critical**: Severity scores never exposed to users
- Calm, reassuring communication

### 🤖 Agent Communication

- State-based data passing (`output_key` pattern)
- Sequential processing for proper order
- Response filtering removes technical details

### 🔍 Medical Information

- Real-time web search via Brave Search
- Context-aware (pregnancy stage + symptoms)
- Evidence-based guidance

## Technology Stack

- **Framework**: Google ADK v1.18.0
- **LLM**: Google Gemini (2.0/2.5-flash-lite)
- **Database**: SQLite
- **Email**: Gmail SMTP
- **Search**: Brave Search (MCP)
- **Language**: Python 3.13

## Configuration

### Environment Variables

Required in `config/.env`:

- `GMAIL_EMAIL`: Your Gmail address
- `GMAIL_APP_PASSWORD`: 16-character app password
- `BRAVE_API_KEY`: (Optional) Brave Search API key

### Database Schema

**user_details table:**

- user_id, name, email, pregnancy_details, partner_details, doctor_details

**user_authentication table:**

- email, code (verification codes, deleted after use)

## Error Handling

- **Retry Logic**: 5 attempts with exponential backoff
- **Graceful Degradation**: Continues if email/search unavailable
- **User-Friendly Messages**: Clear error communication

## Testing

Run test scenarios:

```bash
python tests/test_scenarios.py
```

## Limitations

- Requires Gmail account for email functionality
- Brave Search API key needed for web search (optional)
- ADK doesn't support proactive messaging (workaround: append to next user message)

## Future Enhancements

- Calendar integration for appointments
- Multi-language support
- Analytics and performance tracking
- Follow-up questions after urgent symptoms
- Voice integrations for easier interaction
- Trimester specific check-ins with symptoms and possible anticipated bodily changes

## License

MIT

## Contacts

jeffukus@gmail.com
olaniyidan14@gmail.com
moyosoreabiodunn@gmail.com

---

**Built with Google Agent Development Kit (ADK)**
