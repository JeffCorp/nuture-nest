# Pregnancy AI Agent - Project Documentation

## Overview

The Pregnancy AI Agent is a multi-agent system built using Google's Agent Development Kit (ADK) that provides comprehensive pregnancy care support. The system uses specialized AI agents to handle user onboarding, symptom triage, urgent case escalation, and proactive health coaching.

**Technology Stack**: Google ADK v1.18.0, Gemini LLM (2.0/2.5-flash-lite), SQLite, Gmail SMTP, Brave Search (MCP), Python 3.13

---

## Architecture

### High-Level Architecture

```
Root Agent (PregnancyAssistant)
    ├── IntroducerAgent (User Onboarding)
    ├── SymptomTriageAgent
    │   └── CommunicationAgent (Sequential)
    │       ├── SeverityCheckerAgent
    │       ├── EscalatorAgent
    │       └── FirstAidAgent
    └── ProactiveCoachAgent (Preventive Care)
```

### Design Patterns

- **Hierarchical Multi-Agent System**: Parent-child relationships with clear delegation
- **Sequential Pipeline**: CommunicationAgent processes symptoms in order (severity → escalation → first aid)
- **State-Based Communication**: Uses `output_key` to pass data between agents via session state
- **Tool Integration**: Function tools for database, email, and web search

---

## Agent Hierarchy

### Root Agent (PregnancyAssistant)

**Purpose**: Main orchestrator routing queries to specialized agents  
**Model**: `gemini-2.5-flash-lite`  
**Sub-Agents**: IntroducerAgent, SymptomTriageAgent, ProactiveCoachAgent

### IntroducerAgent

**Purpose**: User onboarding, authentication, profile management  
**Workflow**: Email verification → Collect/retrieve user details → Save to database  
**Tools**: `save_user_details`, `get_user_details`, `authenticate_user`, `verify_user`  
**Model**: `gemini-2.0-flash-lite`

### SymptomTriageAgent

**Purpose**: Evaluates symptoms, assesses severity, provides medical guidance  
**Workflow**: Search medical info → Delegate to CommunicationAgent → Filter severity info  
**Tools**: Brave Search, email tool, get_user_details  
**Sub-Agent**: CommunicationAgent (SequentialAgent)  
**Model**: `gemini-2.5-flash-lite`

### CommunicationAgent (SequentialAgent)

**Purpose**: Coordinates symptom assessment pipeline  
**Workflow**:

1. SeverityCheckerAgent evaluates (1-6 scale)
2. If score > 4: EscalatorAgent sends alerts
3. FirstAidAgent provides guidance

### SeverityCheckerAgent

**Purpose**: Evaluates symptom severity (1-6 scale: 1-2 low, 3-4 medium, 5-6 urgent)  
**Output**: `"Severity Score: [1-6]\nSymptoms: [list]"` stored in `severity_score_and_symptoms`  
**Model**: `gemini-2.0-flash-lite`

### EscalatorAgent

**Purpose**: Escalates urgent cases (severity > 4) to doctor and partner  
**Workflow**: Reads severity from state → Gets user details → Sends email alerts → Returns "Email sent successfully"  
**Critical**: Never exposes severity scores to users  
**Model**: `gemini-2.0-flash-lite`

### FirstAidAgent

**Purpose**: Provides calm, urgent first aid guidance  
**Model**: `gemini-2.0-flash-lite`

### ProactiveCoachAgent

**Purpose**: Delivers preventive care and complication prevention  
**Tools**: Brave Search for latest guidelines  
**Model**: `gemini-2.0-flash`

---

## Key Flows

### Flow 1: User Onboarding

```
User → Root → IntroducerAgent
    → Request Email → Send Verification Code
    → Verify Code → Check Database
    → [New User] Collect Details → Save
    → [Existing] Retrieve Details
```

### Flow 2: Normal Symptom Triage (Severity ≤ 4)

```
User Query → Root → SymptomTriageAgent
    → Brave Search (Medical Info)
    → CommunicationAgent (Sequential)
        → SeverityCheckerAgent (Score: 1-4)
        → FirstAidAgent (Guidance)
    → Response (Filtered, No Severity Info)
```

### Flow 3: Urgent Symptom Escalation (Severity > 4)

```
User Query → Root → SymptomTriageAgent
    → Brave Search
    → CommunicationAgent (Sequential)
        → SeverityCheckerAgent (Score: 5-6)
            → Stores in state: severity_score_and_symptoms
        → EscalatorAgent
            → Reads severity from state
            → get_user_details() → Get emails
            → send_email() → Alert doctor & partner
            → Returns: "Email sent successfully"
        → FirstAidAgent (Calm guidance)
    → Response (Filtered, No Severity Info)
```

### Flow 4: Proactive Care

```
User Query → Root → ProactiveCoachAgent
    → Brave Search (Preventive Guidelines)
    → Returns Guidance
```

---

## Key Features

### 1. User Privacy & Security

- Email verification with 6-digit codes
- Case-insensitive email matching (normalized)
- SQL injection protection (parameterized queries)
- Session isolation by user_id and session_id

### 2. Urgent Case Handling

- Automatic escalation for severity > 4
- Multi-recipient alerts (doctor + partner simultaneously)
- Information filtering: severity scores never exposed to users
- Calm communication: reassuring guidance without technical details

### 3. Agent Communication

- State-based data passing via `output_key` pattern
- Sequential processing ensures proper order
- Response filtering removes technical information

### 4. Medical Information

- Real-time web search via Brave Search
- Context-aware searches (pregnancy stage + symptoms)
- Evidence-based guidance from current medical information

### 5. Database & Session Management

- SQLite for user data (`user_details.db`)
- ADK DatabaseSessionService for session persistence
- Tables: `user_details` (user_id, name, email, pregnancy_details, partner_details, doctor_details), `user_authentication` (email, code)

---

## Tools & Integrations

**IntroducerTools** (`tools/introducer.py`): Database operations for user management  
**EmailTool** (`tools/email_tool.py`): Gmail SMTP for notifications (config: `GMAIL_EMAIL`, `GMAIL_APP_PASSWORD`)  
**Brave Search**: MCP integration for web search (config: `BRAVE_API_KEY`)

---

## Error Handling & Security

**Retry Configuration**: 5 attempts, exponential backoff (base 7), retries on 429/500/503/504  
**Graceful Degradation**: System continues if email/search unavailable  
**Security**: Gmail App Passwords, parameterized queries, data normalization, information filtering

---

## Evaluation Criteria

### Key Strengths

1. **Multi-Agent Architecture**: Well-structured hierarchical system with clear responsibilities and proper delegation patterns
2. **Urgent Case Handling**: Automated escalation with proper information filtering - users never see severity scores
3. **User Experience**: Calm, reassuring communication while maintaining medical accuracy
4. **Security**: Proper authentication, data normalization, SQL injection protection
5. **Extensibility**: Modular design allows easy addition of new agents and tools

### Technical Excellence

- Proper use of ADK patterns (SequentialAgent, output_key/input_key for state management)
- State-based agent communication following ADK best practices
- Tool integration using function tools
- Comprehensive error handling and graceful degradation

### Medical Safety

- **No diagnosis provided** - guidance only
- **Urgent cases escalated** to healthcare providers immediately
- **Evidence-based information** via real-time web search
- **Clear separation** between technical assessment and user-facing communication

---

## Project Structure

```
pregnancy-ai-agent/
├── agents/          # 8 specialized agents
├── tools/           # Database & email tools
├── utils/           # Session utilities
├── db/              # SQLite databases
├── config/          # Environment variables
└── main.py          # Entry point
```

---

**Document Version**: 1.0 | **Last Updated**: 2025
