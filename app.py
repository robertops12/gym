from flask import Flask, request, render_template_string

app = Flask(__name__)

# Esta lista guardará los datos de todos los amigos
amigos = []

# Diseño de la aplicación (Modo noche / Fiesta)
HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nivel de Fiesta de los Colegas 🍻</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #1e1e2f; color: white; text-align: center; padding: 20px; }
        .container { background: #2a2a40; max-width: 500px; margin: auto; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.5); }
        input, select, button { width: 90%; margin: 10px 0; padding: 10px; border-radius: 5px; border: none; font-size: 16px; box-sizing: border-box; }
        input, select { background-color: #3e3e5c; color: white; }
        button { background-color: #2ed573; color: white; font-weight: bold; cursor: pointer; margin-top: 15px; }
        button:hover { background-color: #26b360; }
        
        .btn-borrar { background-color: #ff4757; }
        .btn-borrar:hover { background-color: #ff6b81; }

        .lista-amigos { margin-top: 30px; text-align: left; }
        .amigo-card { background: #3e3e5c; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 6px solid #ccc; }
        
        .estado-Sobrio { border-color: #2ed573; }
        .estado-Puntillo { border-color: #1e90ff; }
        .estado-Borracho { border-color: #ffa502; }
        .estado-Ebrio { border-color: #ff4757; }
        
        h3 { border-bottom: 1px solid #555; padding-bottom: 10px; }
        .zona-reset { margin-top: 40px; padding: 15px; background-color: #222233; border-radius: 8px; border: 1px dashed #555; }
    </style>
</head>
<body>

<div class="container">
    <h2>Muro de la Fiesta 🍻</h2>
    <p>Apunta lo que llevas y elige tu estado.</p>

    <form method="POST">
        <input type="hidden" name="accion" value="actualizar">
        
        <label>Tu Nombre:</label>
        <input type="text" name="nombre" required placeholder="Ej. Juan">

        <label>🍺 Cervezas:</label>
        <input type="number" name="cervezas" value="0" min="0">

        <label>🍹 Cubatas:</label>
        <input type="number" name="cubatas" value="0" min="0">

        <label>🥃 Chupitos:</label>
        <input type="number" name="chupitos" value="0" min="0">

        <label>¿Cómo te sientes ahora mismo?:</label>
        <select name="estado">
            <option value="Sobrio">Fresquísimo / Sobrio 💧</option>
            <option value="Puntillo">Con el puntillo alegre 🕺</option>
            <option value="Borracho">Borracho / Perdiendo los papeles 🥴</option>
            <option value="Ebrio">Ebrio Extremo / En la miseria 💀</option>
        </select>

        <button type="submit">¡Actualizar mi estado!</button>
    </form>

    <div class="lista-amigos">
        <h3>Niveles de la gente:</h3>
        {% if amigos|length == 0 %}
            <p style="text-align: center; color: #aaa;">Aún nadie ha apuntado nada. ¡Sé el primero!</p>
        {% else %}
            {% for amigo in amigos %}
            <div class="amigo-card estado-{{ amigo.estado }}">
                <strong style="font-size: 1.2em;">{{ amigo.nombre }}</strong> se siente <em>{{ amigo.estado }}</em><br>
                <span style="color: #bbb; font-size: 0.9em;">Ha bebido: {{ amigo.cervezas }} 🍺 | {{ amigo.cubatas }} 🍹 | {{ amigo.chupitos }} 🥃</span>
            </div>
            {% endfor %}
        {% endif %}
    </div>

    <div class="zona-reset">
        <h4>Resetear la Fiesta 🧹</h4>
        <form method="POST" style="display: flex; flex-direction: column; align-items: center;">
            <input type="hidden" name="accion" value="resetear">
            <input type="password" name="password" placeholder="Contraseña..." required style="width: 80%;">
            <button type="submit" class="btn-borrar" style="width: 80%;">Borrar Lista</button>
        </form>
        {% if error %}
            <p style="color: #ff4757; font-size: 14px; margin-top: 10px;">{{ error }}</p>
        {% endif %}
    </div>
</div>

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    mensaje_error = ""

    if request.method == 'POST':
        accion = request.form.get('accion')

        # Si el usuario le ha dado al botón de Resetear
        if accion == 'resetear':
            password = request.form.get('password')
            # AQUÍ PUEDES CAMBIAR LA CONTRASEÑA
            if password == '1234':
                amigos.clear()
            else:
                mensaje_error = "Contraseña incorrecta ❌"

        # Si el usuario está añadiendo sus datos
        elif accion == 'actualizar':
            nombre = request.form.get('nombre')
            cervezas = int(request.form.get('cervezas', 0))
            cubatas = int(request.form.get('cubatas', 0))
            chupitos = int(request.form.get('chupitos', 0))
            estado = request.form.get('estado')

            encontrado = False
            for amigo in amigos:
                if amigo['nombre'].lower() == nombre.lower():
                    amigo['cervezas'] = cervezas
                    amigo['cubatas'] = cubatas
                    amigo['chupitos'] = chupitos
                    amigo['estado'] = estado
                    encontrado = True
                    break
            
            if not encontrado:
                amigos.append({
                    'nombre': nombre,
                    'cervezas': cervezas,
                    'cubatas': cubatas,
                    'chupitos': chupitos,
                    'estado': estado
                })

    return render_template_string(HTML, amigos=amigos, error=mensaje_error)

if __name__ == '__main__':
    app.run(debug=True)