from flask import Flask, render_template, request, jsonify
from groq import Groq
import os
import re
import logging
from dotenv import load_dotenv

# Load environment variables (look in root directory)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')

# Application Configuration
class Config:
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    MODEL_NAME = 'llama-3.3-70b-versatile'
    MAX_TOKENS = 1500
    TEMPERATURE = 0.2
    INCIDENT_CHAR_LIMIT = 5000

def get_groq_client():
    """Lazy initialization of the Groq client to prevent startup crashes."""
    api_key = Config.GROQ_API_KEY
    if not api_key:
        logger.error("GROQ_API_KEY is not set in environment variables.")
        return None
    
    try:
        return Groq(
            api_key=api_key,
            timeout=60.0,
            max_retries=3
        )
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {str(e)}")
        return None

SYSTEM_PROMPT = """You are a senior DevOps incident response engineer with deep production experience in high-scale systems.

Analyze the following production incident and provide a precise, high-signal response.

Respond STRICTLY in this format:

1. Likely Root Cause:
- Specific explanation grounded in the incident

2. Immediate Fix (Step-by-step):
1. Step one
2. Step two
(Only actionable, no vague advice)

3. Prevention:
- Concrete engineering improvements

4. Similar Past Incident:
- Describe a realistic past incident and how it was resolved

5. Similarity Score:
- Rate how similar this issue is to the past incident (0–100%)
- One-line justification

6. Confidence Level:
- High / Medium / Low
- Brief reason

IMPORTANT:
- Avoid generic advice like 'check logs' or 'restart server' unless absolutely necessary
- Be specific to the given incident
- Prioritize signal over verbosity
- Think like an on-call engineer under pressure
- Responses should feel decisive, not uncertain"""


def parse_llm_response(response_text):
    """Parse the LLM response into structured sections."""
    sections = {
        'root_cause': '',
        'immediate_fix': '',
        'prevention': '',
        'similar_incident': '',
        'similarity_score': '',
        'confidence_level': ''
    }
    
    patterns = {
        'root_cause': r'1\.\s*Likely Root Cause:(.*?)(?=2\.|$)',
        'immediate_fix': r'2\.\s*Immediate Fix.*?:(.*?)(?=3\.|$)',
        'prevention': r'3\.\s*Prevention:(.*?)(?=4\.|$)',
        'similar_incident': r'4\.\s*Similar Past Incident:(.*?)(?=5\.|$)',
        'similarity_score': r'5\.\s*Similarity Score:(.*?)(?=6\.|$)',
        'confidence_level': r'6\.\s*Confidence Level:(.*?)(?=$)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
        if match:
            sections[key] = match.group(1).strip()
    
    return sections


@app.route('/')
def index():
    """Serve the root application page."""
    # Debug log for Vercel startup verification
    if not Config.GROQ_API_KEY:
        logger.warning("Application started without GROQ_API_KEY configured.")
    else:
        logger.info("Application started with GROQ_API_KEY detected.")
        
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Endpoint for incident analysis via AI."""
    data = request.get_json()
    
    if not data or 'incident' not in data:
        return jsonify({'error': 'Missing incident description'}), 400
    
    incident = data['incident'].strip()
    
    if not incident:
        return jsonify({'error': 'Incident description cannot be empty'}), 400
    
    if len(incident) > Config.INCIDENT_CHAR_LIMIT:
        return jsonify({'error': f'Incident description too long (max {Config.INCIDENT_CHAR_LIMIT} characters)'}), 400
    
    # Get client lazily
    client = get_groq_client()
    if not client:
        return jsonify({
            'error': 'AI Analysis Engine is not configured. Please set the GROQ_API_KEY environment variable.'
        }), 503
    
    try:
        user_prompt = f"Incident:\n{incident}"
        
        response = client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': user_prompt}
            ],
            max_tokens=Config.MAX_TOKENS,
            temperature=Config.TEMPERATURE
        )
        
        response_text = response.choices[0].message.content
        parsed = parse_llm_response(response_text)
        
        return jsonify({
            'success': True,
            'result': parsed,
            'raw': response_text
        })
    
    except Exception as e:
        error_msg = str(e)
        status_code = 500
        
        if "401" in error_msg or "invalid_api_key" in error_msg:
            error_msg = "Invalid API Key. Please check your system configuration."
            status_code = 401
        elif "timeout" in error_msg.lower():
            error_msg = "Upstream API timeout. Please try again with a more concise description."
            status_code = 504
            
        logger.exception(f"Analysis error: {error_msg}")
        return jsonify({'error': f'Analysis engine error: {error_msg}'}), status_code


if __name__ == '__main__':
    app.run(debug=True, port=5000)
