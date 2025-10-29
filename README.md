# CareerMate, Your Partner on JobSeeking

## Done by 
- Gavind Muhammad Pramahita 
- Muhammad Zidane Septian Irsyadi

An AI-powered career coaching agent with Discord integration that provides personalized career guidance, resume improvement suggestions, job matching, and interview preparation using **FREE local LLM** (Ollama) with persistent memory.


**✅ Complete Feature Set Implemented:**
- 🆓 **FREE Local AI** - Uses Ollama + Llama 3.1:8B (no API costs!)
- 🧠 **Persistent Memory** - Remembers conversations across bot restarts
- 💬 **Natural Language Chat** - Conversational AI with intent detection
- 🎯 **5 Core Career Features** - All working with real AI responses
- 🔗 **Discord Integration** - Full bot with traditional commands + chat
- 🗄️ **Data Storage** - JSON-based persistent storage with backups
- 🧪 **Comprehensive Testing** - 46/53 tests passing
- 📝 **Enterprise Logging** - Structured logging and error handling

## 🚀 Features

### 🎯 **Core Career Coaching**
- **Career Path Analysis**: AI-powered recommendations based on skills, experience, and interests
- **Resume Review**: Detailed analysis with improvement suggestions and ATS optimization
- **Job Matching**: Find opportunities matching your profile and preferences
- **Mock Interviews**: Practice with role-specific questions and detailed feedback
- **Skill Gap Analysis**: Identify and prioritize skills needed for target roles

### 💬 **AI Interaction**
- **Natural Language Chat**: Conversational AI that understands context and intent
- **Command-Based Interface**: Traditional Discord bot commands for specific actions
- **Memory System**: Remembers your skills, preferences, and conversation history
- **Multi-Turn Conversations**: Maintains context across extended discussions

### 🔧 **Technical Features**
- **FREE Local LLM**: Uses Ollama + Llama 3.1:8B (no API costs or rate limits)
- **Persistent Storage**: JSON-based system with automatic backups
- **Multi-Platform**: Discord bot + CLI interface + direct Python API
- **Robust Error Handling**: Graceful fallbacks and comprehensive logging

## 📁 Project Structure

```
Agent LLM/
├── src/
│   ├── career_agent.py         # Core AI agent logic with Ollama integration
│   ├── discord_bot.py          # Discord bot with persistent memory
│   ├── ollama_client.py        # Ollama LLM client wrapper
│   ├── storage.py              # Persistent data storage system
│   ├── conversation_handler.py # Natural language processing
│   ├── config.py               # Multi-provider configuration
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # Structured logging system
│       └── validators.py       # Input validation and sanitization
├── data/                       # Persistent storage (auto-created)
│   ├── user_contexts.json      # User conversation history & skills
│   ├── interview_sessions.json # Active interview sessions
│   └── backups/               # Automatic timestamped backups
├── tests/                      # Comprehensive test suite
│   ├── conftest.py
│   ├── test_career_agent.py
│   ├── test_discord_bot.py
│   └── test_utils.py
├── logs/                       # Application logs (auto-created)
├── main.py                     # CLI interface
├── requirements.txt            # Python dependencies
├── .env.ollama                 # Ollama configuration template
└── README.md                   # This documentation
```

## 🛠️ Setup & Installation

### Prerequisites

- **Python 3.8+** (tested with Python 3.9.6)
- **Ollama** (for FREE local LLM) - **RECOMMENDED**
- **Discord Bot Token** (for Discord integration)
- **Optional**: OpenAI/Anthropic API keys (for cloud LLMs)

### Quick Start with Ollama (FREE!)

1. **Install Ollama**
   ```bash
   # macOS
   brew install ollama
   
   # Start Ollama service
   brew services start ollama
   
   # Download Llama 3.1 model (5GB - one time)
   ollama pull llama3.1:8b
   ```

2. **Clone and setup project**
   ```bash
   git clone <your-repo-url>
   cd "Agent LLM"
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure for Ollama (FREE mode)**
   ```bash
   # Copy Ollama configuration
   cp .env.ollama .env
   
   # Edit .env and add your Discord bot token:
   nano .env
   ```

4. **Setup Discord Bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create new application → Bot → Copy token
   - Add token to `.env` file:
     ```env
     DISCORD_BOT_TOKEN=your_actual_bot_token_here
     ```

### Alternative Setup Options

<details>
<summary><b>🔧 Advanced Configuration Options</b></summary>

**Option 1: Demo Mode (No setup required)**
```bash
cp .env.demo .env
# Uses mock responses, no API keys needed
```

**Option 2: Multiple Provider Support**
```env
# The system will use Ollama as primary, fallback to others
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OPENAI_API_KEY=your_backup_key  # Optional fallback
```

</details>

## 🚀 Usage

### Option 1: Discord Bot (Recommended)

**Start the bot:**
```bash
# With Ollama (FREE)
PYTHONPATH=src python src/discord_bot.py

# The bot will show:
# 🤖 Starting Career Coach Discord Bot...
# 📊 LLM Provider: ollama
# 💾 Loaded X user contexts
# ✅ Bot is ready! Logged in as CareerMate
```

**Natural Language Chat:**
```
Hi there!
I know Python, SQL, and Machine Learning
What careers would you recommend for me?
Can you help me improve my resume?
I want to practice interviewing for a Data Scientist role
```

**Traditional Commands:**
```
!help                                          # Show all commands
!career_analyze Python, SQL, Machine Learning # Career recommendations  
!resume_review                                 # Attach .txt resume file
!job_match Remote, Tech, 90k+                 # Find job opportunities
!mock_interview Data Scientist                # Practice interviews
!skill_gap Python, SQL | Data Scientist       # Analyze skill gaps
```

### Option 2: CLI Interface

**Interactive Mode:**
```bash
python main.py --interactive
```

**Direct Commands:**
```bash
# Career analysis
python main.py --analyze "Python,SQL,Git"

# Resume review
python main.py --resume resume.txt --target-role "Data Scientist"

# Job matching
python main.py --jobs "Python,AWS" "Remote,Tech,80k+"

# Skill gap analysis  
python main.py --skills "Python,SQL" --role "Data Scientist"
```

### Option 3: Python API

```python
from src.career_agent import CareerAgent, UserProfile
from src.config import Config

# Initialize agent
config = Config()
agent = CareerAgent(config)

# Create user profile
profile = UserProfile(
    skills=["Python", "SQL", "Machine Learning"],
    experience=["2 years data analysis"],
    interests=["AI", "Data Science"],
    education=["BS Computer Science"]
)

# Get career recommendations
recommendations = await agent.analyze_career_path(profile)
```

## 🧪 Testing

### Automated Testing
```bash
# Run all tests (46/53 passing)
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_career_agent.py

# Run with coverage report
pytest --cov=src
```

### Manual Testing

**Test Storage System:**
```bash
PYTHONPATH=src python src/storage.py
```

**Test Ollama Integration:**
```bash
# Test direct Ollama connection
ollama run llama3.1:8b "What are the top 3 career skills for 2025?"

# Test via CLI
python main.py --analyze "Python,SQL,Git"
```

**Test Discord Bot Features:**
1. Start bot: `PYTHONPATH=src python src/discord_bot.py`
2. In Discord, try natural conversation:
   ```
   Hi!
   I know Python and want to become a Data Scientist
   What skills should I learn?
   ```
3. Test persistent memory:
   - Have a conversation
   - Restart bot
   - Continue conversation - bot should remember you!

### Memory & Storage Testing

**Verify Persistent Memory:**
```bash
# Check stored data
ls -la data/
cat data/user_contexts.json

# Check backups
ls -la data/backups/
```

## Logging

The application creates log files in the `logs/` directory:

- `career_agent.log` - General application logs
- `discord_bot.log` - Discord bot specific logs
- `errors.log` - Error-only logs

Log levels can be configured via the `LOG_LEVEL` environment variable.

## ⚙️ Configuration

### Environment Variables

**Ollama Configuration (Recommended):**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
DISCORD_BOT_TOKEN=your_bot_token_here
LOG_LEVEL=INFO
LOG_DIR=logs
```

**Other LLM Providers:**
```env
# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_key

# Anthropic
LLM_PROVIDER=anthropic  
ANTHROPIC_API_KEY=your_anthropic_key

# Demo (no API needed)
LLM_PROVIDER=demo
```

### Storage Configuration

**Data Storage:**
- **Location**: `data/` directory (auto-created)
- **Format**: JSON files with automatic backups
- **Backup Retention**: Last 10 versions per file type
- **Auto-save**: Every 10 messages + on shutdown

**Memory Features:**
- **Per-user context**: Remembers skills, preferences, conversation history
- **Cross-session persistence**: Survives bot restarts
- **Interview session tracking**: Maintains interview state
- **Automatic cleanup**: Old backups removed automatically

## 🎯 Project Highlights

### ✨ What Makes This Special

- **🆓 Completely FREE**: Uses local LLM (Ollama) - no API costs ever
- **🧠 Persistent Memory**: Remembers users across bot restarts  
- **💬 Natural Conversations**: ChatGPT-like experience in Discord
- **🚀 Production Ready**: Enterprise logging, error handling, validation
- **🤝 Collaboration Friendly**: Shared data storage for team development
- **📈 Scalable Architecture**: Easy to extend with new features
- **🎪 Multi-Modal Interface**: Discord bot + CLI + Python API

### 📊 Use Cases

- **Career Coaching**: Personal career guidance and skill development
- **Interview Preparation**: Practice with AI feedback and improvement tips
- **Resume Optimization**: Professional resume review and enhancement
- **Educational Tool**: Learn about career paths and skill requirements
- **Portfolio Project**: Demonstrate AI integration and Discord bot development
- **Team Collaboration**: Shared development environment with persistent data




## 👥 Development & Architecture

### Key Components

**🧠 Core Agent** (`career_agent.py`):
- Multi-provider LLM integration (Ollama, OpenAI, Anthropic)
- 5 main career coaching functions with specialized prompting
- Fallback system with demo responses
- Structured data parsing with error handling

**💬 Discord Integration** (`discord_bot.py`):
- Natural language conversation with intent detection
- Traditional command interface for specific actions
- Persistent memory with auto-save functionality
- Session management for interviews and contexts

**🗄️ Storage System** (`storage.py`):
- JSON-based persistent storage with automatic backups
- User context and conversation history management
- Interview session state preservation
- Data integrity protection and recovery

**🤖 Ollama Client** (`ollama_client.py`):
- Async HTTP client for local LLM communication
- Specialized prompting for different analysis types  
- Health checking and error handling
- Context window management (4096 tokens)

### Architecture Principles

- **Modular Design**: Each component has single responsibility
- **Async Operations**: Non-blocking I/O for better performance
- **Graceful Degradation**: Fallbacks when services fail
- **Data Persistence**: User context survives restarts
- **Multi-Interface**: CLI, Discord, and Python API access
- **Provider Agnostic**: Easy switching between LLM providers
