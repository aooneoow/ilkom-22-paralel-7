from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secretkey123'

@app.template_filter('rupiah')
def rupiah_format(value):
    try:
        value = int(value)
        return f"{value:,}".replace(",", ".")
    except:
        return value

# ------------------------- DATABASE -------------------------
def get_db():
    conn = sqlite3.connect('kas.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    # Tabel user
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT)''')

    # Tabel kas masuk
    conn.execute('''CREATE TABLE IF NOT EXISTS kas_masuk (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT,
                    keterangan TEXT,
                    nominal INTEGER)''')

    # Tabel kas keluar
    conn.execute('''CREATE TABLE IF NOT EXISTS kas_keluar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT,
                    keterangan TEXT,
                    nominal INTEGER)''')

    # Admin default
    user = conn.execute("SELECT * FROM users WHERE username='admin'").fetchone()
    if not user:
        conn.execute("INSERT INTO users(username, password) VALUES('admin','admin')")

    conn.commit()

init_db()

# ------------------------- ROUTES -------------------------

# LOGIN PAGE
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE username=? AND password=?',
        (username, password)
    ).fetchone()

    if user:
        session['user'] = username
        return redirect('/dashboard')
    else:
        flash("Username atau password salah!", "error")
        return redirect('/')

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    conn = get_db()

    # Total kas masuk
    masuk = conn.execute('SELECT SUM(nominal) AS total FROM kas_masuk').fetchone()['total']
    masuk = masuk if masuk else 0

    # Total kas keluar
    keluar = conn.execute('SELECT SUM(nominal) AS total FROM kas_keluar').fetchone()['total']
    keluar = keluar if keluar else 0

    saldo = masuk - keluar

    return render_template('dashboard.html', masuk=masuk, keluar=keluar, saldo=saldo)

# ------------------- KAS MASUK -------------------
@app.route('/kas_masuk')
def kas_masuk():
    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    data = conn.execute('SELECT * FROM kas_masuk ORDER BY id DESC').fetchall()
    return render_template('kas_masuk.html', data=data)

@app.route('/kas_masuk/tambah', methods=['POST'])
def tambah_masuk():
    if 'user' not in session:
        return redirect('/')

    tanggal = datetime.now().strftime('%Y-%m-%d')
    keterangan = request.form['keterangan']
    nominal = request.form['nominal']

    if not keterangan or not nominal:
        flash("Semua field harus diisi!", "error")
        return redirect('/kas_masuk')

    conn = get_db()
    conn.execute(
        'INSERT INTO kas_masuk(tanggal, keterangan, nominal) VALUES (?,?,?)',
        (tanggal, keterangan, nominal)
    )
    conn.commit()
    return redirect('/kas_masuk')

# ------------------- KAS KELUAR -------------------
@app.route('/kas_keluar')
def kas_keluar():
    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    data = conn.execute('SELECT * FROM kas_keluar ORDER BY id DESC').fetchall()
    return render_template('kas_keluar.html', data=data)

@app.route('/kas_keluar/tambah', methods=['POST'])
def tambah_keluar():
    if 'user' not in session:
        return redirect('/')

    tanggal = datetime.now().strftime('%Y-%m-%d')
    keterangan = request.form['keterangan']
    nominal = request.form['nominal']

    if not keterangan or not nominal:
        flash("Semua field harus diisi!", "error")
        return redirect('/kas_keluar')

    conn = get_db()
    conn.execute(
        'INSERT INTO kas_keluar(tanggal, keterangan, nominal) VALUES (?,?,?)',
        (tanggal, keterangan, nominal)
    )
    conn.commit()
    return redirect('/kas_keluar')

# ------------------- LOGOUT -------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ------------------- RUN -------------------
if __name__ == '__main__':
    app.run(debug=False)
