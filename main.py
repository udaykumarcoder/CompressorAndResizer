from flask import Flask, request, send_file, render_template_string
from PIL import Image
import io

app = Flask(__name__)

HTML_FORM = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Resize & Compress Image</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {
      min-height: 100vh;
      margin: 0;
      font-family: 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(135deg, #232526 0%, #414345 100%);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .container {
      background: rgba(30, 30, 30, 0.95);
      border-radius: 18px;
      box-shadow: 0 8px 32px 0 rgba(0,0,0,0.25);
      border: 3px solid #FFD600;
      padding: 2.5rem 2.5rem 2rem 2.5rem;
      max-width: 400px;
      width: 100%;
      color: #fff;
    }
    h2 {
      margin-top: 0;
      font-weight: 700;
      background: linear-gradient(90deg, #FFD600, #fff, #FFD600);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      text-fill-color: transparent;
      letter-spacing: 1px;
      text-align: center;
    }
    form {
      display: flex;
      flex-direction: column;
      gap: 1.1rem;
    }
    label {
      font-size: 1.08rem;
      font-weight: 500;
      color: #FFD600;
      margin-bottom: 0.2rem;
    }
    input[type="number"], input[type="file"] {
      padding: 0.5rem 0.7rem;
      border-radius: 8px;
      border: 2px solid #fff;
      background: #232526;
      color: #FFD600;
      font-size: 1rem;
      outline: none;
      transition: border 0.2s;
    }
    input[type="number"]:focus, input[type="file"]:focus {
      border: 2px solid #FFD600;
    }
    input[type="submit"] {
      margin-top: 0.5rem;
      padding: 0.7rem 0;
      border-radius: 8px;
      border: none;
      background: linear-gradient(90deg, #FFD600 0%, #fff 100%);
      color: #232526;
      font-weight: 700;
      font-size: 1.1rem;
      cursor: pointer;
      box-shadow: 0 2px 8px 0 rgba(255,214,0,0.15);
      transition: background 0.2s, color 0.2s;
    }
    input[type="submit"]:hover {
      background: linear-gradient(90deg, #fff 0%, #FFD600 100%);
      color: #000;
    }
    .info-block {
      margin-top: 1.5rem;
      background: rgba(255,255,255,0.07);
      border: 2px solid #fff;
      border-radius: 10px;
      padding: 1rem 1.2rem;
      color: #FFD600;
      font-size: 1.05rem;
    }
    ul {
      margin: 0.5rem 0 0 1.2rem;
      padding: 0;
    }
    li {
      margin-bottom: 0.3rem;
    }
    .coffee-block {
      margin-top: 2.2rem;
      text-align: center;
      background: rgba(255, 214, 0, 0.08);
      border: 2px solid #FFD600;
      border-radius: 12px;
      padding: 1.2rem 1rem 1.5rem 1rem;
      color: #FFD600;
      box-shadow: 0 2px 8px 0 rgba(255,214,0,0.10);
      max-width: 320px;
      margin-left: auto;
      margin-right: auto;
    }
    .coffee-block h4 {
      margin: 0 0 0.7rem 0;
      color: #FFD600;
      font-size: 1.1rem;
      font-weight: 600;
      letter-spacing: 0.5px;
    }
    .coffee-block img {
      width: 160px;
      height: 160px;
      object-fit: contain;
      border-radius: 10px;
      border: 2px solid #fff;
      background: #fff;
      margin-bottom: 0.5rem;
      margin-top: 0.2rem;
      box-shadow: 0 2px 8px 0 rgba(255,255,255,0.10);
    }
    .coffee-block p {
      margin: 0.5rem 0 0 0;
      color: #fff;
      font-size: 0.98rem;
    }
    @media (max-width: 500px) {
      .container { padding: 1.2rem 0.5rem; }
      h2 { font-size: 1.2rem; }
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Resize & Compress Image</h2>
    <form method=post enctype=multipart/form-data>
      <label>Target Width:</label> <input type=number name=width value=150 required>
      <label>Target Height:</label> <input type=number name=height value=200 required>
      <label>Target File Size (KB):</label> <input type=number name=target_kb value=50 required>
      <input type=file name=image required>
      <input type=submit value="Upload and Convert">
    </form>
    {% if info %}
      <div class="info-block">
        <h3 style="margin-top:0;color:#fff;">Original Image Info:</h3>
        <ul>
          <li>Dimensions: {{ info.width }} x {{ info.height }}</li>
          <li>Size: {{ info.size_kb }} KB</li>
        </ul>
      </div>
    {% endif %}
    <div class="coffee-block">
      <h4>☕ Buy Me a Coffee!</h4>
      <img src="/assets/QR.jpg" alt="Buy Me a Coffee QR">
      <p>Scan the QR code to support this project if it saved you time.<br>Thank you!</p>
    </div>
  </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload():
    info = None
    if request.method == 'POST':
        file = request.files['image']
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        target_kb = int(request.form.get('target_kb'))

        if not file:
            return "❌ No file uploaded."

        # Load and convert image
        img = Image.open(file.stream).convert("RGB")

        # Save original info
        original_buffer = io.BytesIO()
        img.save(original_buffer, format="JPEG", quality=95)
        size_kb = original_buffer.tell() / 1024
        info = {
            "width": img.width,
            "height": img.height,
            "size_kb": round(size_kb, 2)
        }

        # Resize image
        img = img.resize((width, height), Image.LANCZOS)

        # Save initial version
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        current_kb = buffer.tell() / 1024

        # If smaller, pad with dummy bytes
        if current_kb < target_kb - 2:
            padding = b'\x00' * int((target_kb - current_kb) * 1024)
            buffer.write(padding)
            buffer.seek(0)
            return send_file(buffer, mimetype='image/jpeg', as_attachment=True, download_name='padded.jpg')

        # If larger, compress down
        elif current_kb > target_kb:
            quality = 95
            while quality > 5:
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=quality)
                size_kb = buffer.tell() / 1024
                if size_kb <= target_kb:
                    buffer.seek(0)
                    return send_file(buffer, mimetype='image/jpeg', as_attachment=True, download_name='compressed.jpg')
                quality -= 5
            return "❌ Couldn't compress to target size."

        # If already close
        buffer.seek(0)
        return send_file(buffer, mimetype='image/jpeg', as_attachment=True, download_name='final.jpg')

    return render_template_string(HTML_FORM, info=info)

@app.route('/assets/<path:filename>')
def assets(filename):
    return send_file(f"assets/{filename}")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=False)
