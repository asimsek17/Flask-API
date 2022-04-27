from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'  # asssign secret key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/asims/Desktop/Teams/database.db'
db = SQLAlchemy(app)
# app ve database arasında bağlantı


def token_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        else:
            try:
                jwt.decode(token, options={"verify_signature": False})

            except:
                return jsonify({'message': 'token is invalid'}), 403

        return function(*args, **kwargs)
    return decorated


class Tactics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(80), unique=True, nullable=False)
    formation = db.Column(db.String(20), nullable=False)
    lineup = db.Column(db.String(200), unique=True, nullable=False)
    game_plan = db.Column(db.String(50), nullable=False)


# Takım tablosu tanımladım
class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(80), unique=True, nullable=False)
    coach_name = db.Column(db.String(120), unique=True, nullable=False)
    players = db.Column(db.String(200), unique=True, nullable=False)

# kullanıcı girişi için


@app.route("/login")
def login():
    # kullanıcıdan giriş almamızı sağlıyor
    auth = request.authorization

    if auth and auth.username == "admin" and auth.password == "password":
        token = jwt.encode({'user': auth.username,
                            'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=60)},  # tokenin 60 dakika kullanım süresi var
                           app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return make_response('Could verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

# var olan tüm takımları döner


@app.route('/teams', methods=['GET'])
def get_all_teams():
    # teams tablosundan tüm takımları çekip takım adalrını döndürüyor
    teams_data = Teams.query.all()
    all_teams = []

    for team in teams_data:
        team_data = {}
        team_data['id'] = team.id
        team_data['team_name'] = team.team_name
        all_teams.append(team_data)

    return jsonify({'Teams': all_teams})

# sadece bir takımın verileirine ulaşabilen fonksiyon


@app.route('/teams/<team_name>', methods=['GET'])
def get_one_team(team_name):
    # takım adına göre filtreleme yapıyor
    team = Teams.query.filter_by(team_name=team_name).first()

    if not team:
        return jsonify({'message': 'No team found!'})
    # takımın bilgilerini oluşturduğum değişkene atıyor
    team_data = {}
    team_data['team_name'] = team.team_name
    team_data['coach_name'] = team.coach_name
    team_data['players'] = team.players

    return jsonify({'Team': team_data})

# herhangi bir takımın taktik biligilerini döndüren fonksiyon


@app.route('/teams/<team_name>/tactic', methods=['GET'])
# token olmadan verilere erişemiyor
@token_required
def get_team_tactic(team_name):
    # takım adına göre filtreleme yapıyor
    tactic = Tactics.query.filter_by(team_name=team_name).first()

    if not tactic:
        return jsonify({'message': 'No tactic found!'})
    # takımın taktik bilgilerini oluşturduğum değişkene atıyor
    tactic_data = {}
    tactic_data['team_name'] = tactic.team_name
    tactic_data['formation'] = tactic.formation
    tactic_data['lineup'] = tactic.lineup
    tactic_data['game_plan'] = tactic.game_plan

    return jsonify({'Team': tactic_data})


if __name__ == '__main__':
    app.run(debug=True)
