# versao3
from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import os, uuid, textwrap, subprocess

app = Flask(__name__)

@app.route("/")
def health():
    return jsonify({"status": "ok", "versao": "3"})

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"rotas": "ok", "criar-video": "disponivel"})

@app.route("/criar-video", methods=["POST"])
def criar_video_endpoint():
    try:
        frase = request.form.get("frase", "")
        arquivo = request.files.get("imagem")
        if not frase or not arquivo:
            return jsonify({"erro": "Frase e imagem sao obrigatorios"}), 400
        uid = str(uuid.uuid4())
        imagem_path = f"/tmp/{uid}.jpg"
        output_path = f"/tmp/{uid}.mp4"
        arquivo.save(imagem_path)
        img = Image.open(imagem_path).convert("RGB")
        img = img.resize((1080, 1920), Image.LANCZOS)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        except:
            font = ImageFont.load_default()
        linhas = textwrap.wrap(frase, width=25)
        y = img.height // 2 - (len(linhas) * 90) // 2
        for linha in linhas:
            bbox = draw.textbbox((0, 0), linha, font=font)
            w = bbox[2] - bbox[0]
            x = (img.width - w) // 2
            draw.text((x+3, y+3), linha, font=font, fill=(0, 0, 0))
            draw.text((x, y), linha, font=font, fill=(255, 255, 255))
            y += 90
        frame_path = imagem_path.replace(".jpg", "_frame.jpg")
        img.save(frame_path)
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1",
            "-i", frame_path,
            "-t", "5",
            "-vf", "scale=1080:1920",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_path
        ], check=True)
        os.remove(imagem_path)
        os.remove(frame_path)
        return send_file(output_path, mimetype="video/mp4", as_attachment=True, download_name="video.mp4")
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
