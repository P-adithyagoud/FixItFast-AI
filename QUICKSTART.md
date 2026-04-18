# 🚀 Quick Start Guide

## 30-Second Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env with your OpenAI API key
echo "OPENAI_API_KEY=sk-..." > .env

# 3. Run the app
python api/index.py

# 4. Open browser
# → http://localhost:5000
```

## File Overview

| File | Purpose |
|------|---------|
| `app.py` | Flask backend + OpenAI integration |
| `requirements.txt` | Python dependencies |
| `.env` | Your API key (create this) |
| `templates/index.html` | Frontend structure |
| `static/style.css` | Professional styling |
| `static/script.js` | Client-side logic |
| `README.md` | Full documentation |

## What You Get

✅ **Full-stack Incident Analysis System**
- Paste incident → AI analyzes → Get structured output
- 6 result cards: Root Cause, Fix, Prevention, Similar Incident, Score, Confidence
- Clean, modern demo-ready UI
- Works locally with no database

✅ **Production-Grade Code**
- Error handling & validation
- Responsive design
- Dark mode support
- Accessibility (WCAG)
- ~500 lines of clean, readable code

✅ **Demo Ready**
- 5-10 second response time
- Beautiful result cards
- Smooth animations
- Mobile friendly

## One-Line Explainer

"Production-scale incident diagnosis in your browser, powered by AI."

## Need Help?

1. Check `README.md` for detailed setup
2. See troubleshooting section for common issues
3. Review example incidents for test data

---

Ready to demo? Go to http://localhost:5000 and paste an incident! 🎯
