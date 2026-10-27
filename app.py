import io
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_file
from pypdf import PdfReader
from pypdf.errors import PdfReadError

import ai
import careers
import export
import prompts
import redact

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Vercel serves public/ from its CDN, Flask only uses this locally
app = Flask(__name__, static_folder='public/static')


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
    return render_template('jobs.html', branches=list(careers.MILITARY))

@app.route('/certs')
def certs():
    industry = request.args.get('industry', '')
    job = careers.OCCUPATIONS.get(request.args.get('job', ''))
    if job:
        certs = careers.certs_for(request.args['job'])
    else:
        certs = careers.CERTS.get(industry, [])
    return render_template(
        'certs.html',
        industries=list(careers.CERTS),
        industry=industry,
        job=job,
        certs=certs,
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
        text = export.tidy('\n'.join(page.extract_text() or '' for page in pages)).strip()
    if not text:
        return jsonify(error='Paste your resume or upload a PDF with selectable text.'), 400

    header, body = redact.split_header(text)
    body, references = redact.split_references(body)
    name = header.splitlines()[0] if header else ''
    names = [word for word in name.split() if len(word) > 2]
    body, hidden = redact.scrub(body, names, redact.header_places(header))

    target = redact.scrub(request.form.get('target', '').strip())[0]
    prompt = f'Target role: {target or "not specified"}\n\nResume:\n{body}'
    result = dict(ai.ask(prompts.RESUME, prompt))
    result['resume'] = '\n\n'.join(filter(None, [header, redact.restore(result.get('resume', ''), hidden), references]))
    return jsonify(result)

@app.route('/api/resume/download', methods=['POST'])
def download_resume():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()
    kind = data.get('format')
    if not text or kind not in ('docx', 'pdf'):
        return jsonify(error='Nothing to download yet.'), 400

    if kind == 'docx':
        body, mimetype = export.to_docx(text), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    else:
        body, mimetype = export.to_pdf(text), 'application/pdf'
    return send_file(io.BytesIO(body), mimetype=mimetype, as_attachment=True, download_name=export.filename(text, kind))

@app.route('/api/military')
def military_jobs():
    return jsonify(careers.search(request.args.get('branch', ''), request.args.get('q', '')))

@app.route('/api/jobs', methods=['POST'])
def match_jobs():
    data = request.get_json() or {}
    branch = data.get('branch')
    index = data.get('id')
    if branch not in careers.MILITARY or not isinstance(index, int) or not 0 <= index < len(careers.MILITARY[branch]):
        return jsonify(error='Pick your branch and job from the list first.'), 400

    return jsonify(jobs=careers.match(branch, index, bool(data.get('led'))))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
