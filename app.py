import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
DEFAULT_MARGIN = 200

# 確保上傳資料夾存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 設定 allowed extension 檢查
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# 增加固定邊距和背景的方法
def add_margin_to_pdf(input_pdf_path, output_pdf_path, margin_width, use_grid=False):
    doc = fitz.open(input_pdf_path)
    
    if use_grid:
        grid_image = Image.open('dot_grid.png')
        grid_width, grid_height = grid_image.size  

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        rect = page.rect

        new_media_rect = fitz.Rect(rect.x0, rect.y0, rect.x1 + margin_width, rect.y1)
        page.set_mediabox(new_media_rect)
        page.set_cropbox(new_media_rect)

        if use_grid:
            # Calculate tiles needed to fill the margin
            tiles_needed = (margin_width + grid_width - 1) // grid_width
            scaled_width = margin_width / tiles_needed
            scale_factor = scaled_width / grid_width
            new_grid_height = int(grid_height * scale_factor)

            # Resize grid image
            grid_image_resized = grid_image.resize((int(scaled_width), new_grid_height), Image.LANCZOS)
            temp_image_path = "temp_grid.png"
            grid_image_resized.save(temp_image_path)

            # Tile horizontally and vertically
            y_offset = rect.y0
            while y_offset < rect.y1:
                x_offset = rect.x1
                remaining_width = margin_width
                while remaining_width > 0:
                    current_width = min(scaled_width, remaining_width)
                    tile_rect = fitz.Rect(x_offset, y_offset, 
                                        x_offset + current_width, 
                                        y_offset + new_grid_height)
                    page.insert_image(tile_rect, filename=temp_image_path)
                    x_offset += scaled_width
                    remaining_width -= scaled_width
                y_offset += new_grid_height

    doc.save(output_pdf_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return '沒有檔案', 400
    file = request.files['file']
    use_grid = 'use_grid' in request.form
    
    try:
        margin_width = int(request.form.get('margin_width', DEFAULT_MARGIN))
        if margin_width < 1 or margin_width > 1000:
            margin_width = DEFAULT_MARGIN
    except ValueError:
        margin_width = DEFAULT_MARGIN

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_pdf_path)
        
        output_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_' + filename)
        add_margin_to_pdf(input_pdf_path, output_pdf_path, margin_width, use_grid)
        
        return send_file(output_pdf_path, as_attachment=True)

    return '檔案格式不正確', 400

if __name__ == '__main__':
    app.run(debug=True)
