import json
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session
from pypdf import PdfReader
from pypdf.errors import PdfReadError

import ai
import demo
import prompts
import redact

load_dotenv()

# Vercel serves public/ from its CDN, Flask only uses this locally
app = Flask(__name__, static_folder='public/static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

PROFILE_FIELDS = ['branch', 'role', 'years', 'rank', 'leadership', 'interests']


def read_profile(data):
    return {field: str(data.get(field, '')).strip() for field in PROFILE_FIELDS}


def scrubbed(profile):
    return {field: redact.scrub(value)[0] for field, value in (profile or {}).items()}


@app.context_processor
def inject_demo():
    return {'demo_mode': not os.environ.get('GEMINI_API_KEY')}

@app.errorhandler(ai.AIError)
def ai_error(e):
    return jsonify(error=str(e)), 502

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/jobs')
def jobs():
    return render_template('jobs.html', profile=session.get('profile', {}))

@app.route('/certs')
def certs():
    industry = request.args.get('industry', session.get('industry', ''))
    return render_template('certs.html', industry=industry, profile=session.get('profile'))

@app.route('/roadmap')
def roadmap():
    return render_template(
        'roadmap.html',
        profile=session.get('profile', {}),
        jobs=session.get('jobs', []),
        industry=session.get('industry', ''),
        certs=session.get('certs', []),
        resume_done=session.get('resume_done', False),
    )

@app.route('/api/resume', methods=['POST'])
def convert_resume():
    text = request.form.get('text', '').strip()
    upload = request.files.get('file')
    if upload:
        try:
            pages = PdfReader(upload).pages
        except PdfReadError:
            return jsonify(error="That PDF couldn't be opened."), 400
        text = '\n'.join(page.extract_text() or '' for page in pages).strip()
    if not text:
        return jsonify(error='Paste your resume or upload a PDF with selectable text.'), 400

    header, body = redact.split_header(text)
    body, references = redact.split_references(body)
    name = header.splitlines()[0] if header else ''
    names = [word for word in name.split() if len(word) > 2]
    body, hidden = redact.scrub(body, names, redact.header_places(header))

    target = redact.scrub(request.form.get('target', '').strip())[0]
    prompt = f'Target role: {target or "not specified"}\n\nResume:\n{body}'
    result = dict(ai.ask(prompts.RESUME, prompt, demo.RESUME))
    result['resume'] = '\n\n'.join(filter(None, [header, redact.restore(result.get('resume', ''), hidden), references]))
    session['resume_done'] = True
    return jsonify(result)

@app.route('/api/jobs', methods=['POST'])
def match_jobs():
    profile = read_profile(request.get_json())
    if not profile['branch'] or not profile['role']:
        return jsonify(error='Tell us your branch and what you did.'), 400

    result = ai.ask(prompts.JOBS, json.dumps(scrubbed(profile), indent=2), demo.JOBS)
    session['profile'] = profile
    session['jobs'] = [job['title'] for job in result.get('jobs', [])]
    return jsonify(result)

@app.route('/api/certs', methods=['POST'])
def find_certs():
    data = request.get_json()
    industry = str(data.get('industry', '')).strip()
    if not industry:
        return jsonify(error='Pick an industry first.'), 400

    prompt = json.dumps({
        'industry': industry,
        'target_job': redact.scrub(str(data.get('target', '')).strip())[0],
        'profile': scrubbed(session.get('profile')),
    }, indent=2)
    result = ai.ask(prompts.CERTS, prompt, demo.CERTS)
    session['industry'] = industry
    session['certs'] = [cert['name'] for cert in result.get('certs', [])]
    return jsonify(result)

@app.route('/api/roadmap', methods=['POST'])
def build_roadmap():
    profile = read_profile(request.get_json())
    if not profile['branch'] or not profile['role']:
        return jsonify(error='Tell us your branch and what you did.'), 400

    session['profile'] = profile
    prompt = json.dumps({
        'profile': scrubbed(profile),
        'interested_jobs': session.get('jobs', []),
        'target_industry': session.get('industry', ''),
        'planned_certs': session.get('certs', []),
        'resume_converted': session.get('resume_done', False),
    }, indent=2)
    return jsonify(ai.ask(prompts.ROADMAP, prompt, demo.ROADMAP))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
