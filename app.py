from flask import Flask, render_template, request, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta'

class ProcuracaoForm(FlaskForm):
    nome_cliente = StringField('Nome do Cliente', validators=[DataRequired()])
    cpf_cliente = StringField('CPF do Cliente', validators=[DataRequired()])
    rg_cliente = StringField('RG do Cliente', validators=[DataRequired()])
    endereco_cliente = StringField('Endereço do Cliente', validators=[DataRequired()])
    cep_cliente = StringField('CEP do Cliente', validators=[DataRequired()])
    nome_procurador = StringField('Nome do Procurador', validators=[DataRequired()])
    cpf_procurador = StringField('CPF do Procurador', validators=[DataRequired()])
    submit = SubmitField('Gerar PDF')

def draw_text(canvas, text, x, y, max_width, line_height):
    lines = []
    line = ''
    for word in text.split():
        if canvas.stringWidth(line + word) <= max_width:
            line += word + ' '
        else:
            lines.append(line)
            line = word + ' '
    lines.append(line)

    for line in lines:
        canvas.drawString(x, y, line)
        y -= line_height

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ProcuracaoForm()
    if form.validate_on_submit():
        nome_cliente = form.nome_cliente.data
        cpf_cliente = form.cpf_cliente.data
        rg_cliente = form.rg_cliente.data
        endereco_cliente = form.endereco_cliente.data
        cep_cliente = form.cep_cliente.data
        nome_procurador = form.nome_procurador.data
        cpf_procurador = form.cpf_procurador.data
        data_atual = datetime.now().strftime('%d/%m/%Y')
        validade = (datetime.now() + timedelta(days=365)).strftime('%d/%m/%Y')  # Adicionando 1 ano à data atual

        # Gerar o PDF
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        texto = f"Por este instrumento particular de procuração, eu {nome_cliente}, Brasileira, portador do CPF de número {cpf_cliente} e cédula de Identidade de número {rg_cliente}, expedida pela ITEP/RN, residente e domiciliados {endereco_cliente}, CEP: {cep_cliente}, nomeio e constituo meu bastante procurador o {nome_procurador}, brasileiro, portador do CPF de número {cpf_procurador}, residente na Rua Rianápolis, Nº 13, Neópolis, na cidade de Natal/RN, CEP 59088-350, para processos junto à COSERN, a quem concedo poderes para assinar documentos, podendo, inclusive, substabelecer."
        draw_text(pdf, texto, 50, 750, 500, 15)
        pdf.drawString(50, 580, f"A presente procuração terá validade até o dia {validade}")
        pdf.drawString(50, 560, f"NATAL, {data_atual}")
        pdf.drawString(50, 500, " " * 10 + "_" * 45)
        pdf.save()

        buffer.seek(0)
        return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f"procuracao_{nome_cliente}.pdf")

    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
