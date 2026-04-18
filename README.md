# AI Incident Response Assistant

A production-grade MVP for analyzing DevOps incidents in seconds using AI. Built for hackathon impact with maximum clarity and minimum complexity.

## Features

- **Instant Analysis**: Paste an incident and get expert-level diagnosis
- **Structured Output**: Root cause, immediate fixes, prevention steps, and confidence level
- **Demo-Ready**: Clean, modern UI optimized for live presentations
- **No Database**: Pure Flask + OpenAI API, runs locally with minimal setup

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **AI**: OpenAI API (Claude 3.5 Sonnet)
- **Deployment**: Local development server

## Quick Start

### 1. Prerequisites

- Python 3.8+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### 2. Setup

```bash
# Clone or extract the project
cd incident-response-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### 3. Run

```bash
python api/index.py
```

The app will be available at: **http://localhost:5000**

## Project Structure

```
.
├── app.py                  # Flask backend
├── requirements.txt        # Python dependencies
├── .env                    # API key (create this)
├── templates/
│   └── index.html         # Frontend HTML
└── static/
    ├── style.css          # Styling
    └── script.js          # Client-side logic
```

## How It Works

1. **User Input**: Paste incident (logs, errors, description)
2. **Backend Processing**:
   - Validates input (max 5000 chars)
   - Calls OpenAI with system prompt (senior DevOps engineer)
   - Parses response into structured sections
3. **Frontend Display**: Shows 6 cards with instant, actionable intelligence
   - Root Cause
   - Immediate Fix (step-by-step)
   - Prevention strategies
   - Similar Past Incident (realistic example)
   - Similarity Score
   - Confidence Level

## LLM Behavior

The system uses a specialized prompt that instructs the AI to:
- Think like an on-call engineer under pressure
- Provide specific, actionable advice (not generic tips)
- Avoid vague suggestions ("check logs" only if critical)
- Be decisive, not uncertain
- Include realistic past incident context

## API Response Format

The backend returns parsed sections:

```json
{
  "success": true,
  "result": {
    "root_cause": "Database connection pool exhausted due to...",
    "immediate_fix": "1. Restart database service\n2. Increase connection pool...",
    "prevention": "- Implement connection pooling...",
    "similar_incident": "Similar issue occurred on 2023-03-15...",
    "similarity_score": "85% - Both involve database resources",
    "confidence_level": "High - Clear symptoms match known patterns"
  }
}
```

## Configuration

### Timeout & Limits

- **Input limit**: 5000 characters
- **API timeout**: 30 seconds
- **Max tokens**: 1500 (LLM response)

### Customization

Edit the `SYSTEM_PROMPT` in `app.py` to modify AI behavior:
- Change instructions for different incident types
- Adjust tone and detail level
- Add domain-specific guidance

## Example Incidents

### Database Outage
```
Error connecting to database: Connection timeout after 30s
Services: API, Analytics, Auth
Failed queries: SELECT * FROM users (999 concurrent)
Last deployment: 2 hours ago (ORM upgrade)
```

### Memory Leak
```
Memory usage: 87% → 98% in 2 hours
Service: video-processor
Restart: temporary fix (comes back in ~4h)
New code: streaming pipeline refactored
```

### Deployment Issue
```
Container rollout failed
Error: Image push to registry timeout (504 Gateway)
Current: v2.1.5, Target: v2.2.0
Network: 15% packet loss on internal network
```

## Troubleshooting

### API Key Issues
```bash
# Make sure .env exists and contains your key:
cat .env
# Should show: OPENAI_API_KEY=sk-...
```

### Port Already in Use
```bash
# Change port in app.py:
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change 5000 to 5001
```

### Slow Responses
- Check internet connection
- Verify API quota and rate limits
- Ensure API key is valid

## Demo Tips

1. **Prepare incidents**: Have 2-3 realistic scenarios ready
2. **Show the flow**: Paste incident → click analyze → see results
3. **Highlight specificity**: Point out how responses are tailored to the incident
4. **Time it**: Most responses in 5-10 seconds
5. **Mobile demo**: Works great on tablets for team environments

## Performance Notes

- Average response time: 5-10 seconds
- Input processing: <100ms
- UI rendering: <200ms
- Bottleneck: OpenAI API latency

## Security Notes

- API key stored in `.env` (add to `.gitignore`)
- No user data stored
- No authentication needed (internal use only)
- HTTPS recommended for production

## Next Steps (Future)

- [ ] Add incident history (in-memory store)
- [ ] Export analysis as PDF
- [ ] Slack integration
- [ ] Team collaboration features
- [ ] Custom prompt templates
- [ ] Metrics dashboard

## License

MIT - Use freely for hackathons and internal projects.

---

**Built for maximum impact with minimum complexity.** 🚀
