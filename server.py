from flask import Flask, send_file, Response, render_template, request, url_for
import time
import matplotlib.pyplot as plt
import os
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return render_template('video.html')

@app.route('/video_chunk_page')
def video_chunk_page():
    return render_template('video_chunk.html')

@app.route('/video_chunk')
def video_chunk():
    def generate():
        filepath = os.path.join("static", "videos", "video.mp4")
        with open(filepath, "rb") as f:
            chunk_size = 1024 * 128  # 128 KB por chunk
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
                time.sleep(0.5)  # Puedes ajustar para simular buffering
    return Response(generate(), mimetype='video/mp4')

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        responses = {
            "preg1": request.form.get("preg1"),
            "preg2": request.form.get("preg2"),
            "preg3": request.form.get("preg3"),
            "preg4": request.form.get("preg4"),
            "preg5": request.form.get("preg5"),
            "preg6": request.form.get("preg6"),
            "preg7": request.form.get("preg7")
        }

        with open('survey_results.txt', 'a') as f:
            f.write(str(responses) + "\n")

        for key, val in responses.items():
            with open(f'static/data/{key}.txt', 'a') as pf:
                pf.write(f"{val}\n")

        return '¡Gracias por tu respuesta! <a href="/metrics">Ver estadísticas</a>'

    return render_template('survey.html')

@app.route('/metrics')
def metrics():
    metric_html = "<h2>Resultados de la Encuesta QoE</h2>"
    preguntas = {
        "preg1": "¿Pudo ver el video sin interrupciones?",
        "preg2": "Calidad de imagen (MOS)",
        "preg3": "Calidad de audio (MOS)",
        "preg4": "¿Buffering?",
        "preg5": "¿Demora inicial?",
        "preg6": "Satisfacción general (MOS)",
        "preg7": "¿Cable o Wi-Fi?"
    }

    os.makedirs("static/charts", exist_ok=True)

    for key, label in preguntas.items():
        try:
            with open(f'static/data/{key}.txt', 'r') as f:
                data = [line.strip() for line in f if line.strip()]

            if not data:
                continue

            plt.figure(figsize=(6,4))
            if key in ["preg2", "preg3", "preg6"]:
                data_int = [int(d) for d in data if d.isdigit()]
                plt.hist(data_int, bins=range(1,7), color='orange', edgecolor='black', align='left', rwidth=0.8)
                plt.xticks(range(1, 6))
                avg = sum(data_int)/len(data_int)
                plt.title(f"{label} (promedio: {avg:.2f})")
            else:
                counts = {}
                for d in data:
                    counts[d] = counts.get(d, 0) + 1
                plt.bar(counts.keys(), counts.values(), color='skyblue', edgecolor='black')
                plt.title(label)
                plt.xticks(rotation=15)

            plt.tight_layout()
            chart_path = f"static/charts/{key}.png"
            plt.savefig(chart_path)
            plt.close()

            metric_html += f'<h4>{label}</h4><img src="/{chart_path}" width="400"><br>'

        except Exception as e:
            metric_html += f'<p>Error generando estadística para {label}: {e}</p>'

    return metric_html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

