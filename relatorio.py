from flask import Flask, render_template_string, request, redirect, url_for
import json
from datetime import datetime
from pyngrok import ngrok

ARQUIVO = "dados.json"
app = Flask(__name__)


def carregar_dados():
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def salvar_dados(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def parse_int(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return 0


def registrar_culto(culto, data, dia_semana, meninas, meninos, visitantes, tios):
    total = meninas + meninos + visitantes + tios
    registro = {
        "culto": culto,
        "data": data,
        "dia_semana": dia_semana,
        "quantidades": {
            "Meninas": meninas,
            "Meninos": meninos,
            "Visitantes": visitantes,
            "Tios": tios,
        },
        "total": total,
        "timestamp": datetime.now().isoformat()
    }
    dados = carregar_dados()
    dados.append(registro)
    salvar_dados(dados)
    return registro


def gerar_relatorio_diario(data_consulta):
    dados = carregar_dados()
    registros_dia = [d for d in dados if d["data"] == data_consulta]
    totals = {"Meninas": 0, "Meninos": 0, "Visitantes": 0, "Tios": 0, "Total": 0}

    for r in registros_dia:
        for k, v in r["quantidades"].items():
            totals[k] += v
        totals["Total"] += r["total"]

    return registros_dia, totals


def gerar_relatorio_mensal(mes_ano):
    dados = carregar_dados()
    registros_mes = []
    for d in dados:
        try:
            dt = datetime.strptime(d["data"], "%d/%m/%Y")
            if dt.strftime("%m/%Y") == mes_ano:
                registros_mes.append(d)
        except ValueError:
            continue

    totals = {"Meninas": 0, "Meninos": 0, "Visitantes": 0, "Tios": 0, "Total": 0}
    for r in registros_mes:
        for k, v in r["quantidades"].items():
            totals[k] += v
        totals["Total"] += r["total"]

    return registros_mes, totals


def excluir_registro(index):
    dados = carregar_dados()
    if 0 <= index < len(dados):
        dados.pop(index)
        salvar_dados(dados)
        return True
    return False


PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Controle de Frequência - Igreja</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Poppins', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: #2d3748; margin: 0; padding: 0; }
        .header { background: rgba(255,255,255,0.95); padding: 20px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .header h1 { color: #5a67d8; font-size: 28px; font-weight: 700; }
        .header p { color: #718096; font-size: 14px; margin-top: 4px; }
        .page { max-width: 900px; margin: 24px auto; padding: 0 16px 24px; }
        .card { background: #fff; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); padding: 24px; }
        .card h2 { color: #2d3748; font-size: 20px; margin-bottom: 20px; font-weight: 600; }
        .topbar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; justify-content: center; }
        .topbar a { padding: 12px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; border-radius: 12px; text-decoration: none; font-size: 14px; font-weight: 500; transition: transform 0.2s, box-shadow 0.2s; }
        .topbar a:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102,126,234,0.4); }
        label { display: block; margin-top: 16px; font-weight: 500; font-size: 14px; color: #4a5568; }
        input, select { width: 100%; padding: 14px 16px; border: 2px solid #e2e8f0; border-radius: 12px; margin-top: 6px; box-sizing: border-box; font-size: 16px; font-family: 'Poppins', sans-serif; transition: border-color 0.2s; }
        input:focus, select:focus { outline: none; border-color: #667eea; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 8px; }
        button { margin-top: 20px; padding: 16px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; border: none; border-radius: 12px; cursor: pointer; font-size: 16px; font-weight: 600; width: 100%; transition: transform 0.2s, box-shadow 0.2s; }
        button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102,126,234,0.4); }
        .info { margin-top: 20px; padding: 16px 20px; border-radius: 12px; background: #f7fafc; border-left: 4px solid #667eea; }
        .info strong { color: #2d3748; }
        .table-wrap { overflow-x: auto; margin-top: 20px; -webkit-overflow-scrolling: touch; border-radius: 12px; }
        table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 12px; overflow: hidden; }
        th, td { text-align: left; padding: 14px 12px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }
        th { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; font-weight: 600; }
        tr:hover { background: #f7fafc; }
        
        /* Mobile adjustments */
        @media (max-width: 600px) {
            .page { margin: 12px auto; padding: 12px; }
            .card { padding: 16px; border-radius: 12px; }
            h1 { font-size: 20px; }
            .topbar { gap: 6px; }
            .topbar a { padding: 8px 12px; font-size: 13px; flex: 1; text-align: center; min-width: 80px; }
            .grid { grid-template-columns: 1fr; gap: 10px; }
            label { font-size: 13px; margin-top: 12px; }
            input, select { padding: 10px 12px; font-size: 16px; }
            button { padding: 12px 16px; font-size: 15px; }
            .info { padding: 12px 14px; font-size: 13px; }
            table { font-size: 13px; }
            th, td { padding: 8px 6px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⛪ Controle de Frequência</h1>
        <p>Registro de presença nos cultos</p>
    </div>
    <div class="page">
        <div class="card">
            <h2>Registrar culto</h2>
            <div class="topbar">
                <a href="/">📝 Registrar</a>
                <a href="/relatorio_diario">📊 Diário</a>
                <a href="/relatorio_mensal">📈 Mensal</a>
            </div>
            <form method="post" action="/">
                <label for="culto">Nome do culto</label>
                <input id="culto" name="culto" type="text" value="{{ culto }}" required>
                <label for="data">Data (dd/mm/aaaa)</label>
                <input id="data" name="data" type="text" value="{{ data }}" required>
                <label for="dia_semana">Dia da semana</label>
                <select id="dia_semana" name="dia_semana">
                    <option value="segunda-feira" {% if dia_semana == 'segunda-feira' %}selected{% endif %}>Segunda-feira</option>
                    <option value="terça-feira" {% if dia_semana == 'terça-feira' %}selected{% endif %}>Terça-feira</option>
                    <option value="quarta-feira" {% if dia_semana == 'quarta-feira' %}selected{% endif %}>Quarta-feira</option>
                    <option value="quinta-feira" {% if dia_semana == 'quinta-feira' %}selected{% endif %}>Quinta-feira</option>
                    <option value="sexta-feira" {% if dia_semana == 'sexta-feira' %}selected{% endif %}>Sexta-feira</option>
                    <option value="sábado" {% if dia_semana == 'sábado' %}selected{% endif %}>Sábado</option>
                    <option value="domingo" {% if dia_semana == 'domingo' %}selected{% endif %}>Domingo</option>
                </select>
                <div class="grid">
                    <div>
                        <label for="meninas">Meninas</label>
                        <input id="meninas" name="meninas" type="number" min="0" value="{{ meninas }}">
                    </div>
                    <div>
                        <label for="meninos">Meninos</label>
                        <input id="meninos" name="meninos" type="number" min="0" value="{{ meninos }}">
                    </div>
                    <div>
                        <label for="visitantes">Visitantes</label>
                        <input id="visitantes" name="visitantes" type="number" min="0" value="{{ visitantes }}">
                    </div>
                    <div>
                        <label for="tios">Tios</label>
                        <input id="tios" name="tios" type="number" min="0" value="{{ tios }}">
                    </div>
                </div>
                <button type="submit">Salvar registro</button>
            </form>
            {% if message %}
            <div class="info">{{ message }}</div>
            {% endif %}
            <div class="info">
                <strong>Últimos registros:</strong>
                {% if registros %}
                    <div class="table-wrap">
                        <table>
                            <thead>
                                <tr><th>Data</th><th>Culto</th><th>Dia</th><th>Total</th><th>Ação</th></tr>
                            </thead>
                            <tbody>
                                {% for r in registros %}
                                <tr>
                                    <td>{{ r.data }}</td>
                                    <td>{{ r.culto }}</td>
                                    <td>{{ r.dia_semana }}</td>
                                    <td>{{ r.total }}</td>
                                    <td>
                                        <form method="post" action="/excluir/{{ r.timestamp }}" style="display:inline;">
                                            <button type="submit" style="background:#e74c3c; padding:6px 10px; font-size:12px;" onclick="return confirm('Tem certeza que deseja excluir este registro?')">Excluir</button>
                                        </form>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                {% else %}
                    <p>Nenhum registro encontrado.</p>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
"""

REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Igreja</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Poppins', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: #2d3748; }
        .header { background: rgba(255,255,255,0.95); padding: 20px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .header h1 { color: #5a67d8; font-size: 28px; font-weight: 700; }
        .header p { color: #718096; font-size: 14px; margin-top: 4px; }
        .page { max-width: 980px; margin: 24px auto; padding: 0 16px 24px; }
        .card { background: #fff; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); padding: 24px; }
        .card h2 { color: #2d3748; font-size: 20px; margin-bottom: 20px; font-weight: 600; }
        .topbar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; justify-content: center; }
        .topbar a { padding: 12px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; border-radius: 12px; text-decoration: none; font-size: 14px; font-weight: 500; transition: transform 0.2s, box-shadow 0.2s; }
        .topbar a:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102,126,234,0.4); }
        .grid { display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-end; }
        label { display: block; margin-bottom: 8px; font-weight: 500; font-size: 14px; color: #4a5568; }
        input, button { padding: 14px 16px; border-radius: 12px; border: 2px solid #e2e8f0; font-size: 16px; font-family: 'Poppins', sans-serif; }
        input { width: 220px; transition: border-color 0.2s; }
        input:focus { outline: none; border-color: #667eea; }
        button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; cursor: pointer; font-weight: 600; transition: transform 0.2s, box-shadow 0.2s; }
        button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102,126,234,0.4); }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #fff; border-radius: 12px; overflow: hidden; }
        th, td { border: 1px solid #e2e8f0; padding: 14px 12px; font-size: 14px; }
        th { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; font-weight: 600; }
        tr:hover { background: #f7fafc; }
        .totals { margin-top: 20px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: #fff; }
        .totals p { margin: 8px 0; font-size: 15px; }
        .totals strong { font-weight: 600; }
        
        /* Mobile adjustments */
        @media (max-width: 600px) {
            .page { margin: 12px auto; padding: 0 12px 12px; }
            .card { padding: 16px; border-radius: 16px; }
            h1 { font-size: 20px; }
            .topbar { gap: 6px; }
            .topbar a { padding: 10px 14px; font-size: 12px; flex: 1; text-align: center; min-width: 70px; }
            .grid { flex-direction: column; gap: 12px; }
            input { width: 100%; }
            button { width: 100%; }
            .totals { padding: 14px; font-size: 13px; }
            table { font-size: 12px; }
            th, td { padding: 10px 6px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⛪ Controle de Frequência</h1>
        <p>Registro de presença nos cultos</p>
    </div>
    <div class="page">
        <div class="card">
            <h2>{{ title }}</h2>
            <div class="topbar">
                <a href="/">📝 Registrar</a>
                <a href="/relatorio_diario">📊 Diário</a>
                <a href="/relatorio_mensal">📈 Mensal</a>
            </div>
        .topbar a { padding: 10px 16px; background: #2f4cd4; color: #fff; border-radius: 10px; text-decoration: none; }
        .grid { display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-end; }
        label { display: block; margin-bottom: 6px; font-weight: bold; }
        input, button { padding: 12px 14px; border-radius: 10px; border: 1px solid #d4dbea; }
        input { width: 220px; }
        button { background: #2f4cd4; color: white; border: none; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; margin-top: 18px; }
        th, td { border: 1px solid #e7ecf5; padding: 12px; }
        th { background: #f4f8ff; }
        .totals { margin-top: 20px; padding: 18px; background: #f4f8ff; border-radius: 12px; }
    </style>
</head>
<body>
    <div class="page">
        <div class="card">
            <div class="topbar">
                <a href="/">Registrar</a>
                <a href="/relatorio_diario">Relatório Diário</a>
                <a href="/relatorio_mensal">Relatório Mensal</a>
            </div>
            <h2>{{ title }}</h2>
            <div class="topbar">
                <a href="/">📝 Registrar</a>
                <a href="/relatorio_diario">📊 Diário</a>
                <a href="/relatorio_mensal">📈 Mensal</a>
            </div>
            <form class="grid" method="get" action="{{ url }}">
                {% if period == 'daily' %}
                    <div>
                        <label for="data">Data</label>
                        <input id="data" name="data" type="text" value="{{ selected }}" placeholder="dd/mm/aaaa" />
                    </div>
                {% else %}
                    <div>
                        <label for="mes_ano">Mês/Ano</label>
                        <input id="mes_ano" name="mes_ano" type="text" value="{{ selected }}" placeholder="mm/aaaa" />
                    </div>
                {% endif %}
                <button type="submit">Gerar relatório</button>
            </form>
            {% if registros is not none %}
                <div class="totals">
                    <p><strong>Registros:</strong> {{ registros|length }}</p>
                    <p><strong>Total geral:</strong> {{ totals.Total }}</p>
                    <p><strong>Meninas:</strong> {{ totals.Meninas }}</p>
                    <p><strong>Meninos:</strong> {{ totals.Meninos }}</p>
                    <p><strong>Visitantes:</strong> {{ totals.Visitantes }}</p>
                    <p><strong>Tios:</strong> {{ totals.Tios }}</p>
                </div>
                <table>
                    <thead>
                        <tr><th>Data</th><th>Culto</th><th>Dia</th><th>Meninas</th><th>Meninos</th><th>Visitantes</th><th>Tios</th><th>Total</th><th>Ação</th></tr>
                    </thead>
                    <tbody>
                        {% for r in registros %}
                        <tr>
                            <td>{{ r.data }}</td>
                            <td>{{ r.culto }}</td>
                            <td>{{ r.dia_semana }}</td>
                            <td>{{ r.quantidades.Meninas }}</td>
                            <td>{{ r.quantidades.Meninos }}</td>
                            <td>{{ r.quantidades.Visitantes }}</td>
                            <td>{{ r.quantidades.Tios }}</td>
                            <td>{{ r.total }}</td>
                            <td>
                                <form method="post" action="/excluir/{{ r.timestamp }}" style="display:inline;">
                                    <button type="submit" style="background:#e74c3c; padding:6px 10px; font-size:12px;" onclick="return confirm('Tem certeza que deseja excluir este registro?')">Excluir</button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    if request.method == 'POST':
        culto = request.form.get('culto', '').strip()
        data = request.form.get('data', '').strip()
        dia_semana = request.form.get('dia_semana', '').strip()
        meninas = parse_int(request.form.get('meninas', 0))
        meninos = parse_int(request.form.get('meninos', 0))
        visitantes = parse_int(request.form.get('visitantes', 0))
        tios = parse_int(request.form.get('tios', 0))

        if not culto or not data:
            message = 'Informe o nome do culto e a data.'
        else:
            registrar_culto(culto, data, dia_semana, meninas, meninos, visitantes, tios)
            message = 'Registro salvo com sucesso.'

    dados = carregar_dados()
    registros = list(reversed(dados[-8:]))

    return render_template_string(
        PAGE_TEMPLATE,
        culto="",
        data=datetime.now().strftime('%d/%m/%Y'),
        dia_semana='segunda-feira',
        meninas=0,
        meninos=0,
        visitantes=0,
        tios=0,
        registros=registros,
        message=message
    )


@app.route('/relatorio_diario', methods=['GET'])
def relatorio_diario_view():
    data = request.args.get('data', datetime.now().strftime('%d/%m/%Y'))
    registros, totals = gerar_relatorio_diario(data)
    return render_template_string(
        REPORT_TEMPLATE,
        title='Relatório Diário',
        url=url_for('relatorio_diario_view'),
        period='daily',
        selected=data,
        registros=registros,
        totals=totals
    )


@app.route('/relatorio_mensal', methods=['GET'])
def relatorio_mensal_view():
    selected = request.args.get('mes_ano', datetime.now().strftime('%m/%Y'))
    registros, totals = gerar_relatorio_mensal(selected)
    return render_template_string(
        REPORT_TEMPLATE,
        title='Relatório Mensal',
        url=url_for('relatorio_mensal_view'),
        period='monthly',
        selected=selected,
        registros=registros,
        totals=totals
    )


@app.route('/excluir/<path:timestamp>', methods=['POST'])
def excluir_registro_view(timestamp):
    dados = carregar_dados()
    dados = [d for d in dados if d.get('timestamp') != timestamp]
    salvar_dados(dados)
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Configurar o authtoken do ngrok
    ngrok.set_auth_token("3ClqFuQJUsIgWf7LBqA9jHyc6JG_5GvV15Z3QRGoXthmDeeCq")
    
    # Iniciar túnel público com ngrok
    public_url = ngrok.connect(5000)
    print(f"App rodando localmente em http://127.0.0.1:5000/")
    print(f"Link público para compartilhar: {public_url}")
    print("Pressione Ctrl+C para parar.")

    # Desabilitar o reloader do Flask para evitar conflito com ngrok
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)

