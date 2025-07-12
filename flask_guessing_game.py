from flask import Flask, render_template, request, session, redirect, url_for, flash
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

def get_performance_message(tries_used, max_tries):
    """Generate performance message based on tries used"""
    percentage = (tries_used / max_tries) * 100
    
    if percentage <= 25:
        return "🏆 INCREDIBLE! You're a guessing master!"
    elif percentage <= 50:
        return "🎯 Excellent work! Very impressive!"
    elif percentage <= 75:
        return "👍 Good job! Nice guessing!"
    else:
        return "😅 You made it! That was close!"

@app.route('/')
def index():
    """Home page - setup game"""
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    """Initialize game with user settings"""
    try:
        # Get form data
        player_name = request.form.get('player_name', '').strip()
        min_num = int(request.form.get('min_num'))
        max_num = int(request.form.get('max_num'))
        max_tries = int(request.form.get('max_tries'))
        
        # Validate inputs
        if not player_name:
            flash('Please enter a valid name!', 'error')
            return redirect(url_for('index'))
        
        if min_num >= max_num:
            flash('Maximum number must be greater than minimum number!', 'error')
            return redirect(url_for('index'))
        
        if max_tries <= 0:
            flash('Maximum tries must be greater than 0!', 'error')
            return redirect(url_for('index'))
        
        # Store game data in session
        session['player_name'] = player_name
        session['min_num'] = min_num
        session['max_num'] = max_num
        session['max_tries'] = max_tries
        session['secret_number'] = random.randint(min_num, max_num)
        session['tries_used'] = 0
        session['game_over'] = False
        session['won'] = False
        session['guesses'] = []
        
        return redirect(url_for('game'))
        
    except ValueError:
        flash('Please enter valid numbers!', 'error')
        return redirect(url_for('index'))

@app.route('/game')
def game():
    """Main game page"""
    if 'player_name' not in session:
        return redirect(url_for('index'))
    
    return render_template('game.html', 
                         player_name=session['player_name'],
                         min_num=session['min_num'],
                         max_num=session['max_num'],
                         max_tries=session['max_tries'],
                         tries_used=session['tries_used'],
                         game_over=session['game_over'],
                         won=session['won'],
                         guesses=session['guesses'])

@app.route('/make_guess', methods=['POST'])
def make_guess():
    """Process user's guess"""
    if 'player_name' not in session or session['game_over']:
        return redirect(url_for('index'))
    
    try:
        guess = int(request.form.get('guess'))
        
        # Validate guess is in range
        if guess < session['min_num'] or guess > session['max_num']:
            flash(f'Please guess a number between {session["min_num"]} and {session["max_num"]}!', 'error')
            return redirect(url_for('game'))
        
        # Update tries
        session['tries_used'] += 1
        
        # Process guess
        if guess == session['secret_number']:
            # Player wins!
            session['won'] = True
            session['game_over'] = True
            performance_msg = get_performance_message(session['tries_used'], session['max_tries'])
            flash(f'🎉 CONGRATULATIONS! You guessed {session["secret_number"]} correctly in {session["tries_used"]} tries! {performance_msg}', 'success')
        elif guess < session['secret_number']:
            session['guesses'].append({'guess': guess, 'result': 'Too low! Try higher.'})
            flash('📈 Too low! Try a higher number.', 'info')
        else:
            session['guesses'].append({'guess': guess, 'result': 'Too high! Try lower.'})
            flash('📉 Too high! Try a lower number.', 'info')
        
        # Check if out of tries
        if session['tries_used'] >= session['max_tries'] and not session['won']:
            session['game_over'] = True
            flash(f'💥 GAME OVER! You used all {session["max_tries"]} tries. The number was {session["secret_number"]}.', 'error')
        
        return redirect(url_for('game'))
        
    except ValueError:
        flash('Please enter a valid number!', 'error')
        return redirect(url_for('game'))

@app.route('/new_game')
def new_game():
    """Start a new game"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


# HTML Templates (save these in a 'templates' folder)

"""
templates/base.html:
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Number Guessing Game{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Arial', sans-serif;
        }
        .game-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            padding: 30px;
            margin: 20px auto;
            max-width: 600px;
        }
        .game-title {
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
            font-weight: bold;
        }
        .btn-game {
            background: linear-gradient(45deg, #667eea, #764ba2);
            border: none;
            color: white;
            padding: 12px 30px;
            font-weight: bold;
            border-radius: 25px;
            transition: transform 0.2s;
        }
        .btn-game:hover {
            transform: translateY(-2px);
            color: white;
        }
        .guess-history {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
        }
        .game-stats {
            background: #e9ecef;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="game-container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{% if category == 'error' %}danger{% elif category == 'success' %}success{% else %}info{% endif %} alert-dismissible fade show" role="alert">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            {% block content %}{% endblock %}
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

"""
templates/index.html:
{% extends "base.html" %}

{% block content %}
<div class="text-center">
    <h1 class="game-title">🎮 Number Guessing Game 🎮</h1>
    <p class="lead">Welcome! Let's set up your personalized guessing game.</p>
</div>

<form method="POST" action="{{ url_for('start_game') }}">
    <div class="mb-3">
        <label for="player_name" class="form-label">Your Name:</label>
        <input type="text" class="form-control" id="player_name" name="player_name" required>
    </div>
    
    <div class="row">
        <div class="col-md-6">
            <div class="mb-3">
                <label for="min_num" class="form-label">Minimum Number:</label>
                <input type="number" class="form-control" id="min_num" name="min_num" value="1" required>
            </div>
        </div>
        <div class="col-md-6">
            <div class="mb-3">
                <label for="max_num" class="form-label">Maximum Number:</label>
                <input type="number" class="form-control" id="max_num" name="max_num" value="100" required>
            </div>
        </div>
    </div>
    
    <div class="mb-4">
        <label for="max_tries" class="form-label">Maximum Tries:</label>
        <input type="number" class="form-control" id="max_tries" name="max_tries" value="7" min="1" required>
    </div>
    
    <div class="text-center">
        <button type="submit" class="btn btn-game btn-lg">🎲 Start Game</button>
    </div>
</form>
{% endblock %}
"""

"""
templates/game.html:
{% extends "base.html" %}

{% block content %}
<div class="text-center">
    <h1 class="game-title">🎯 Let's Play, {{ player_name }}! 🎯</h1>
</div>

<div class="game-stats">
    <div class="row text-center">
        <div class="col-md-3">
            <strong>Range:</strong><br>
            {{ min_num }} - {{ max_num }}
        </div>
        <div class="col-md-3">
            <strong>Tries Used:</strong><br>
            {{ tries_used }} / {{ max_tries }}
        </div>
        <div class="col-md-3">
            <strong>Remaining:</strong><br>
            {{ max_tries - tries_used }}
        </div>
        <div class="col-md-3">
            <strong>Status:</strong><br>
            {% if game_over %}
                {% if won %}
                    <span class="text-success">Won! 🎉</span>
                {% else %}
                    <span class="text-danger">Lost 💥</span>
                {% endif %}
            {% else %}
                <span class="text-primary">Playing 🎮</span>
            {% endif %}
        </div>
    </div>
</div>

{% if not game_over %}
<div class="text-center">
    <p class="lead">I've picked a number between {{ min_num }} and {{ max_num }}. Can you guess it?</p>
    
    <form method="POST" action="{{ url_for('make_guess') }}" class="mb-4">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="input-group">
                    <input type="number" class="form-control form-control-lg" name="guess" 
                           min="{{ min_num }}" max="{{ max_num }}" 
                           placeholder="Enter your guess..." required autofocus>
                    <button type="submit" class="btn btn-game">Guess!</button>
                </div>
            </div>
        </div>
    </form>
</div>
{% endif %}

{% if guesses %}
<div class="guess-history">
    <h5>📊 Your Guesses:</h5>
    {% for guess_info in guesses %}
        <div class="d-flex justify-content-between align-items-center border-bottom py-2">
            <span><strong>{{ guess_info.guess }}</strong></span>
            <span class="text-muted">{{ guess_info.result }}</span>
        </div>
    {% endfor %}
</div>
{% endif %}

{% if game_over %}
<div class="text-center mt-4">
    <hr>
    {% if won %}
        <h3 class="text-success">🎉 Congratulations! 🎉</h3>
        <p>You guessed the number <strong>{{ session.secret_number }}</strong> in {{ tries_used }} tries!</p>
    {% else %}
        <h3 class="text-danger">💥 Game Over! 💥</h3>
        <p>The number was <strong>{{ session.secret_number }}</strong>. Better luck next time!</p>
    {% endif %}
    
    <a href="{{ url_for('new_game') }}" class="btn btn-game btn-lg mt-3">🔄 Play Again</a>
</div>
{% endif %}
{% endblock %}
"""