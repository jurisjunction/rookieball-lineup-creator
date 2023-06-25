from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

from positions import Position, positions

# Configure application
app = Flask(__name__)




# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///roster.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def get_team(team_id):
    rows = db.execute("SELECT players.id, players.name, players.jersey FROM players JOIN rosters ON players.id = rosters.player_id JOIN teams ON rosters.team_id = teams.id WHERE rosters.team_id = ?;", team_id)
    return rows


@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    if request.method == "GET":
        rows = db.execute("SELECT name FROM teams WHERE creator_id = ?;", session['user_id'])
        if len(rows) == 0:
            return render_template("noteams.html")
        else:
            return render_template("index.html", teams=rows)
    else:
        team_name = request.form.get("team")
        if team_name == None:
            return apology("Please enter a team name.")

        session["team_id"] = int(db.execute("SELECT id FROM teams WHERE creator_id = ? AND name = ?;", session['user_id'], team_name)[0]['id'])
        return redirect("/showteam")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if username == "" or password == "" or confirmation == "":
            return apology("Not all information entered.")
        elif not not db.execute("SELECT username FROM users WHERE username = ?;", username):
            return apology("Username already taken.")
        elif password != confirmation:
            return apology("Password not confirmed.")
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?);", username, generate_password_hash(password))

            # Log the user in.
            rows = db.execute("SELECT * FROM users WHERE username = ?;", username)
            session["user_id"] = rows[0]["id"]

            # Redirect user to home page
            return redirect("/")

@app.route("/create", methods = ["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        return render_template("create.html")
    else:

        team_name = request.form.get("teamname")
        if not team_name:
            return apology("Please enter a team name.")
        else:
            db.execute("INSERT INTO teams (name, creator_id) VALUES (?, ?);", team_name, session["user_id"])
            return redirect("/")

@app.route("/addplayer", methods = ["GET", "POST"])
@login_required
def addplayer():
    if request.method == "GET":
        return render_template("addplayer.html")

    else:

        player_name = request.form.get("name")
        try:
            player_jersey = int(request.form.get("jersey"))
        except:
            return apology("Jersey number needs to be an integer.")

        player_id = db.execute("INSERT INTO players (name, jersey) VALUES (?, ?);", player_name, player_jersey)
        db.execute("INSERT INTO rosters (player_id, team_id) VALUES (?, ?);", player_id, session["team_id"])
        rows = db.execute("SELECT players.id, players.name, players.jersey FROM players JOIN rosters ON players.id = rosters.player_id JOIN teams ON rosters.team_id = teams.id WHERE rosters.team_id = ?;", session["team_id"])
        if len(rows) == 0:
            return render_template("noplayers.html")
        return redirect("/showteam")

@app.route("/deleteplayer", methods=["POST"])
@login_required
def delete():
    player_id = int(request.form.get("player_id"))
    db.execute("DELETE FROM rosters WHERE player_id = ?;", player_id)
    db.execute("DELETE FROM players WHERE id = ?;", player_id)
    return redirect("/showteam")

@app.route("/showteam")
@login_required
def showteam():

    rows = db.execute("SELECT players.id, players.name, players.jersey FROM players JOIN rosters ON players.id = rosters.player_id JOIN teams ON rosters.team_id = teams.id WHERE rosters.team_id = ?;", session["team_id"])
    if len(rows) == 0:
        return render_template("noplayers.html")
    return render_template("showteam.html", team = rows)

@app.route("/lineup", methods=["GET", "POST"])
@login_required
def lineup():

    team = get_team(session['team_id'])

    # If the session variable isn't set yet, initialize it to an empty list
    if 'availability' not in session:
        session['availability'] = []

    if len(team) == 0:
        return render_template("noplayers.html")
    if request.method == "GET":
        return render_template("lineup.html", team=team, positions=positions, availability=session['availability'])

    if request.method == "POST":
        if request.form['submit-button'] == 'update-availability':
            # Process the player availability data from the form
            availability = request.form.getlist('player-availability')
            # Convert all IDs from the form into integers, as they are submitted as strings.
            availability = [int(id) for id in availability]
            session['availability'] = availability
            print(session['availability'])
            return render_template("lineup.html", team=team, positions=positions, availability=session['availability'])
        elif request.form['submit-botton'] == 'set-lineup':
            # Set the first-inning lineup
            
