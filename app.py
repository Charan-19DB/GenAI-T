import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config

import database
from auth import auth_bp
import gemini_helper
import markdown
import json

app = Flask(__name__)
app.config.from_object(Config)

# Enable ProxyFix for Render HTTPS reverse proxy sessions
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize database
database.init_db()


# Register auth blueprint
app.register_blueprint(auth_bp)

@app.route('/')
def landing():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html', full_name=session.get('full_name'))

@app.route('/api/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if not Config.GEMINI_API_KEY:
        return jsonify({'error': 'API key not configured.'}), 500

    data = request.get_json()
    prompt = data.get('prompt')
    task_type = data.get('task_type', 'general')

    if not prompt or not prompt.strip():
        return jsonify({'error': 'Prompt cannot be empty.'}), 400

    try:
        md_extensions = ['markdown.extensions.tables', 'markdown.extensions.fenced_code']

        # ==========================================
        # TASK 1: Structured Format
        # ==========================================
        if task_type == 'structured':
            response_text = gemini_helper.generate_normal_response(prompt)
            html_output = markdown.markdown(response_text, extensions=md_extensions)
            # Verify Markdown tables and lists using Regex
            import re
            has_table = bool(re.search(r'\|[-\s:]+\|', response_text))
            has_list = bool(re.search(r'(?m)^[\s]*([-*+]|\d+\.)\s+', response_text))
            
            status_message = "✅ Verified: Markdown Table and List found." if (has_table and has_list) else "⚠️ Warning: Expected Markdown Table and Bullet List structures were not fully detected."
            
            return jsonify({
                'type': 'structured',
                'html': html_output,
                'status': status_message,
                'success': (has_table and has_list)
            })

        # ==========================================
        # TASK 2: JSON Generation (with refinement)
        # ==========================================
        elif task_type == 'json':
            parsed_data, raw_text, was_refined, success = gemini_helper.generate_json_with_refinement(prompt)
            
            if success:
                # Beautifully format the JSON
                formatted_json = json.dumps(parsed_data, indent=4)
                html_output = markdown.markdown(f"```json\n{formatted_json}\n```", extensions=md_extensions)
                status_message = "✅ JSON Syntax Validated Successfully!"
                if was_refined:
                    status_message += " (Required auto-refinement to fix syntax errors)"
            else:
                html_output = markdown.markdown(raw_text, extensions=md_extensions)
                status_message = "❌ Error: Failed to generate valid JSON after retries."
                
            return jsonify({
                'type': 'json',
                'html': html_output,
                'status': status_message,
                'success': success
            })

        # ==========================================
        # TASK 3: Chain-of-Thought
        # ==========================================
        elif task_type == 'cot':
            # 1. Baseline (Direct Answer)
            baseline_response = gemini_helper.generate_normal_response(prompt)
            baseline_html = markdown.markdown(baseline_response, extensions=md_extensions)
            
            # 2. Zero-Shot CoT
            cot_prompt = prompt + "\n\nLet's think step by step. Explain your reasoning before the final answer."
            cot_response = gemini_helper.generate_normal_response(cot_prompt)
            cot_html = markdown.markdown(cot_response, extensions=md_extensions)
            
            return jsonify({
                'type': 'cot',
                'baseline_html': baseline_html,
                'cot_html': cot_html,
                'status': "✅ Chain-of-Thought comparison generated successfully."
            })

        # ==========================================
        # GENERAL CHAT
        # ==========================================
        else:
            response_text = gemini_helper.generate_normal_response(prompt)
            html_output = markdown.markdown(response_text, extensions=md_extensions)
            return jsonify({
                'type': 'general',
                'html': html_output
            })

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.errorhandler(500)
def handle_500_error(e):
    return jsonify({'error': 'Server Error (500). Please check that GEMINI_API_KEY is configured in Render Environment Variables.'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)



