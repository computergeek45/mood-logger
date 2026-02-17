from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# Storage file
DATA_FILE = 'mood_data.json'

# Load existing data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

# Save data
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# HTML template with inline CSS
TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nova AI - Mood Tracker</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 3em;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 30px;
        }
        
        .mood-selector {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .mood-btn {
            padding: 20px;
            border: 3px solid #e0e0e0;
            border-radius: 15px;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            font-size: 2em;
        }
        
        .mood-btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        
        .mood-btn.selected {
            border-color: #667eea;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .mood-label {
            display: block;
            font-size: 0.5em;
            margin-top: 5px;
            font-weight: 600;
        }
        
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            font-family: inherit;
            resize: vertical;
            min-height: 100px;
            margin-bottom: 20px;
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .submit-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .history-item {
            padding: 20px;
            border-left: 4px solid #667eea;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        
        .history-date {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }
        
        .history-mood {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .history-note {
            color: #333;
            line-height: 1.6;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        
        .success-message {
            background: #4caf50;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✨ Nova AI</h1>
            <p>Track your mood, understand yourself better</p>
        </div>
        
        <div class="card">
            <div id="successMessage" class="success-message">Mood saved successfully!</div>
            
            <h2 style="margin-bottom: 20px;">How are you feeling today?</h2>
            
            <form method="POST" action="/save" id="moodForm">
                <div class="mood-selector">
                    <label class="mood-btn">
                        <input type="radio" name="mood" value="amazing" style="display:none;" required>
                        <span>😄<span class="mood-label">Amazing</span></span>
                    </label>
                    <label class="mood-btn">
                        <input type="radio" name="mood" value="good" style="display:none;">
                        <span>😊<span class="mood-label">Good</span></span>
                    </label>
                    <label class="mood-btn">
                        <input type="radio" name="mood" value="okay" style="display:none;">
                        <span>😐<span class="mood-label">Okay</span></span>
                    </label>
                    <label class="mood-btn">
                        <input type="radio" name="mood" value="sad" style="display:none;">
                        <span>😢<span class="mood-label">Sad</span></span>
                    </label>
                    <label class="mood-btn">
                        <input type="radio" name="mood" value="stressed" style="display:none;">
                        <span>😰<span class="mood-label">Stressed</span></span>
                    </label>
                </div>
                
                <textarea name="note" placeholder="What's on your mind? (optional)"></textarea>
                
                <button type="submit" class="submit-btn">Save Mood</button>
            </form>
        </div>
        
        <div class="card">
            <h2 style="margin-bottom: 20px;">Your Mood History</h2>
            
            {% if moods %}
                {% for mood in moods[:10] %}
                <div class="history-item">
                    <div class="history-date">{{ mood.timestamp }}</div>
                    <div class="history-mood">{{ mood.emoji }}</div>
                    {% if mood.note %}
                    <div class="history-note">{{ mood.note }}</div>
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <p>No moods tracked yet. Start by recording your first mood!</p>
                </div>
            {% endif %}
        </div>
    </div>
    
    <script>
        // Handle mood selection styling
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));
                this.classList.add('selected');
            });
        });
        
        // Show success message if redirected after save
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('saved') === 'true') {
            document.getElementById('successMessage').style.display = 'block';
            setTimeout(() => {
                document.getElementById('successMessage').style.display = 'none';
            }, 3000);
        }
    </script>
</body>
</html>
'''

MOOD_EMOJIS = {
    'amazing': '😄',
    'good': '😊',
    'okay': '😐',
    'sad': '😢',
    'stressed': '😰'
}

@app.route('/')
def index():
    moods = load_data()
    moods.reverse()  # Show newest first
    return render_template_string(TEMPLATE, moods=moods)

@app.route('/save', methods=['POST'])
def save_mood():
    mood = request.form.get('mood')
    note = request.form.get('note', '')
    
    if mood:
        data = load_data()
        entry = {
            'mood': mood,
            'emoji': MOOD_EMOJIS.get(mood, '😐'),
            'note': note,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        data.append(entry)
        save_data(data)
    
    return render_template_string(TEMPLATE + '<script>window.location.href = "/?saved=true";</script>', moods=load_data()[::-1])

if __name__ == '__main__':
    app.run(debug=True, port=5000)