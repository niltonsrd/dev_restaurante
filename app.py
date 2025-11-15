import os
import sqlite3
from datetime import datetime
from flask import (
    Flask, render_template, g, jsonify,
    request, redirect, url_for, flash, send_from_directory
)
from werkzeug.utils import secure_filename

# -----------------------------------
# CONFIGURAÇÕES DO SISTEMA
# -----------------------------------

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'database.db')

UPLOAD_FOLDER_PRODUCTS = os.path.join(BASE_DIR, 'static', 'img')
UPLOAD_FOLDER_PIX = os.path.join(BASE_DIR, 'static', 'pix_comprovantes')

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
RESTAURANT_PHONE = os.environ.get('RESTAURANT_PHONE', '5571991118924')
# Opcional: se tiver domínio público, use SERVER_URL (ex: https://meusite.com)
SERVER_URL = os.environ.get('SERVER_URL', None)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

os.makedirs(UPLOAD_FOLDER_PRODUCTS, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_PIX, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')
app.config['UPLOAD_FOLDER_PRODUCTS'] = UPLOAD_FOLDER_PRODUCTS
app.config['UPLOAD_FOLDER_PIX'] = UPLOAD_FOLDER_PIX


# -----------------------------------
# BANCO DE DADOS (get_db usando g)
# -----------------------------------

def get_db():
    if '_database' not in g:
        # cria a pasta do DB se necessário
        db_dir = os.path.dirname(DB_PATH)
        os.makedirs(db_dir, exist_ok=True)
        g._database = sqlite3.connect(DB_PATH)
        g._database.row_factory = sqlite3.Row
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('_database', None)
    if db is not None:
        db.close()


# -----------------------------------
# UTILS
# -----------------------------------

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_pix_file(file_storage):
    """Salva o comprovante PIX em static/pix_comprovantes com nome único e retorna o filename salvo."""
    if not file_storage:
        return None
    filename = secure_filename(file_storage.filename)
    if filename == '':
        return None
    if not allowed_file(filename):
        return None
    name, ext = os.path.splitext(filename)
    ts = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    final = f"{name}_{ts}{ext}"
    dest = os.path.join(app.config['UPLOAD_FOLDER_PIX'], final)
    file_storage.save(dest)
    return final


def build_public_pix_url(filename):
    if not filename:
        return None
    base = SERVER_URL.rstrip('/') if SERVER_URL else request.host_url.rstrip('/')
    return f"{base}/pix/{filename}"


# -----------------------------------
# ROTAS PÚBLICAS
# -----------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/products')
def api_products():
    db = get_db()
    cur = db.execute("SELECT id, name, price, category, image, description FROM products ORDER BY category, name")
    rows = cur.fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/delivery-fees')
def api_delivery_fees():
    TAXAS = {
        'Bairro da Paz': 5.00,
        'Itapoã': 8.00,
        'Pituaçu': 7.00,
        'São Cristovão': 6.00,
        'Mussurunga': 6.00,
        'Outro': 10.00
    }
    return jsonify(TAXAS)



# -----------------------------------
# CHECKOUT (ENVIO PARA WHATSAPP)
# -----------------------------------

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    from flask import request
    import json
    from datetime import datetime

    # -------------------------------
    # Dados do cliente enviados pelo frontend
    # -------------------------------
    data = request.form

    customer_name = data.get('customer_name') or data.get('customerName') or data.get('name') or ''
    customer_address = data.get('customer_address') or data.get('customerAddress') or ''
    customer_contact = data.get('customer_contact') or data.get('customerContact') or ''
    customer_note = data.get('customer_note') or data.get('customerNote') or ''
    customer_bairro = (data.get('customer_bairro')
                       or data.get('customerBairro')
                       or data.get('bairro')
                       or '').strip()
    payment_method = (data.get('payment_method') or data.get('paymentMethod') or '').strip()
    troco_para = (data.get('troco_para') or data.get('trocoPara') or '').strip()

    cart_json = data.get('cart') or data.get('cart_json') or data.get('carrinho') or '[]'
    try:
        cart = json.loads(cart_json)
    except Exception:
        cart = []

    if not customer_name or not customer_address or not cart:
        return jsonify({'ok': False, 'error': 'Preencha todos os campos obrigatórios.'}), 400

    # -------------------------------
    # TAXA DE ENTREGA POR BAIRRO
    # -------------------------------
    TAXAS = {
        'Bairro da Paz': 5.00,
        'Itapoã': 8.00,
        'Pituaçu': 7.00,
        'São Cristovão': 6.00,
        'Mussurunga': 6.00,
        'Zona Sul': 12.00,   # Exemplo: adicione todos os bairros usados
        'Outro': 10.00
    }

    # Se o bairro não existir no dicionário, usar 'Outro'
    delivery_fee = TAXAS.get(customer_bairro, TAXAS['Outro'])

    # Se frontend enviar explicitamente delivery_tax, usar esse valor
    delivery_override = data.get('delivery_tax') or data.get('deliveryTax')
    if delivery_override:
        try:
            delivery_fee = float(delivery_override)
        except ValueError:
            pass

    # -------------------------------
    # Comprovante PIX
    # -------------------------------
    pix_filename = None
    pix_url = None
    if (payment_method or '').lower() == "pix" and 'pix_comprovante' in request.files:
        file = request.files['pix_comprovante']
        saved = save_pix_file(file)
        if saved:
            pix_filename = saved
            pix_url = build_public_pix_url(saved)
        else:
            return jsonify({'ok': False, 'error': 'Arquivo do comprovante inválido.'}), 400

    # -------------------------------
    # Montagem da mensagem para WhatsApp
    # -------------------------------
    lines = []
    lines.append("🧾 *Pedido - Dev Restaurante*")
    lines.append(f"👤 Cliente: {customer_name}")
    lines.append(f"📍 Endereço: {customer_address}")
    lines.append(f"🏙 Bairro: {customer_bairro or '—'}")
    if customer_contact:
        lines.append(f"📞 Contato: {customer_contact}")
    if customer_note:
        lines.append(f"📝 Obs: {customer_note}")

    lines.append("")
    lines.append(f"💳 *Pagamento:* {payment_method or '—'}")

    if payment_method.lower() == "dinheiro" and troco_para:
        # Normaliza o valor do troco
        raw = ''.join(ch for ch in troco_para if (ch.isdigit() or ch in ',.'))
        raw = raw.replace(',', '.')
        try:
            troco_val = float(raw)
            lines.append(f"Troco para: R$ {troco_val:.2f}")
        except Exception:
            lines.append(f"Troco para: {troco_para}")

    if payment_method.lower() == "pix":
        lines.append("💠 PIX enviado ✔")

    lines.append("")
    lines.append("🍔 *Itens:*")

    total = 0.0
    for it in cart:
        name = it.get('name') or it.get('nome') or 'Item'
        qty = int(it.get('qty') or it.get('qtd') or 1)
        price = float(it.get('price') or it.get('preco') or 0.0)
        subtotal = qty * price
        total += subtotal
        lines.append(f"- {qty}x {name} — R$ {subtotal:.2f}")

    # Taxa de entrega
    lines.append("")
    lines.append(f"🚚 Entrega: R$ {delivery_fee:.2f}")

    total_final = total + delivery_fee
    lines.append(f"💰 *Total:* R$ {total_final:.2f}")

    if pix_url:
        lines.append("")
        lines.append(f"📎 Comprovante PIX: {pix_url}")

    lines.append("")
    lines.append("📨 Pedido enviado via site Dev Restaurante.")

    text = "%0A".join(lines)
    url = f"https://api.whatsapp.com/send?phone={RESTAURANT_PHONE}&text={text}"

    return jsonify({
        'ok': True,
        'whatsapp_url': url,
        'pix_file': pix_filename,
        'pix_url': pix_url
    })




# DOWNLOAD DO COMPROVANTE PIX
@app.route('/pix/<filename>')
def get_pix_file(filename):
    return send_from_directory(UPLOAD_FOLDER_PIX, filename)


# -----------------------------------
# ADMIN
# -----------------------------------

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Login
    if request.method == 'POST':
        password = request.form.get('password', '')

        if password == ADMIN_PASSWORD:
            response = redirect(url_for('admin'))
            response.set_cookie(
                'admin_auth',
                '1',
                max_age=3600,
                httponly=True,
                samesite='Strict'
            )
            return response

        flash("Senha incorreta", "error")
        return redirect(url_for('admin'))

    # Verifica cookie (se está logado)
    is_admin = request.cookies.get('admin_auth') == '1'

    # Se NÃO estiver logado → manda admin=False
    if not is_admin:
        return render_template("admin.html", admin=False, products=[])

    # Se estiver logado → manda admin=True
    db = get_db()
    products = db.execute("SELECT * FROM products ORDER BY id").fetchall()

    return render_template("admin.html", admin=True, products=products)

from flask import session, redirect, url_for

@app.route('/admin/logout', methods=['GET', 'POST'])
def admin_logout():
    # Remove o cookie de login
    response = redirect(url_for('index'))  # redireciona para o cardápio
    response.set_cookie('admin_auth', '', expires=0)  # apaga o cookie
    return response

 # substitua 'cardapio' pelo nome da função da página do cardápio





# adicionar produto
@app.route('/admin/add', methods=['POST'])
def admin_add():
    if request.cookies.get('admin_auth') != '1':
        flash("Acesso negado", "error")
        return redirect(url_for('admin'))

    name = request.form.get('name')
    price = request.form.get('price')
    category = request.form.get('category')
    description = request.form.get('description')

    file = request.files.get('image')
    filename = None

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # adicionar timestamp para evitar sobrescrita
        name_only, ext = os.path.splitext(filename)
        ts = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        filename = f"{name_only}_{ts}{ext}"
        file.save(os.path.join(UPLOAD_FOLDER_PRODUCTS, filename))

    db = get_db()
    db.execute("""
        INSERT INTO products (name, price, category, image, description)
        VALUES (?, ?, ?, ?, ?)
    """, (name, price, category, filename, description))
    db.commit()

    flash("Produto adicionado!", "success")
    return redirect(url_for('admin'))


# deletar produto
@app.route('/admin/delete/<int:id>', methods=['POST'])
def admin_delete(id):
    if request.cookies.get('admin_auth') != '1':
        flash("Acesso negado", "error")
        return redirect(url_for('admin'))

    db = get_db()
    db.execute("DELETE FROM products WHERE id=?", (id,))
    db.commit()

    flash("Produto removido.", "success")
    return redirect(url_for('admin'))


# editar produto
@app.route('/admin/edit/<int:id>', methods=['POST'])
def admin_edit(id):
    if request.cookies.get('admin_auth') != '1':
        flash("Acesso negado", "error")
        return redirect(url_for('admin'))

    name = request.form.get('name')
    price = request.form.get('price')
    category = request.form.get('category')
    description = request.form.get('description')

    file = request.files.get('image')
    filename = None

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        name_only, ext = os.path.splitext(filename)
        ts = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        filename = f"{name_only}_{ts}{ext}"
        file.save(os.path.join(UPLOAD_FOLDER_PRODUCTS, filename))

    db = get_db()
    if filename:
        db.execute("""
            UPDATE products SET name=?, price=?, category=?, image=?, description=? WHERE id=?
        """, (name, price, category, filename, description, id))
    else:
        db.execute("""
            UPDATE products SET name=?, price=?, category=?, description=? WHERE id=?
        """, (name, price, category, description, id))

    db.commit()

    flash("Produto atualizado!", "success")
    return redirect(url_for('admin'))


# -----------------------------------
# RUN
# -----------------------------------

if __name__ == '__main__':
    # cria DB se não existir
    init_db_path = os.path.join(BASE_DIR, 'database', 'database.db')
    if not os.path.exists(init_db_path):
        try:
            from database.init_db import init_db
            init_db()
        except Exception:
            # se não houver módulo init_db, apenas garante pasta
            os.makedirs(os.path.dirname(init_db_path), exist_ok=True)

    app.run(host='0.0.0.0', port=5000, debug=True)
