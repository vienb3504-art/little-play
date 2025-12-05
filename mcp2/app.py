import os
import uuid
import shutil
from io import BytesIO
from flask import Flask, request, send_file, jsonify, render_template
import custom_amzqr as amzqr

app = Flask(__name__)

# Configure upload folder and output folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'temp_uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'temp_outputs')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/art_qr', methods=['POST'])
def art_qr():
    input_path = None
    output_path = None
    
    try:
        # 1. Receive user uploaded image
        if 'background' not in request.files:
            return jsonify({'error': 'No background file provided'}), 400
        
        file = request.files['background']
        url = request.form.get('url')
        
        # Get contrast and brightness from form data (default 1.0)
        try:
            contrast = float(request.form.get('contrast', 1.0))
            brightness = float(request.form.get('brightness', 1.0))
        except ValueError:
            contrast = 1.0
            brightness = 1.0
            
        # Get version and level
        try:
            version = int(request.form.get('version', 1))
            if version not in range(1, 41):
                version = 1
        except ValueError:
            version = 1
            
        level = request.form.get('level', 'H')
        if level not in ['L', 'M', 'Q', 'H']:
            level = 'H'
        
        if not url:
            return jsonify({'error': 'No url provided'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Determine file extension
        input_ext = os.path.splitext(file.filename)[1].lower()
        if not input_ext:
            input_ext = '.png'
            
        # Determine output extension
        # Force PNG for static images to avoid "cannot write mode RGBA as JPEG" error
        # Keep GIF for animations
        if input_ext == '.gif':
            output_ext = '.gif'
        else:
            output_ext = '.png'
            
        # Generate unique filenames
        unique_id = str(uuid.uuid4())
        input_filename = f"{unique_id}{input_ext}"
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        
        output_filename = f"out_{unique_id}{output_ext}"
        # amzqr will create the file in save_dir with save_name
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        # Save uploaded file
        file.save(input_path)
        
        # 2. Call amzqr
        try:
            # amzqr.run returns: version, level, qr_name
            amzqr.run(
                words=url,
                version=version,
                level=level,
                picture=input_path,
                colorized=True,
                contrast=contrast,
                brightness=brightness,
                save_name=output_filename,
                save_dir=OUTPUT_FOLDER
            )
        except Exception as e:
            print(f"Error in amzqr: {e}")
            return jsonify({'error': f'Failed to generate QR code: {str(e)}'}), 500

        # 3. Return file and cleanup
        if not os.path.exists(output_path):
             return jsonify({'error': 'Output file was not generated'}), 500

        # Read into memory to allow deleting the file immediately
        with open(output_path, 'rb') as f:
            file_data = f.read()
            
        return send_file(
            BytesIO(file_data),
            mimetype=f'image/{output_ext.strip(".") if output_ext != ".jpg" else "jpeg"}',
            as_attachment=False,
            download_name=output_filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    finally:
        # Cleanup temp files
        if input_path and os.path.exists(input_path):
            try:
                os.remove(input_path)
            except Exception as e:
                print(f"Error deleting input file: {e}")
                
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
            except Exception as e:
                print(f"Error deleting output file: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
