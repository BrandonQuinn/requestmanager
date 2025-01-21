from flask import Flask, render_template, redirect, url_for
import init

app = Flask(__name__)

@app.route('/install')
def install():
    if init.is_database_initialised():
        return redirect(url_for('home'))
    return render_template('install.html')

@app.route('/')
def home():
    return "Home Page"

if __name__ == '__main__':
    app.run(debug=True)
