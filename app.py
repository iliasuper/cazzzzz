from flask import Flask, request, url_for, render_template, flash, redirect, session
import os
import random

app = Flask(__name__)
app.secret_key = 'super secret key'

def save_depzit(email, depzit):
    folder_name = email.replace('@', '_').replace('.', '_')
    file_path = os.path.join(folder_name, 'credentials.txt')
    
    if os.path.exists(file_path):
        lines = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip().lower().startswith('depzit: '):
                    lines.append(line)
            lines.append(f'depzit: {depzit}')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
                
@app.route('/')
def index_():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    if not email or not password:
        flash('все поля должны быть заполнены!')
        return redirect(url_for('index_'))

    folder_name = email.replace('@', '_').replace('.', '_')
    user_folder = os.path.join(folder_name)
    file_path = os.path.join(user_folder, 'credentials.txt')
    if os.path.exists(user_folder):
        save_password = None
        save_name = 'Игрок'
        save_depzit = 1000 
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip().lower()
                    if key == 'password':
                        save_password = value
                    if key == 'name':
                        save_name = value
                    if key == 'depzit':
                        save_depzit = int(value)
        if save_password and password == save_password:
            session['user_name'] = save_name
            session['depzit'] = save_depzit
            session['user_email'] = email
            flash('успешный вход!')
            return redirect(url_for('cazino'))
        else:
            flash('неверный логин или пароль')
            return redirect(url_for('index_'))
    else:
        flash('неверный логин или пароль')
        return redirect(url_for('index_'))
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form['email']
    password = request.form['password']
    if not email or not password:
        flash('все поля должны быть заполнены!')
        return redirect(url_for('register_page'))
    
    folder_name = email.replace('@', '_').replace('.', '_')
    user_folder = os.path.join(folder_name)
    if os.path.exists(user_folder):
        flash('такой пользователь уже существует! Войдите)')
        return redirect(url_for('index_'))
    
    os.makedirs(user_folder, exist_ok = True)
    file_path = os.path.join(user_folder, 'credentials.txt')
    
    with open(file_path, 'w') as f:
        f.write(f'email: {email}\n')
        f.write(f'password: {password}\n')
        f.write(f'depzit: 1000\n')
        if name:
            f.write(f'name: {name}\n')
    
    session['user_name'] = name if not name else "игрок"
    session['depzit'] = '1000'
    session['user_email'] = email
    flash('успешный регистрация!')
    return redirect(url_for('cazino'))

@app.route('/cazino')
def cazino():
    user_name = session.get('user_name', 'Игрок')
    depzit = session.get('depzit', 1000)
    return render_template('cazino.html', depzit=depzit, user_name=user_name)

@app.route('/exeat', methods=['GET'])
def exeat():
    return render_template('login.html')

@app.route('/send', methods=['GET'])
def send():
    depzit = int(session.get('depzit', 1000))
    user_name = session.get('user_name', 'Игрок')
    user_email = session.get('user_email')
    try:
        bid = int(request.args.get('bid', 10))
    except ValueError:
        flash('введите корректную число')
        return render_template('cazino.html', depzit=depzit, users_name=user_name)
    if bid <= 0:
        flash('ставка должна быть больше 0')
        return render_template('cazino.html', depzit=depzit, users_name=user_name)
    elif bid > depzit:
        flash('у вас недостаточно денег')
        return render_template('cazino.html', depzit=depzit, users_name=user_name)
    
    if depzit == 0:
        flash('у вас закачиваются денги')
        return render_template('cazino.html', depzit=depzit, users_name=session.get('user_name', 'Игрок'))
    
    list_slots = ['🎁','❤','🌹']
    first = random.choice(list_slots)
    second = random.choice(list_slots)
    thir = random.choice(list_slots)
    if first == second == thir:
        
        flash('джекпот!!! поздравляю! вы визунчик')
        depzit += bid*4
    else:
        flash('эх, попробуйте еще раз')
        depzit -= bid
    session['depzit'] = depzit
    if user_email:
        save_depzit(user_email, depzit)
    return render_template('cazino.html', first=first, second=second, thir=thir,  users_name=user_name, depzit=depzit)

@app.route('/plus_depzit', methods=['GET'])
def plus_depzit():
    depzit = int(session.get('depzit', 1000))
    user_name = session.get('user_name', 'Игрок')
    email = session.get('user_email')
    if depzit == 0:
        depzit = 1000
        session['depzit'] = depzit
        if email:
            save_depzit(email, depzit)
            flash('успешно попонено')
    else:
        flash('нужно дойти до нуля')
    
    return render_template('cazino.html', depzit=depzit, users_name=user_name)
    

if __name__ == '__main__':
    app.run(debug=True)
