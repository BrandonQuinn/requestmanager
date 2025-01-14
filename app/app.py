from flask import Flask, render_template_string
from mako.template import Template
from mako.lookup import TemplateLookup

app = Flask(__name__)

# Configure Mako template lookup
template_lookup = TemplateLookup(directories=['templates'])

@app.route("/")
def index():
	template = template_lookup.get_template("index.html")
	return template.render(title="Request")

@app.route("/api/users/<username>")
def api(username):
	template = template_lookup.get_template("index.html")
	return template.render(title="Request")

if __name__ == "__main__":
	app.run(debug=True)