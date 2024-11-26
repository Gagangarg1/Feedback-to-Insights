from flask import Flask, render_template_string, request, url_for
import requests
from app import getoutput
import json

app = Flask(__name__)

# Enhanced HTML template with a smaller banner and centered UI
template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SG Insights</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f0f0f0;
        }
        .container {
            text-align: center;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 80%;
            max-width: 600px;
        }
        .banner {
            max-width: 100%;
            max-height: 150px; /* Adjust the max-height for a smaller banner */
            height: auto;
            width: auto;
            border-radius: 10px;
        }
        form {
            margin-top: 20px;
        }
        input[type="text"] {
            width: 80%;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        button {
            padding: 10px 20px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        pre {
            text-align: left;
            background-color: #f8f8f8;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="{{ banner_url }}" alt="Banner" class="banner">
        <h1>SG Insights</h1>
        <form method="post">
            <input type="text" id="api_url" name="api_url" value="{{ api_url }}" placeholder="Enter API URL" required>
            <button type="submit">Call API</button>
        </form>
        <hr>
        <h6 align="left">Insights</h6>
        <pre>{{ response_data }}</pre>
    </div>
</body>
</html>
"""

def format_json(json_obj):
    """Format JSON with highlighted keys."""
    def json_to_html(json_obj):
        if isinstance(json_obj, dict):
            items = [f'<div><span class="key">{json.dumps(k)}</span>: {json_to_html(v)}</div>' for k, v in json_obj.items()]
            return f'<div class="object>{"".join(items)}</div>'
        elif isinstance(json_obj, list):
            items = [json_to_html(v) for v in json_obj]
            return f'<div class="array>{"".join(items)}</div>'
        elif isinstance(json_obj, str):
            return f'<span class="string">{json.dumps(json_obj)}</span>'
        elif isinstance(json_obj, (int, float, bool, type(None))):
            return f'<span class="literal">{json_obj}</span>'
        return '<span class="unknown">Unknown</span>'
    
    return json_to_html(json.loads(json_obj))

@app.route('/', methods=['GET', 'POST'])
def index():
    banner_url = url_for('static', filename='sglogo.png')  # Use Flask's url_for to serve the image
    api_url = ""
    response_data = "No data yet."

    if request.method == 'POST':
        api_url = request.form['api_url']
        try:
            response = getoutput()
            response_data = json.dumps(response, indent=4)
        except Exception as e:
            response_data = f"An error occurred: {e}"

    return render_template_string(template, banner_url=banner_url, api_url=api_url, response_data=response_data)

if __name__ == '__main__':
    app.run(debug=True, port=8080)