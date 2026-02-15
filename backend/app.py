from flask import Flask, request, jsonify
from flask_cors import CORS
from risk_analyzer import RiskAnalyzer
from backboard_client import BackboardClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize clients
risk_analyzer = RiskAnalyzer()
backboard = BackboardClient(os.getenv('BACKBOARD_API_KEY'))

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        policy_text = request.json.get('policy', '')
        
        if not policy_text or len(policy_text) < 100:
            return jsonify({'error': 'Policy text too short'}), 400
        
        # Phase 1: Basic risk detection
        results = risk_analyzer.analyze(policy_text)
        
        # Phase 2: AI enhancement (if enabled)
        use_ai = request.json.get('use_ai', False)
        if use_ai and backboard.is_configured():
            results = backboard.enhance_analysis(results)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)