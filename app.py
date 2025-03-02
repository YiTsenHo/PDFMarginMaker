from flask import Flask, request, send_file, render_template
import fitz  # PyMuPDF
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 處理 PDF 增加右側空白
def add_margin_to_pdf(input_pdf, output_pdf, right_margin=100):
    doc = fitz.open(input_pdf)
    for page in doc:
        rect = page.rect
        new_width = rect.width + right_margin
        new_rect = fitz.Rect(rect.x0, rect.y0, new_width, rect.y1)
        page.set_mediabox(new_rect)
    doc.save(output_pdf)
    doc.close()

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "沒有選擇檔案！", 400
        file = request.files["file"]
        if file.filename == "":
            return "檔案名稱為空！", 400

        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.join(UPLOAD_FOLDER, "output_" + file.filename)

        file.save(input_path)
        add_margin_to_pdf(input_path, output_path, right_margin=100)

        return send_file(output_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
