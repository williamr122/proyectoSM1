from flask import Flask, request, send_file, Response, render_template, request, url_for
import time
import matplotlib.pyplot as plt
import os
import random
import json
from collections import Counter


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
        with open('ratings.txt', 'a') as rf:
            rf.write(f"{responses['preg6']}\n")
        return '¡Gracias por tu respuesta!'
    return render_template('survey.html')

/* ---------------------  encuesta ------------------------ */


app = Flask(__name__)

# Define the file path for storing survey responses and the static folder for plots
SURVEY_RESPONSES_FILE = 'survey_responses.jsonl'
STATIC_FOLDER = 'static'

# Ensure the static folder exists
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)
# Ensure the static/videos folder exists (if not using a real Flask setup with static files)
if not os.path.exists(os.path.join(STATIC_FOLDER, 'videos')):
    os.makedirs(os.path.join(STATIC_FOLDER, 'videos'))


# Route for the main entry point
@app.route('/')
def index():
    """
    Renders the main index page with navigation links to video and metrics.
    """
    return render_template('index.html')

# Route for the video page
@app.route('/video')
def video_page():
    """
    Renders the video evaluation page.
    Note: In a real Flask app, you'd have a 'video.html' template.
    For simplicity, this example returns the HTML string directly.
    """
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video de Evaluación</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {
                font-family: 'Inter', sans-serif;
                background-color: #f0f4f8;
                color: #333;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                box-sizing: border-box;
            }
            h1, h2 {
                color: #2c5282;
                text-align: center;
                margin-bottom: 1rem;
            }
            .video-container {
                position: relative;
                width: 90%;
                max-width: 960px;
                padding-bottom: 56.25%;
                height: 0;
                overflow: hidden;
                background-color: #000;
                border-radius: 0.75rem;
                box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
                margin-bottom: 2rem;
            }
            .video-container video {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: contain;
                border-radius: 0.75rem;
            }
            .survey-link {
                display: inline-block;
                background-color: #4299e1;
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 0.5rem;
                text-decoration: none;
                font-weight: bold;
                transition: background-color 0.3s ease;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .survey-link:hover {
                background-color: #3182ce;
            }
            @media (max-width: 768px) {
                .video-container {
                    width: 100%;
                }
                body {
                    padding: 10px;
                }
            }
        </style>
    </head>
    <body>
        <h1 class="text-4xl font-extrabold mb-4">Evaluación QoE/QoS</h1>
        <h2 class="text-2xl font-semibold mb-6">Video de prueba local</h2>
        <div class="video-container">
            <video controls>
                <!-- This path assumes 'video.mp4' is in 'static/videos/' -->
                <source src="/static/videos/video.mp4" type="video/mp4">
                Tu navegador no soporta la etiqueta de video.
            </video>
        </div>
        <p>
            <a href="/survey" class="survey-link">Ir a la encuesta QoE</a>
        </p>
    </body>
    </html>
    """


# Route for the survey form
@app.route('/survey', methods=['GET', 'POST'])
def survey():
    """
    Handles displaying the survey form (GET) and processing submissions (POST).
    """
    if request.method == 'POST':
        # Collect all form data
        response_data = {
            'preg1': request.form.get('preg1'),
            'preg2': request.form.get('preg2'),
            'preg3': request.form.get('preg3'),
            'preg4': request.form.get('preg4'),
            'preg5': request.form.get('preg5'),
            'preg6': request.form.get('preg6'),
            'preg7': request.form.get('preg7')
        }
        # Append the response as a JSON object to the file
        try:
            with open(SURVEY_RESPONSES_FILE, 'a') as f:
                f.write(json.dumps(response_data) + '\n')
        except IOError:
            print(f"Error: Could not write to {SURVEY_RESPONSES_FILE}")
            # Optionally, handle this error more gracefully for the user
        return redirect(url_for('metrics')) # Redirect to metrics page after submission
    # Render the survey HTML template for GET requests
    return render_template('survey.html')

# Route for displaying the metrics and generated plots
@app.route('/metrics')
def metrics():
    """
    Reads survey data, generates statistical plots for each question,
    and renders them on the metrics page.
    """
    all_responses = []
    try:
        # Read all survey responses from the JSON Lines file
        with open(SURVEY_RESPONSES_FILE, 'r') as f:
            for line in f:
                try:
                    all_responses.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"Warning: Skipping malformed JSON line: {line.strip()}")
    except FileNotFoundError:
        return """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Métricas de Encuesta QoE</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                body { font-family: 'Inter', sans-serif; background-color: #f0f4f8; color: #333; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
                h2 { color: #2c5282; text-align: center; margin-bottom: 1.5rem; font-size: 2.5rem; font-weight: 700; }
                p { text-align: center; margin-bottom: 1rem; }
                .link-button { display: inline-block; background-color: #4299e1; color: white; padding: 0.75rem 1.5rem; border-radius: 0.5rem; text-decoration: none; font-weight: bold; transition: background-color 0.3s ease; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-top: 1rem; }
                .link-button:hover { background-color: #3182ce; }
            </style>
        </head>
        <body>
            <h2>No hay datos de encuestas para mostrar.</h2>
            <p>Por favor, complete la <a href='/survey' class='link-button'>encuesta</a> primero.</p>
            <p><a href='/' class='link-button'>Volver al Inicio</a></p>
        </body>
        </html>
        """
    except IOError:
        return """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Métricas de Encuesta QoE</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                body { font-family: 'Inter', sans-serif; background-color: #f0f4f8; color: #333; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
                h2 { color: #2c5282; text-align: center; margin-bottom: 1.5rem; font-size: 2.5rem; font-weight: 700; }
                p { text-align: center; margin-bottom: 1rem; }
                .link-button { display: inline-block; background-color: #4299e1; color: white; padding: 0.75rem 1.5rem; border-radius: 0.5rem; text-decoration: none; font-weight: bold; transition: background-color 0.3s ease; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-top: 1rem; }
                .link-button:hover { background-color: #3182ce; }
            </style>
        </head>
        <body>
            <h2>Error al leer los datos de la encuesta.</h2>
            <p>Intente de nuevo más tarde.</p>
            <p><a href='/' class='link-button'>Volver al Inicio</a></p>
        </body>
        </html>
        """

    if not all_responses:
        return """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Métricas de Encuesta QoE</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                body { font-family: 'Inter', sans-serif; background-color: #f0f4f8; color: #333; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
                h2 { color: #2c5282; text-align: center; margin-bottom: 1.5rem; font-size: 2.5rem; font-weight: 700; }
                p { text-align: center; margin-bottom: 1rem; }
                .link-button { display: inline-block; background-color: #4299e1; color: white; padding: 0.75rem 1.5rem; border-radius: 0.5rem; text-decoration: none; font-weight: bold; transition: background-color 0.3s ease; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-top: 1rem; }
                .link-button:hover { background-color: #3182ce; }
            </style>
        </head>
        <body>
            <h2>No hay datos de encuestas para mostrar.</h2>
            <p>Por favor, complete la <a href='/survey' class='link-button'>encuesta</a> primero.</p>
            <p><a href='/' class='link-button'>Volver al Inicio</a></p>
        </body>
        </html>
        """

    plot_html = "" # String to accumulate HTML for all plots

    # --- Generate plots for each question ---

    # Question 1: ¿Pudo ver el video sin interrupciones ni pausas prolongadas? (Sí/No)
    q1_data = [r['preg1'] for r in all_responses if 'preg1' in r and r['preg1'] in ['Si', 'No']]
    if q1_data:
        counts = Counter(q1_data)
        labels = ['Sí', 'No'] # Ensure consistent order
        values = [counts.get('Si', 0), counts.get('No', 0)]

        plt.figure(figsize=(7, 5))
        plt.bar(labels, values, color=['#63b3ed', '#fc8181'], edgecolor='black', width=0.6) # Tailwind colors
        plt.title('1. Interrupciones del video', fontsize=14)
        plt.xlabel('Respuesta', fontsize=12)
        plt.ylabel('Cantidad de Respuestas', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.yticks(range(0, max(values) + 2, 1)) # Ensure integer ticks
        plt.tight_layout()
        filename = os.path.join(STATIC_FOLDER, 'q1_interruptions.png')
        plt.savefig(filename)
        plt.close()
        plot_html += f'<h3>1. ¿Pudo ver el video sin interrupciones ni pausas prolongadas?</h3><img src="/static/{os.path.basename(filename)}" alt="Gráfico de interrupciones del video"><br><br>'

    # Question 2: ¿Cómo calificaría la calidad de la imagen? (MOS)
    q2_data = [int(r['preg2']) for r in all_responses if 'preg2' in r and r['preg2'].isdigit()]
    if q2_data:
        plt.figure(figsize=(7, 5))
        plt.hist(q2_data, bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5], color='#9ae6b4', edgecolor='black', align='mid', rwidth=0.8) # Tailwind green
        plt.title('2. Calidad de la imagen (MOS)', fontsize=14)
        plt.xlabel('Calificación (1-5)', fontsize=12)
        plt.ylabel('Cantidad de Respuestas', fontsize=12)
        plt.xticks(range(1, 6))
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        filename = os.path.join(STATIC_FOLDER, 'q2_image_mos.png')
        plt.savefig(filename)
        plt.close()
        plot_html += f'<h3>2. ¿Cómo calificaría la calidad de la imagen? (MOS)</h3><img src="/static/{os.path.basename(filename)}" alt="Gráfico MOS de calidad de imagen"><br><br>'

    # Question 3: ¿Cómo calificaría la calidad del audio? (MOS)
    q3_data = [int(r['preg3']) for r in all_responses if 'preg3' in r and r['preg3'].isdigit()]
    if q3_data:
        plt.figure(figsize=(7, 5))
        plt.hist(q3_data, bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5], color='#feb2b2', edgecolor='black', align='mid', rwidth=0.8) # Tailwind red
        plt.title('3. Calidad del audio (MOS)', fontsize=14)
        plt.xlabel('Calificación (1-5)', fontsize=12)
        plt.ylabel('Cantidad de Respuestas', fontsize=12)
        plt.xticks(range(1, 6))
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        filename = os.path.join(STATIC_FOLDER, 'q3_audio_mos.png')
        plt.savefig(filename)
        plt.close()
        plot_html += f'<h3>3. ¿Cómo calificaría la calidad del audio? (MOS)</h3><img src="/static/{os.path.basename(filename)}" alt="Gráfico MOS de calidad de audio"><br><br>'

    # Question 4: ¿El video se detuvo para cargar (buffering)?
    q4_data = [r['preg4'] for r in all_responses if 'preg4' in r]
    if q4_data:
        # Define order for categories
        order = ['Nunca', '1 o 2 veces', 'Varias veces', 'Continuamente']
        counts = Counter(q4_data)
        # Sort counts according to the defined order, handling missing keys
        sorted_labels = [k for k in order if k in counts]
        sorted_values = [counts[k] for k in sorted_labels]

        plt.figure(figsize=(9, 5))
        plt.bar(sorted_labels, sorted_values, color='#81e6d9', edgecolor='black', width=0.7) # Tailwind teal
        plt.title('4. Frecuencia de Buffering', fontsize=14)
        plt.xlabel('Frecuencia', fontsize=12)
        plt.ylabel('Cantidad de Respuestas', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xticks(rotation=45, ha='right', fontsize=10) # Rotate labels for better readability
        plt.yticks(range(0, max(sorted_values) + 2, 1)) # Ensure integer ticks
        plt.tight_layout() # Adjust layout to prevent labels from overlapping
        filename = os.path.join(STATIC_FOLDER, 'q4_buffering.png')
        plt.savefig(filename)
        plt.close()
        plot_html += f'<h3>4. ¿El video se detuvo para cargar (buffering)?</h3><img src="/static/{os.path.basename(filename)}" alt="Gráfico de frecuencia de buffering"><br><br>'

    # Question 5: ¿Hubo una demora notable al empezar el video?
    q5_data = [r['preg5'] for r in all_responses if 'preg5' in r]
    if q5_data:
        # Define order for categories
        order = ['No, comenzó enseguida', 'Sí, pero leve', 'Sí, fue molesta', 'Muy larga, casi abandono']
        counts = Counter(q5_data)
        # Sort counts according to the defined order, handling missing keys
        sorted_labels = [k for k in order if k in counts]
        sorted_values = [counts[k] for k in sorted_labels]

        plt.figure(figsize=(10, 5))
        plt.bar(sorted_labels, sorted_values, color='#a78bfa', edgecolor='black', width=0.7) # Tailwind purple
        plt.title('5. Demora al empezar el video', fontsize=14)
        plt.xlabel('Respuesta', fontsize=12)
        plt.ylabel('Cantidad de Respuestas', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xticks(rotation=45, ha='right', fontsize=10) # Rotate labels for better readability
        plt.yticks(range(0, max(sorted_values) + 2, 1)) # Ensure integer ticks
        plt.tight_layout() # Adjust layout to prevent labels from overlapping
        filename = os.path.join(STATIC_FOLDER, 'q5_startup_delay.png')
        plt.savefig(filename)
        plt.close()
        plot_html += f'<h3>5. ¿Hubo una demora notable al empezar el video?</h3><img src="/static/{os.path.basename(filename)}" alt="Gráfico de demora al inicio del video"><br><br>'

    # Question 6: ¿Qué tan satisfecho está con la experiencia general? (MOS final)
    q6_data = [int(r['preg6']) for r in all_responses if 'preg6' in r and r['preg6'].isdigit()]
    if q6_data:
        plt.figure(figsize=(7, 5))
        plt.hist(q6_data, bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5], color='#fbd38d', edgecolor='black', align='mid', rwidth=0.8) # Tailwind orange
        plt.title('6. Satisfacción general (MOS final)', fontsize=14)
        plt.xlabel('Calificación (1-5)', fontsize=12)
        plt.ylabel('Cantidad de Respuestas', fontsize=12)
        plt.xticks(range(1, 6))
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        filename = os.path.join(STATIC_FOLDER, 'q6_overall_mos.png')
        plt.savefig(filename)
        plt.close()
        plot_html += f'<h3>6. ¿Qué tan satisfecho está con la experiencia general? (MOS final)</h3><img src="/static/{os.path.basename(filename)}" alt="Gráfico MOS de satisfacción general"><br><br>'

    # Question 7: ¿Estaba conectado por cable o Wi-Fi?
    q7_data = [r['preg7'] for r in all_responses if 'preg7' in r and r['preg7'] in ['Cable', 'Wi-Fi']]
    if q7_data:
        counts = Counter(q7_data)
        labels = ['Cable', 'Wi-Fi'] # Ensure consistent order
        values = [counts.get('Cable', 0), counts.get('Wi-Fi', 0)]

        plt.figure(figsize=(7, 5))
        plt.bar(labels, values, color=['#4fd1c5', '#f6ad55'], edgecolor='black', width=0.6) # Tailwind colors
        plt.title('7. Tipo de Conexión', fontsize=14)
        plt.xlabel('Tipo de Conexión', fontsize=12)
        plt.ylabel('Cantidad de Respuestas', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.yticks(range(0, max(values) + 2, 1)) # Ensure integer ticks
        plt.tight_layout()
        filename = os.path.join(STATIC_FOLDER, 'q7_connection_type.png')
        plt.savefig(filename)
        plt.close()
        plot_html += f'<h3>7. ¿Estaba conectado por cable o Wi-Fi?</h3><img src="/static/{os.path.basename(filename)}" alt="Gráfico de tipo de conexión"><br><br>'

    # Calculate overall average MOS from Question 6
    overall_avg_mos = sum(q6_data) / len(q6_data) if q6_data else 0

    # Return the HTML with all generated plots
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Métricas de Encuesta QoE</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{
                font-family: 'Inter', sans-serif;
                background-color: #f0f4f8;
                color: #333;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
                box-sizing: border-box;
                min-height: 100vh;
                margin: 0;
            }}
            h2 {{
                color: #2c5282;
                text-align: center;
                margin-bottom: 1.5rem;
                font-size: 2.5rem; /* text-4xl */
                font-weight: 700; /* font-bold */
            }}
            h3 {{
                color: #4a5568;
                margin-top: 2rem;
                margin-bottom: 1rem;
                font-size: 1.5rem; /* text-xl */
                font-weight: 600; /* font-semibold */
                text-align: center;
            }}
            img {{
                max-width: 100%;
                height: auto;
                border-radius: 0.75rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin: 0 auto; /* Center images */
                display: block;
            }}
            .back-link {{
                display: inline-block;
                background-color: #4299e1;
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 0.5rem;
                text-decoration: none;
                font-weight: bold;
                transition: background-color 0.3s ease;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-top: 2rem;
            }}
            .back-link:hover {{
                background-color: #3182ce;
            }}
            .home-link {{ /* New style for home link */
                display: inline-block;
                background-color: #63b3ed; /* A different blue */
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 0.5rem;
                text-decoration: none;
                font-weight: bold;
                transition: background-color 0.3s ease;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-top: 1rem; /* Space from previous link */
            }}
            .home-link:hover {{
                background-color: #4299e1;
            }}
            @media (max-width: 768px) {{
                h2 {{
                    font-size: 2rem;
                }}
                h3 {{
                    font-size: 1.25rem;
                }}
            }}
        </style>
    </head>
    <body>
        <h2>Métricas de Encuesta QoE</h2>
        <h3>Promedio MOS General (Pregunta 6): {overall_avg_mos:.2f}</h3>
        <br>
        {plot_html}
        <p>
            <a href="/survey" class="back-link">Volver a la Encuesta</a>
            <a href="/" class="home-link">Volver al Inicio</a>
        </p>
    </body>
    </html>

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

