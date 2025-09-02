from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.utils import secure_filename
import os
import secrets

from utils import parse_excel
from content import generate_content
from main import dispatch_message

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Optional: upload settings
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB
app.config['UPLOAD_EXTENSIONS'] = ['.xlsx', '.xls']

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/trigger', methods=['POST'])
def trigger_action():
    # Step 1: Excel file
    excel_file = request.files.get('excel_file')
    if not excel_file:
        flash("❌ Please upload an Excel file.", 'error')
        return redirect(url_for('index'))

    filename = secure_filename(excel_file.filename)
    if not filename.lower().endswith(tuple(app.config['UPLOAD_EXTENSIONS'])):
        flash("❌ Invalid file format. Only .xlsx or .xls allowed.", 'error')
        return redirect(url_for('index'))

    # Step 2: Parse
    contacts, msg = parse_excel(excel_file)
    if not contacts:
        flash(msg, 'error')
        return redirect(url_for('index'))

    # Step 3: Get preferences
    mode = request.form.get('mode')
    use_custom = request.form.get('use_custom', 'yes')
    user_message = request.form.get('user_message', '').strip()

    if not mode:
        flash("❌ Please select a communication mode.", 'error')
        return redirect(url_for('index'))

    successes = []
    failures = []

    # Step 4: Loop through all contacts
    for contact in contacts:
        if use_custom == 'yes' and user_message:
            content = user_message
        elif use_custom == 'no':
            content = generate_content(mode, recipient_name=contact.get('name', 'User'))
        else:
            failures.append((contact, "❌ Please enter a message or choose to auto-generate it."))
            continue

        # Step 5: Pick email or phone based on mode
        if mode in ['sms', 'whatsapp', 'call']:
            contact_value = contact.get('phone')
        else:
            contact_value = contact.get('email')

        if not contact_value:
            failures.append((contact, f"❌ Contact info missing for mode '{mode}'."))
            continue

        # Step 6: Send
        if mode == 'email':
            success, dispatch_msg = dispatch_message(mode, content, contact_value, name=contact.get('name', 'User'))
        else:
            success, dispatch_msg = dispatch_message(mode, content, contact_value)

        if success:
            successes.append((contact, dispatch_msg))
        else:
            failures.append((contact, dispatch_msg))

    # Step 7: Summary
    if successes:
        flash(f"✅ Sent to {len(successes)} contact(s).", 'success')
    if failures:
        flash(f"⚠️ Failed to send to {len(failures)} contact(s).", 'error')

    return render_template(
        'summary.html',
        successes=successes,
        failures=failures,
        mode=mode
    )


@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == '__main__':
    # app.run(debug=True, port=5000)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
