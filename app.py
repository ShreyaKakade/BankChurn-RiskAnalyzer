from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from utils.preprocess import load_artifacts, build_feature_vector
import os
import sqlite3
from contextlib import closing

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change_this_in_production')
app.config['DATABASE'] = os.path.join(app.instance_path, 'app.db')

# Ensure instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# ----------------------
# Database helpers
# ----------------------
def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with closing(get_db()) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                credit_score INTEGER,
                geography TEXT,
                gender TEXT,
                age INTEGER,
                tenure INTEGER,
                balance REAL,
                num_products INTEGER,
                has_cr_card INTEGER,
                is_active_member INTEGER,
                estimated_salary REAL,
                prediction INTEGER,  -- 0 for Stay, 1 for Churn
                probability REAL,   -- Churn probability (if available)
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        db.commit()

init_db()

# ----------------------
# Routes
# ----------------------
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','').strip()
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('register.html')
        pw_hash = generate_password_hash(password)
        try:
            db = get_db()
            db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, pw_hash))
            db.commit()
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'warning')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','').strip()
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = username
            return redirect(url_for('home'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    # Total registered users
    total_users = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    
    # Total predictions
    total_predictions = db.execute('SELECT COUNT(*) FROM predictions').fetchone()[0]
    
    # User-specific predictions
    user_predictions = db.execute(
        'SELECT COUNT(*) FROM predictions WHERE user_id = ?',
        (session['user_id'],)
    ).fetchone()[0]
    
    # Churn vs. Stay counts (for chart)
    prediction_counts = db.execute("""
        SELECT prediction, COUNT(*) as count
        FROM predictions
        GROUP BY prediction
    """).fetchall()
    churn_counts = {'Stay': 0, 'Churn': 0}
    for row in prediction_counts:
        label = 'Churn' if row['prediction'] == 1 else 'Stay'
        churn_counts[label] = row['count']
    
    # Average feature values (example: Credit Score, Balance)
    avg_features = db.execute("""
        SELECT AVG(credit_score) as avg_credit_score,
               AVG(balance) as avg_balance
        FROM predictions
    """).fetchone()
    
    return render_template(
        'home.html',
        username=session.get('username'),
        total_users=total_users,
        total_predictions=total_predictions,
        user_predictions=user_predictions,
        churn_counts=churn_counts,
        avg_credit_score=round(avg_features['avg_credit_score'] or 0, 2),
        avg_balance=round(avg_features['avg_balance'] or 0, 2)
    )
# Prediction routes
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    result = None
    probability = None
    error = None
    try:
        model, geo_encoder, feature_order, scaler = load_artifacts()
    except Exception as e:
        error = f"Model load error: {e}"
        flash(f"Model load error: {e}", 'danger')
        return render_template('predict.html', result=result, probability=probability, error=error)

    if request.method == 'POST':
        try:
            X = build_feature_vector(request.form, feature_order, geo_encoder, scaler)
            y_pred = model.predict(X)[0]
            try:
                proba = model.predict_proba(X)[0][1]
                y_pred = 1 if proba >= 0.3 else 0  # Lower threshold to 30%
            except Exception:
                proba = None
            result = 'Customer Will Churn' if int(y_pred) == 1 else 'Customer Will Stay'
            probability = round(float(proba)*100, 2) if proba is not None else None
            # Save prediction to database
            db = get_db()
            db.execute("""
                INSERT INTO predictions (
                    user_id, credit_score, geography, gender, age, tenure, balance,
                    num_products, has_cr_card, is_active_member, estimated_salary,
                    prediction, probability
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session['user_id'],
                request.form.get('credit_score'),
                request.form.get('geography'),
                request.form.get('gender'),
                request.form.get('age'),
                request.form.get('tenure'),
                request.form.get('balance'),
                request.form.get('num_products'),
                1 if request.form.get('has_cr_card') == 'Yes' else 0,
                1 if request.form.get('is_active') == 'Yes' else 0,
                request.form.get('estimated_salary'),
                int(y_pred),
                proba
            ))
            db.commit()
        except Exception as e:
            error = f"Prediction error: {e}"
            flash(f"Prediction error: {e}", 'danger')
    return render_template('predict.html', result=result, probability=probability, error=error)

if __name__ == '__main__':
    app.run(debug=True)
