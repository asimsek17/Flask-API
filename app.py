from flask import Flask,jsonify,request,make_response
from flask_sqlalchemy import SQLAlchemy
from functools import wraps 
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY']='secretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/asims/Desktop/Teams/database.db'
db = SQLAlchemy(app)

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=request.args.get('token')

        if not token:
            return jsonify({'message':'Token is missing!'}) ,403        
        else:
            try:
                jwt.decode(token, options={"verify_signature": False})
                
        
            except:
                return jsonify({'message': 'token is invalid'}) , 403
        
        return f(*args,**kwargs)
    return decorated

class Tactics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(80), unique=True, nullable=False)
    formation= db.Column(db.String(20), unique=False, nullable=False)
    lineup = db.Column(db.String(200), unique=True, nullable=False)
    game_plan=db.Column(db.String(50), unique=False, nullable=False)



class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(80), unique=True, nullable=False)
    coach_name = db.Column(db.String(120), unique=True, nullable=False)
    players=db.Column(db.String(200), unique=True, nullable=False)
    

@app.route("/login")
def login():
    
    auth=request.authorization
    if auth  and auth.username=="admin" and  auth.password=="password":
        token=jwt.encode({'user':auth.username,
                          'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=60)},
                         app.config['SECRET_KEY'])
        return jsonify({'token':token})
    return make_response('Could verify!',401,{'WWW-Authenticate':'Basic realm="Login Required"'})


@app.route('/teams', methods=['GET'])
def get_all_teams():
    
    teams_data= Teams.query.all()   
    output=[]
    
    for team in teams_data:
        team_data={}
        team_data['id']=team.id 
        team_data['team_name']=team.team_name
        output.append(team_data)

    return jsonify({'Teams': output})


@app.route('/teams/<team_name>', methods=['GET'])

def get_one_team(team_name):
    
    team=Teams.query.filter_by(team_name=team_name).first()
        
    if not team:
        return jsonify({'message':'No team found!'})
    
    team_data={}
    team_data['team_name']=team.team_name
    team_data['coach_name']=team.coach_name
    team_data['players']=team.players
    
    return jsonify({ 'Team': team_data})

    
@app.route('/teams/<team_name>/tactic', methods=['GET'])
@token_required
def get_team_tactic(team_name):
    tactic=Tactics.query.filter_by(team_name=team_name).first()
    
    if not tactic:
        return jsonify({'message':'No tactic found!'})
    
    tactic_data={}
    tactic_data['team_name']=tactic.team_name
    tactic_data['formation']=tactic.formation
    tactic_data['lineup']=tactic.lineup
    tactic_data['game_plan']=tactic.game_plan
  
    return jsonify({ 'Team': tactic_data})


if __name__=='__main__':
    app.run(debug=True)