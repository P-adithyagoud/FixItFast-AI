import os
import re
import logging
import json
from flask import Flask, render_template, request, jsonify
from groq import Groq
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
    MODEL_NAME = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', 1500))
    TEMPERATURE = float(os.getenv('TEMPERATURE', 0.2))
    INCIDENT_CHAR_LIMIT = 5000

# Singleton client to optimize connection pooling
_groq_client = None

def get_groq_client():
    """Persistent initialization of the Groq client."""
    global _groq_client
    if _groq_client is not None:
        return _groq_client
        
    api_key = Config.GROQ_API_KEY
    if not api_key:
        logger.error("GROQ_API_KEY is not set in environment variables.")
        return None
    
    try:
        _groq_client = Groq(
            api_key=api_key,
            timeout=60.0,
            max_retries=3
        )
        return _groq_client
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {str(e)}")
        return None

SYSTEM_PROMPT = """You are a senior DevOps incident response engineer with deep production experience.

Analyze the incident and respond ONLY with a JSON object.

The JSON MUST follow this schema:
{
  "root_cause": "Detailed explanation of the root cause.",
  "immediate_fix": "Step-by-step numbered list of fixes.",
  "prevention": "Concrete engineering improvements.",
  "similar_incident": "Realistic past incident context.",
  "similarity_score": "0-100% with justification.",
  "confidence_level": "High/Medium/Low with reason."
}

CRITICAL:
- No conversational text before or after the JSON.
- No markdown formatting (like ```json).
- Be specific, actionable, and decisive."""


# Deprecated: parse_llm_response is no longer needed with JSON mode


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
        user_prompt = f"Incident Details:\n{incident}"
        
        response = client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': user_prompt}
            ],
            max_tokens=Config.MAX_TOKENS,
            temperature=Config.TEMPERATURE,
            response_format={"type": "json_object"}
        )
        
        raw_content = response.choices[0].message.content
        try:
            parsed_result = json.loads(raw_content)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode LLM response as JSON: {raw_content}")
            return jsonify({'error': 'The analysis engine returned a malformed response. Please try again.'}), 502

        return jsonify({
            'success': True,
            'result': parsed_result,
            'raw': raw_content
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
