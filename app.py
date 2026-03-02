import os
import psycopg2
from psycopg2.extras import DictCursor
import json
from flask import Flask, request, render_template_string, redirect, url_for
from datetime import datetime

# ⚠️ PEGA AQUÍ TU ENLACE DE NEON.TECH (Entre las comillas) ⚠️
DATABASE_URL = "postgresql://tu_usuario:tu_contraseña@tu_host.neon.tech/neondb?sslmode=require"

app = Flask(__name__)

# --- CONEXIÓN A POSTGRESQL ---
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# --- INICIALIZACIÓN DE LA BASE DE DATOS (POSTGRESQL) ---
def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # En PostgreSQL, AUTOINCREMENT se escribe como SERIAL
    c.execute('''
        CREATE TABLE IF NOT EXISTS ejercicios (
            id SERIAL PRIMARY KEY,
            sesion TEXT,
            musculo TEXT,
            nombre TEXT,
            series INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id SERIAL PRIMARY KEY,
            fecha TEXT,
            ejercicio_id INTEGER,
            serie INTEGER,
            kg REAL,
            reps INTEGER,
            rir INTEGER
        )
    ''')
    
    # Verificamos si la tabla está vacía para rellenarla con tu rutina
    c.execute('SELECT COUNT(*) FROM ejercicios')
    count = c.fetchone()[0]
    
    if count == 0:
        ejercicios = [
            ('EMPUJE', 'PECTORAL', 'Press banca con barra', 3),
            ('EMPUJE', 'PECTORAL', 'Press banca inclinado en multipower', 3),
            ('EMPUJE', 'PECTORAL', 'Cruce de polea ascendente parado', 3),
            ('EMPUJE', 'DELTOIDES LATERAL', 'Elevaciones laterales en maquina', 3),
            ('EMPUJE', 'DELTOIDES LATERAL', 'Elevaciones laterales en polea', 3),
            ('EMPUJE', 'TRICEPS', 'Extensión de tríceps en polea alta', 3),
            ('EMPUJE', 'TRICEPS', 'Triceps katana', 3),
            ('TIRON', 'ESPALDA', 'Jalon al pecho agarre prono', 3),
            ('TIRON', 'ESPALDA', 'Remo sentado agarre prono', 3),
            ('TIRON', 'ESPALDA', 'Remo dorian', 3),
            ('TIRON', 'ESPALDA', 'Jalón al pecho agarre neutro', 3),
            ('TIRON', 'DELTOIDES POSTERIOR', 'Peck deck inverso', 3),
            ('TIRON', 'BICEPS', 'Curl de bíceps con mancuernas', 3),
            ('TIRON', 'BICEPS', 'Curl con barra', 3),
            ('PIERNA', 'ADUCTORES', 'Aductores en maquina', 3),
            ('PIERNA', 'CUADRICEPS', 'Prensa', 3),
            ('PIERNA', 'GLUTEOS', 'Hip thrust', 3),
            ('PIERNA', 'ISQUIOS', 'Curl de isquios sentado', 3),
            ('PIERNA', 'CUADRICEPS', 'Extension de cuadriceps', 3),
            ('PIERNA', 'ISQUIOS', 'Curl de isquios tumbado', 3),
            ('PIERNA', 'GEMELOS', 'Gemelos', 4),
            ('TORSO', 'PECTORAL', 'Press banca inclinado con mancuernas', 3),
            ('TORSO', 'PECTORAL', 'Press de pecho en maquina horizontal', 3),
            ('TORSO', 'ESPALDA', 'Remo en T', 3),
            ('TORSO', 'ESPALDA', 'Jalon al pecho agarre supino', 3),
            ('TORSO', 'DELTOIDES ANTERIOR', 'Press militar en multipower', 3),
            ('TORSO', 'DELTOIDES LATERAL', 'Elevaciones laterales en maquina', 3),
            ('TORSO', 'BICEPS', 'Curl con banco inclinado', 3),
            ('TORSO', 'TRICEPS', 'Extensión de tríceps unilateral', 3),
            ('ABDOMEN', 'ABDOMEN', 'Encogimientos en polea alta', 4),
            ('ABDOMEN', 'ABDOMEN', 'Elevaciones de pierna colgado', 4),
            ('ABDOMEN', 'ABDOMEN', 'Crunch abdominal en banco inclinado', 4)
        ]
        # PostgreSQL usa %s en lugar de ? para las variables
        c.executemany('INSERT INTO ejercicios (sesion, musculo, nombre, series) VALUES (%s, %s, %s, %s)', ejercicios)
        
    conn.commit()
    conn.close()

init_db()

# --- DISEÑO ---
BASE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gym Tracker Pro</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-color: #121212; --card-bg: #1e1e1e; --input-bg: #2c2c2c;
            --text-main: #ffffff; --text-muted: #aaaaaa;
            --accent: #ff4757; --success: #2ed573; --primary: #1e90ff; --warning: #ffa502;
        }
        body { font-family: -apple-system, sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 15px; }
        .container { max-width: 600px; margin: auto; padding-bottom: 80px; }
        
        .header { text-align: center; margin-bottom: 25px; }
        .header h1 { margin: 0; color: var(--primary); }
        .header p { color: var(--text-muted); margin-top: 5px; font-size: 14px; }

        .btn-sesion { display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 18px; margin-bottom: 12px; border-radius: 12px; background: var(--card-bg); border: 1px solid #333; color: white; font-size: 18px; font-weight: bold; text-decoration: none; box-sizing: border-box; }
        .btn-sesion.progreso { border-color: var(--warning); color: var(--warning); background: rgba(255, 165, 2, 0.1); margin-top: 30px; }
        
        .card-ejercicio { background: var(--card-bg); border-radius: 12px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.4); border-left: 4px solid var(--primary); }
        .ejercicio-titulo { font-size: 18px; font-weight: bold; margin-bottom: 5px; color: white; text-decoration: none; display: block; }
        .ejercicio-musculo { font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; }
        
        table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
        th { color: var(--text-muted); font-size: 12px; text-align: center; padding-bottom: 8px; font-weight: normal; }
        td { padding: 4px; text-align: center; }
        
        input[type="number"] { width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #444; background: var(--input-bg); color: white; text-align: center; font-size: 16px; box-sizing: border-box; }
        
        .btn-guardar { width: 100%; padding: 15px; border-radius: 12px; border: none; background: var(--success); color: white; font-size: 18px; font-weight: bold; cursor: pointer; position: fixed; bottom: 15px; left: 50%; transform: translateX(-50%); max-width: 570px; box-shadow: 0 4px 10px rgba(46, 213, 115, 0.4); }
        .btn-volver { display: inline-block; margin-bottom: 20px; color: var(--text-muted); text-decoration: none; }
        
        .ultimo-registro { font-size: 11px; color: var(--success); text-align: left; padding-left: 10px; margin-top: -5px; margin-bottom: 10px; display: block; }
        
        .grupo-musculo { margin-top: 20px; color: var(--primary); font-size: 14px; text-transform: uppercase; border-bottom: 1px solid #333; padding-bottom: 5px; }
        .link-progreso { display: block; padding: 12px; background: var(--card-bg); border-radius: 8px; margin-top: 8px; color: white; text-decoration: none; font-size: 15px; }
        .link-progreso:hover { background: #2c2c2c; }
        
        canvas { background: var(--card-bg); padding: 10px; border-radius: 10px; margin-top: 20px; }
    </style>
</head>
"""

# --- RUTAS DE LA APP ---

@app.route('/')
def index():
    html = BASE_HTML + """
    <body>
    <div class="container">
        <div class="header">
            <h1>Gym Tracker 🏋️‍♂️</h1>
            <p>Programa de Roberto Priego (Nube ☁️)</p>
        </div>
        <a href="/sesion/EMPUJE" class="btn-sesion"><span>💪 EMPUJE</span> <span>➔</span></a>
        <a href="/sesion/TIRON" class="btn-sesion"><span>🔙 TIRON</span> <span>➔</span></a>
        <a href="/sesion/PIERNA" class="btn-sesion"><span>🦵 PIERNA</span> <span>➔</span></a>
        <a href="/sesion/TORSO" class="btn-sesion"><span>🦍 TORSO</span> <span>➔</span></a>
        <a href="/sesion/ABDOMEN" class="btn-sesion"><span>🍫 ABDOMEN</span> <span>➔</span></a>
        
        <a href="/lista_progresos" class="btn-sesion progreso"><span>📈 VER PROGRESIONES</span> <span>➔</span></a>
    </div>
    </body></html>
    """
    return render_template_string(html)

@app.route('/sesion/<nombre>')
def sesion(nombre):
    conn = get_db()
    c = conn.cursor(cursor_factory=DictCursor)
    
    c.execute('SELECT * FROM ejercicios WHERE sesion = %s', (nombre,))
    ejercicios = c.fetchall()
    
    ultimos_registros = {}
    for ej in ejercicios:
        c.execute('SELECT serie, kg, reps FROM registros WHERE ejercicio_id = %s ORDER BY id DESC LIMIT %s', (ej['id'], ej['series']))
        regs = c.fetchall()
        if regs:
            regs_ordenados = sorted(regs, key=lambda x: x['serie'])
            ultimos_registros[ej['id']] = {r['serie']: f"{r['kg']}kg x {r['reps']} reps" for r in regs_ordenados}
            
    conn.close()
    
    html = BASE_HTML + """
    <body>
    <div class="container">
        <a href="/" class="btn-volver">← Volver al inicio</a>
        <div class="header">
            <h1>{{ nombre }}</h1>
            <p>Registra tus marcas de hoy</p>
        </div>
        
        <form method="POST" action="/guardar/{{ nombre }}">
            {% for ej in ejercicios %}
            <div class="card-ejercicio">
                <a href="/progreso/{{ ej['id'] }}" class="ejercicio-titulo">{{ ej['nombre'] }} 📈</a>
                <div class="ejercicio-musculo">{{ ej['musculo'] }}</div>
                
                <table>
                    <tr><th>Serie</th><th>KG</th><th>Reps</th><th>RIR</th></tr>
                    {% for i in range(1, ej['series'] + 1) %}
                    <tr>
                        <td style="color: #aaa; font-weight: bold;">{{ i }}</td>
                        <td><input type="number" step="0.25" name="kg_{{ ej['id'] }}_{{ i }}"></td>
                        <td><input type="number" name="reps_{{ ej['id'] }}_{{ i }}"></td>
                        <td><input type="number" name="rir_{{ ej['id'] }}_{{ i }}"></td>
                    </tr>
                    {% if ultimos_registros.get(ej['id']) and ultimos_registros[ej['id']].get(i) %}
                    <tr>
                        <td></td>
                        <td colspan="3"><span class="ultimo-registro">Última: {{ ultimos_registros[ej['id']][i] }}</span></td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </table>
            </div>
            {% endfor %}
            <button type="submit" class="btn-guardar">💾 Guardar Entrenamiento</button>
        </form>
    </div>
    </body></html>
    """
    return render_template_string(html, nombre=nombre, ejercicios=ejercicios, ultimos_registros=ultimos_registros)

@app.route('/guardar/<sesion_nombre>', methods=['POST'])
def guardar(sesion_nombre):
    conn = get_db()
    c = conn.cursor(cursor_factory=DictCursor)
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    c.execute('SELECT * FROM ejercicios WHERE sesion = %s', (sesion_nombre,))
    ejercicios = c.fetchall()
    
    for ej in ejercicios:
        for i in range(1, ej['series'] + 1):
            kg = request.form.get(f"kg_{ej['id']}_{i}")
            reps = request.form.get(f"reps_{ej['id']}_{i}")
            rir = request.form.get(f"rir_{ej['id']}_{i}")
            
            if kg and reps:
                c.execute('''
                    INSERT INTO registros (fecha, ejercicio_id, serie, kg, reps, rir)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (fecha_actual, ej['id'], i, float(kg), int(reps), int(rir) if rir else 0))
                
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/lista_progresos')
def lista_progresos():
    conn = get_db()
    c = conn.cursor(cursor_factory=DictCursor)
    c.execute('SELECT * FROM ejercicios ORDER BY sesion, nombre')
    ejercicios = c.fetchall()
    conn.close()
    
    agrupados = {}
    for ej in ejercicios:
        if ej['sesion'] not in agrupados:
            agrupados[ej['sesion']] = []
        agrupados[ej['sesion']].append(ej)
        
    html = BASE_HTML + """
    <body>
    <div class="container">
        <a href="/" class="btn-volver">← Volver al inicio</a>
        <div class="header">
            <h1 style="color: var(--warning);">Tus Progresiones</h1>
            <p>Selecciona un ejercicio para ver tu gráfica</p>
        </div>
        
        {% for sesion, lista in agrupados.items() %}
            <div class="grupo-musculo">{{ sesion }}</div>
            {% for ej in lista %}
                <a href="/progreso/{{ ej['id'] }}" class="link-progreso">{{ ej['nombre'] }} <span style="float:right;">📈</span></a>
            {% endfor %}
        {% endfor %}
    </div>
    </body></html>
    """
    return render_template_string(html, agrupados=agrupados)

@app.route('/progreso/<int:ejercicio_id>')
def ver_progreso(ejercicio_id):
    conn = get_db()
    c = conn.cursor(cursor_factory=DictCursor)
    c.execute('SELECT nombre, musculo FROM ejercicios WHERE id = %s', (ejercicio_id,))
    ejercicio = c.fetchone()
    
    # En PostgreSQL la función para extraer una parte del texto es SUBSTRING
    c.execute('''
        SELECT SUBSTRING(fecha, 1, 10) as dia, MAX(kg) as peso_maximo
        FROM registros
        WHERE ejercicio_id = %s AND kg > 0
        GROUP BY dia
        ORDER BY dia ASC
    ''', (ejercicio_id,))
    historial = c.fetchall()
    conn.close()
    
    fechas = [fila['dia'] for fila in historial]
    pesos = [fila['peso_maximo'] for fila in historial]
    
    html = BASE_HTML + """
    <body>
    <div class="container">
        <a href="javascript:history.back()" class="btn-volver">← Volver</a>
        <div class="header">
            <h1 style="font-size: 22px; color: var(--primary);">{{ ejercicio['nombre'] }}</h1>
            <p>Evolución de Peso Máximo (KG)</p>
        </div>
        
        {% if fechas|length < 2 %}
            <div style="text-align:center; margin-top: 50px; color: var(--text-muted);">
                <p style="font-size: 30px;">🏋️‍♂️</p>
                <p>Necesitas registrar este ejercicio al menos 2 días diferentes para ver tu gráfica de progreso.</p>
            </div>
        {% else %}
            <canvas id="graficoProgreso"></canvas>
            
            <script>
                const ctx = document.getElementById('graficoProgreso').getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: {{ fechas_json | safe }},
                        datasets: [{
                            label: 'KG Máximos Levantados',
                            data: {{ pesos_json | safe }},
                            borderColor: '#1e90ff',
                            backgroundColor: 'rgba(30, 144, 255, 0.2)',
                            borderWidth: 3,
                            pointBackgroundColor: '#ff4757',
                            pointRadius: 5,
                            fill: true,
                            tension: 0.3
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { ticks: { color: '#aaaaaa' }, grid: { color: '#333' } },
                            y: { 
                                ticks: { color: '#aaaaaa', stepSize: 2.5 }, 
                                grid: { color: '#333' },
                                beginAtZero: false
                            }
                        },
                        plugins: { legend: { labels: { color: '#ffffff' } } }
                    }
                });
            </script>
        {% endif %}
    </div>
    </body></html>
    """
    return render_template_string(html, ejercicio=ejercicio, fechas=fechas, fechas_json=json.dumps(fechas), pesos_json=json.dumps(pesos))

if __name__ == '__main__':
    app.run(debug=True)
