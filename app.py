import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
FIXED_MARGIN = 200  # 固定增加 200px 邊距

# 確保上傳資料夾存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 設定 allowed extension 檢查
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# 增加固定邊距和背景的方法
def add_margin_to_pdf(input_pdf_path, output_pdf_path, use_grid=False):
    doc = fitz.open(input_pdf_path)
    
    # 讀取 dot_grid.png 並取得原始尺寸
    if use_grid:
        grid_image = Image.open('dot_grid.png')
        grid_width, grid_height = grid_image.size  

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        rect = page.rect

        # 設定新的 MediaBox
        new_media_rect = fitz.Rect(rect.x0, rect.y0, rect.x1 + FIXED_MARGIN, rect.y1)
        page.set_mediabox(new_media_rect)
        page.set_cropbox(new_media_rect)

        if use_grid:
            # 計算需要填滿的寬高
            margin_width = FIXED_MARGIN
            margin_height = int(rect.height)

            # 縮放 dot_grid.png 保持比例
            scale_factor = margin_width / grid_width
            new_grid_height = int(grid_height * scale_factor)

            # 避免超出高度
            if new_grid_height > margin_height:
                scale_factor = margin_height / grid_height
                new_grid_width = int(grid_width * scale_factor)
                new_grid_height = margin_height
            else:
                new_grid_width = margin_width

            # 調整 dot_grid.png 尺寸
            grid_image_resized = grid_image.resize((new_grid_width, new_grid_height), Image.LANCZOS)

            # 存成暫存檔案
            temp_image_path = "temp_grid.png"
            grid_image_resized.save(temp_image_path)

            # 平鋪填滿整個區域
            y_offset = rect.y0
            while y_offset < rect.y1:
                tile_rect = fitz.Rect(rect.x1, y_offset, rect.x1 + new_grid_width, y_offset + new_grid_height)
                page.insert_image(tile_rect, filename=temp_image_path)
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
    use_grid = 'use_grid' in request.form  # 是否使用背景

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_pdf_path)
        
        output_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_' + filename)
        add_margin_to_pdf(input_pdf_path, output_pdf_path, use_grid)
        
        return send_file(output_pdf_path, as_attachment=True)

    return '檔案格式不正確', 400

if __name__ == '__main__':
    app.run(debug=True)
