from flask import Flask, session, redirect, url_for, render_template, request
from flask_caching import Cache

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['CACHE_TYPE'] = 'SimpleCache'
cache = Cache(app)

@app.route('/')
def index():
    if 'username' in session:
        return f'Logged in as {session["username"]}'
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type="text" name="username">
            <p><input type="submit" value="Login">
        </form>
    '''

@cache.cached(timeout=60)
def get_data():
    return  0

@cache.cached(timeout=60)
@app.route('/expensive_query')
def expensive_query():
    # Імітація дорогого запиту до бази даних
    import time
    time.sleep(2)
    return "This is a result of a time-consuming query!"


@app.route('/clear_cache')
def clear_cache():
    cache.clear()
    return "Cache cleared!"


@app.route('/logout')
def logout():
    session.pop('username', None)
    # session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
