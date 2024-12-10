from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) # Gerador de uma chave aleatória

# Configuração do banco de dados
def init_sqlite_db():
    conn = sqlite3.connect('database.db')
    print("Banco de dados aberto com sucesso")
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS products (name TEXT, quantity INTEGER)')
    print("Tabelas criadas com sucesso")
    conn.close()

init_sqlite_db()

@app.route('/')
def login():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['loginUsername']
    password = request.form['loginPassword']
    
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
    
    if user:
        session['logged_in'] = True
        return redirect(url_for('estoques'))
    else:
        return "Nome de usuário ou senha incorretos. Tente novamente."

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['signupUsername']
        password = request.form['signupPassword']
        
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            con.commit()
        
        return redirect(url_for('login'))
    
    return render_template('cadastro.html')

@app.route('/estoques', methods=['GET', 'POST'])
def estoques():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        product_name = request.form['productName']
        product_quantity = request.form['productQuantity']

        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("INSERT INTO products (name, quantity) VALUES (?, ?)", (product_name, product_quantity))
            con.commit()

    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("SELECT name, quantity FROM products")
        products = cur.fetchall()

    return render_template('estoques.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    product_name = request.form['productName']
    product_quantity = request.form['productQuantity']

    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("INSERT INTO products (name, quantity) VALUES (?, ?)", (product_name, product_quantity))
        con.commit()

    new_product_id = cur.lastrowid
    return jsonify({'id': new_product_id, 'name': product_name, 'quantity': product_quantity})


@app.route('/get_products', methods=['GET'])
def get_products():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("SELECT rowid, name, quantity FROM products")
        products = cur.fetchall()
    return jsonify(products)

@app.route('/update_quantity/<int:product_id>/<int:delta>', methods=['POST'])
def update_quantity(product_id, delta):
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("UPDATE products SET quantity = quantity + ? WHERE rowid = ?", (delta, product_id))
        con.commit()
    return '', 204

@app.route('/delete_product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("DELETE FROM products WHERE rowid = ?", (product_id,))
        con.commit()
    return '', 204

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)