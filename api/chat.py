import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 200

    data = request.json or {}
    messages = data.get('messages', [])
    system = data.get('system', '')

    if not messages or not isinstance(messages, list):
        return jsonify({'error': 'Invalid request body'}), 400

    try:
        openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        site_url = os.environ.get('SITE_URL', 'https://hardik-portfolio-rho.vercel.app')
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {openrouter_api_key}',
            'HTTP-Referer': site_url,
            'X-Title': 'Aishwarya Gupta Portfolio',
        }
        
        payload = {
            'model': 'inclusionai/ring-2.6-1t:free',
            'max_tokens': 800,
            'messages': [{'role': 'system', 'content': system}] + messages
        }
        
        res = requests.post('https://openrouter.ai/api/v1/chat/completions', json=payload, headers=headers)
        
        if not res.ok:
            return jsonify({'error': 'Upstream error', 'detail': res.text}), res.status_code
            
        res_data = res.json()
        choices = res_data.get('choices', [])
        text = 'No response received.'
        if choices:
            text = choices[0].get('message', {}).get('content', 'No response received.')
            
        response = jsonify({'content': [{'text': text}]})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response, 200
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'detail': str(e)}), 500

# Vercel serverless function entrypoint
# It looks for an object named `app` or a function named `handler`
handler = app
