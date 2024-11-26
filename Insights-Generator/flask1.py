from flask import Flask, jsonify, render_template
import json
from app import getoutput

app = Flask(__name__)

# Replace this function with your actual JSON-generating code
def generate_json_output():
    return {
        "Heading 1": ["Point 1", "Point 2", "Point 3"],
        "Heading 2": ["Point A", "Point B", "Point C", "Point D"],
        "Heading 3": ["Item X", "Item Y", "Item Z"],
        "Heading 4": ["Detail 1", "Detail 2", "Detail 3"],
        "Heading 5": ["Fact A", "Fact B", "Fact C"],
        "Heading 6": ["Note 1", "Note 2", "Note 3", "Note 4"]
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_insights')
def get_json():
    data = getoutput()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)