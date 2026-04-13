from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import io

app = Flask(__name__)
CORS(app) # ブラウザからのアクセスを許可

@app.route('/ai-process', methods=['POST'])
def ai_process():
    public_key = request.form.get('public_key')
    image_file = request.files
    
    try:
        # 1. タスク開始
        start_url = "https://iloveapi.com"
        headers = {"Authorization": f"Bearer {public_key}"}
        res = requests.get(start_url, headers=headers).json()
        server, task = res['server'], res['task']

        # 2. アップロード
        upload_url = f"https://{server}/v1/upload"
        files = {'file': (image_file.filename, image_file.read(), 'image/jpeg')}
        requests.post(upload_url, data={'task': task}, files=files)

        # 3. 実行 (2倍アップスケール)
        process_url = f"https://{server}/v1/process"
        requests.post(process_url, json={
            'task': task, 'tool': 'upscaleimg', 'upscale_factor': 2
        })

        # 4. ダウンロード
        download_url = f"https://{server}/v1/download/{task}"
        img_res = requests.get(download_url)
        
        return send_file(io.BytesIO(img_res.content), mimetype='image/jpeg')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
