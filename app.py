from flask import Flask, render_template, request, redirect, session
import sqlite3
import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE = "knowledge.db"

# -------------------
# DATABASE SETUP
# -------------------

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            department TEXT,
            category TEXT,
            version TEXT,
            content TEXT,
            video_link TEXT,
            file_name TEXT,
            date_created TEXT,
            views INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()

# -------------------
# LOGIN
# -------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == "Windesheim":
            session['logged_in'] = True
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# -------------------
# PROTECT ROUTES
# -------------------

@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if not session.get('logged_in') and request.endpoint not in allowed_routes:
        return redirect('/login')

# -------------------
# DASHBOARD
# -------------------
# -------------------
# ADD ARTICLE
# -------------------

@app.route('/add', methods=['GET', 'POST'])
def add_article():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        department = request.form['department']
        category = request.form['category']
        version = request.form['version']
        content = request.form['content']
        video_link = request.form['video_link']
        date_created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO articles 
            (title, author, department, category, version, content, video_link, date_created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, author, department, category, version, content, video_link, date_created))

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('add.html')


@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM articles")
    total_articles = c.fetchone()[0]

    c.execute("SELECT * FROM articles ORDER BY date_created DESC LIMIT 5")
    latest = c.fetchall()

    c.execute("SELECT * FROM articles ORDER BY views DESC LIMIT 5")
    most_viewed = c.fetchall()

    conn.close()

    return render_template('dashboard.html',
                           total_articles=total_articles,
                           latest=latest,
                           most_viewed=most_viewed)

@app.route('/articles')
def articles():
    search = request.args.get('search')
    category = request.args.get('category')
    department = request.args.get('department')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    query = "SELECT * FROM articles WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params.extend(['%'+search+'%']*2)

    if category:
        query += " AND category = ?"
        params.append(category)

    if department:
        query += " AND department = ?"
        params.append(department)

    c.execute(query, params)
    articles = c.fetchall()

    conn.close()

    return render_template('articles.html', articles=articles)
@app.route('/article/<int:id>')
def article_detail(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("UPDATE articles SET views = views + 1 WHERE id = ?", (id,))
    conn.commit()

    c.execute("SELECT * FROM articles WHERE id = ?", (id,))
    article = c.fetchone()

    conn.close()

    return render_template('detail.html', article=article)
@app.route('/delete/<int:id>')
def delete_article(id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM articles WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/articles')



# -------------------

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)


