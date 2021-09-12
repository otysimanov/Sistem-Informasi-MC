from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('firebase.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
app.secret_key = "apl1k4s1kuY"

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')
    

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/mahasiswa')
def mahasiswa():
    # panggil data di database
    # lakukan pengulangan terhadap data
    # simpan data yang sudah di ulang di dalam sebuah array
    maba = db.collection("mahasiswa").stream()
    mb = []

    for mhs in maba:
        m = mhs.to_dict()
        m["id"] = mhs.id
        mb.append(m)    
    
    return render_template('mahasiswa.html', data=mb)
    # return jsonify(mb)

@app.route('/mahasiswa/tambah', methods=["GET", "POST"])
def tambah_mhs():
    if request.method == 'POST':
        data = {
            "nama": request.form["nama"],
            "email": request.form["email"],
            "nim": request.form["nim"],
            "jurusan": request.form["jurusan"]
        }
        # ini adalah fungsi firebase untuk menambahkan data
        db.collection("mahasiswa").document().set(data)
        flash('Berhasil Tambah Mahasiswa', 'success')
        return redirect(url_for('mahasiswa'))
    return render_template('add_mhs.html')

@app.route('/mahasiswa/hapus/<uid>')
def hapus_mhs(uid):
    db.collection('mahasiswa').document(uid).delete()
    flash('berhasil hapus data', 'danger')
    return redirect(url_for('mahasiswa'))

@app.route('/mahasiswa/lihat/<uid>')
def lihat_mhs(uid):
    # memanggil datanya di database
    user = db.collection('mahasiswa').document(uid).get().to_dict()
    # db.collection('mahasiswa').document(uid).delete()
    return render_template('lihat_mhs.html', user=user)

@app.route('/mahasiswa/ubah/<uid>', methods=["GET", "POST"])
def ubah_mhs(uid):
    # menentukan method
    if request.method == "POST":
        data = {
            "nama": request.form["nama"],
            "email": request.form["email"],
            "nim": request.form["nim"],
            "jurusan": request.form["jurusan"]
        }

        db.collection('mahasiswa').document(uid).set(data, merge=True)
        flash('Berhasil ubah data', 'success')
        return redirect(url_for('mahasiswa'))
    # menerima data baru
    # set di database

    # mengambil data
    user = db.collection('mahasiswa').document(uid).get().to_dict()
    user['id'] = uid
    # render template
    return render_template('ubah_mhs.html', user=user)

@app.route('/register',methods=["GET", "POST"])
def register():
    # cek dulu methodnya
    if request.method == "POST":
    # if post
        # ambil data dari form
        data = {
            "nama_lengkap": request.form["nama_lengkap"],
            "email": request.form["email"],
            "no_hp": request.form["no_hp"]
        }
        users = db.collection('users').where('email', '==', data['email']).stream()
        user = {}    
        for us in users:
            user = us.to_dict()
        if user:
            flash('email sudah terdaftar', 'danger')
            return redirect(url_for('register'))

        data['password'] = generate_password_hash(request.form['password'], 'sha256')
        # kita masukkan datanya ke database
        db.collection('users').document().set(data)
        flash('Berhasil Register', 'success')
        # redirect ke halaman login
        return redirect(url_for('login'))

    # menampilkan halaman register
    return render_template('register.html')


if __name__ == "__main__":
    app.run(debug=True)