from cgitb import html
import datetime
from flask import Flask, flash, redirect, render_template, request, jsonify, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from password_strength import PasswordPolicy
from password_strength import PasswordStats
from urllib.parse import quote_plus

Esagschool = Flask(__name__)
mail = Mail(Esagschool)

policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 2 uppercase letters
    numbers=1,  # need min. 2 digits
    strength=0.66 # need a password that scores at least 0.5 with its entropy bits
)
#motdepasse=quote_plus('moise@12345')

Esagschool.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:010296@localhost:5432/CampusEsag'
Esagschool.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


Esagschool.config['MAIL_SERVER'] ='smtp.gmail.com'
Esagschool.config['MAIL_PORT'] = 465
Esagschool.config['MAIL_USERNAME'] ='esagndetogo1@gmail.com'
Esagschool.config['MAIL_PASSWORD'] ='Esag12345678'
Esagschool.config['MAIL_USE_TLS'] = False
Esagschool.config['MAIL_USE_SSL'] = True

secretKEy=URLSafeTimedSerializer('MyKey')

mail = Mail(Esagschool)

db=SQLAlchemy(Esagschool)

class Compte(db.Model):
    __tablename__='Compte'
    iduser = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(), nullable=False)
    Prenom = db.Column(db.String(), nullable=False)
    motDepasse = db.Column(db.String(), nullable=False)  
    email =   db.Column(db.String(), nullable=False)  
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    def __init__(self,userName,Prenom,motDepasse,email,confirmed,confirmed_on):
        self.userName=userName
        self.Prenom=Prenom
        self.motDepasse=motDepasse
        self.email=email
        self.confirmed=confirmed
        self.confirmed_on=confirmed_on

class Parcour(db.Model):
    __tablename__='Parcours'
    idParcours = db.Column(db.Integer, primary_key=True)
    CodeParcours = db.Column(db.String(), nullable=True)
    LibelleParcours = db.Column(db.String(), nullable=True)  
    DescriptionParcours =  db.Column(db.String(), nullable=True)
    ConditionAdmissionParcours = db.Column(db.String(),nullable=True)
    def __init__(self,CodeParcours,LibelleParcours,DescriptionParcours,ConditionAdmissionParcours):
        self.CodeParcours=CodeParcours
        self.LibelleParcours=LibelleParcours
        self.DescriptionParcours=DescriptionParcours
        self.ConditionAdmissionParcours=ConditionAdmissionParcours
        
        
class Filiere(db.Model):
    __tablename__='FIlieres' 
    idFiliere = db.Column(db.Integer, primary_key=True)
    CodeFiliere = db.Column(db.String(), nullable=True)
    LibelleFiliere = db.Column(db.String(), nullable=True)    
    LibelleParcours = db.Column(db.String(), nullable=True) 
    Nomresponsable = db.Column(db.String(),nullable=True)
    Prenomresponsable = db.Column(db.String(),nullable=True)
    Telresponsable = db.Column(db.String(),nullable=True) 
    def __init__(self,CodeFiliere,LibelleFiliere,LibelleParcours,Nomresponsable,Prenomresponsable,Telresponsable):
        self.CodeFiliere=CodeFiliere
        self.LibelleFiliere=LibelleFiliere
        self.LibelleParcours=LibelleParcours
        self.Nomresponsable=Nomresponsable
        self.Prenomresponsable=Prenomresponsable
        self.Telresponsable=Telresponsable
        

class Admission(db.Model):
    __tablename__='Admissions'
    idAdmission = db.Column(db.Integer, primary_key=True)
    NomCandidat = db.Column(db.String(), nullable=False)
    PrenomCandidat = db.Column(db.String(), nullable=True)  
    DatedeNaissance =  db.Column(db.String(), nullable=True)
    SexeCandidat =  db.Column(db.String(), nullable=True) 
    NationaliteCandidat =  db.Column(db.String(), nullable=True) 
    TelephoneCandidat = db.Column(db.String(), nullable=True) 

db.create_all()

##########################################################################################################################################################
#
#
#
# Routes adding
#
#
#
##########################################################################################################################################################

@Esagschool.route('/')
def index():
        result=Parcour.query.all()
        return render_template('index.html',listeparcours=result)
    
    
    
##########################################################################################################################################################
#
#
#
# Connexion
#
#
#
##########################################################################################################################################################


@Esagschool.route('/connexion', methods=['POST','GET'])
def connexion():
    if request.method=='POST':
            emailuser=request.form.get('usermail')
            password=request.form.get('password')
            session['usermail']=emailuser
            session['password']=password
            requete = Compte.query.filter(Compte.email==emailuser , Compte.motDepasse==password).all()    
            if requete:
                requete2 = Compte.query.filter(Compte.email==emailuser , Compte.motDepasse==password, Compte.confirmed==True).all() 
                if requete2:
                    return  redirect(url_for('dashbord', email=emailuser))
                else:
                    if not requete2:
                        flash("Votre compte n'est pas confirmé, veuillez confirmer dans votre email")
                        return redirect(url_for('connexion'))
            else:
                if not requete:
                    flash("Impossible de se connecter car email ou mot de passe invalide")
                    return redirect(url_for('connexion'))       
    else:
        request.method=="GET"
        return render_template('login.html')    
  
    return render_template('login.html')

##########################################################################################################################################################
#
#
#
# logout
#
#
#
##########################################################################################################################################################


@Esagschool.route('/logout')
def logout():
    if "usermail" in session:
        session.pop("usermail",None)
        return redirect(url_for('index'))






##########################################################################################################################################################
#
#
#
# Create Account
#
#
#
##########################################################################################################################################################
@Esagschool.route('/nouveau_compte', methods=['POST','GET'])
def nouveau_compte():
    if request.method=="POST":
       emaila=request.form.get('Email')
       session['Email']=emaila
       requete=Compte.query.filter_by(email=emaila).first()
       if requete:
            flash("Impossible de continuer car l'email existe déjà")
            return redirect(url_for('nouveau_compte'))
       else:
           if not requete:
                userName=request.form['Nom']
                Prenom=request.form['Prenom']
                motDepasse=request.form['Mdp']
                email=request.form['Email']
                stats = PasswordStats(motDepasse)
                checkpolicy = policy.test(motDepasse)
                confirmed=False
                confirmed_on = None
                if stats.strength() < 0.66:
                     print(stats.strength())
                     flash("Le mot de passe est faible. Veuillez ne pas utiliser des caractères consécutifs et facilement devinables.")
                     return render_template('signup.html')
                else: 
                    compte = Compte(userName,Prenom,motDepasse,email,confirmed,confirmed_on)
                    db.session.add(compte)
                    db.session.commit()
                    flash("Le compte creer avec success. Un mail de confirmation est envoyé à votre adresse mail")
                    #mail de confirmation envoyee au email
                    token = secretKEy.dumps(email, salt = 'email-confirm')
                    msg = Message('Email de Confirmation', sender = 'esagndetogo1@gmail.com', recipients = [email])
                    link = url_for('confirmermail', token=token, _external=True)
                    msg.body = "Voici votre lien de confirmation : "+link
                    mail.send(msg)
                    return render_template('signup.html')
    else:
        request.method=="GET"
        return render_template('signup.html')   


##########################################################################################################################################################
#
#
#
# Confirm mail
#
#
#
##########################################################################################################################################################





@Esagschool.route('/confirmermail/<token>')
def confirmermail(token):
    try:
         email=secretKEy.loads(token , salt = 'email-confirm', max_age=3600) 
    except SignatureExpired:
         return'le lien de confirmation est expiré'
    requete=Compte.query.filter_by(email=email).first_or_404()
    if requete.confirmed:
        return("Votre compte est deja confirmé, Connectez vous")
    else:
        requete.confirmed = True
        requete.confirmed_on = datetime.datetime.now()
        db.session.add(requete)
        db.session.commit()
    return redirect(url_for('connexion'))




##########################################################################################################################################################
#
#
#
# Gallerie
#
#
#
##########################################################################################################################################################

@Esagschool.route('/galerie', methods=['GET'])
def galerie():
    return render_template('gallery.html')



##########################################################################################################################################################
#
#
#
#Ddropboxroute
#
#
#
##########################################################################################################################################################
    
@Esagschool.route('/filiere/<get_filiere>')
def filiere(get_filiere):
    filiere = Filiere.query.filter_by(LibelleParcours=get_filiere).all()
    FiliereArray = []
    for FIlieres in filiere:
        requeteObj = {}
        requeteObj['idFiliere'] = FIlieres.idFiliere
        requeteObj['LibelleFiliere'] = FIlieres.LibelleFiliere
        requeteObj['CodeFiliere'] = FIlieres.CodeFiliere
        FiliereArray.append(requeteObj)
    return jsonify({'listefiliere' : FiliereArray}) 


##########################################################################################################################################################
#
#
#
#Details Confition admission
#
#
#
##########################################################################################################################################################
 

@Esagschool.route('/conditions_admission', methods=['GET'])
def conditions_admission():
    return render_template('detailsconditions.html')



##########################################################################################################################################################
#
#
#
#check logged user for admission
#
#
#
##########################################################################################################################################################

@Esagschool.route('/procedure_admission_checkuserlogged', methods=['GET'])
def procedure_admission_checkuserlogged():
     if "usermail" in session:
         return redirect(url_for('conditions_admission'))
     else:
         return redirect(url_for('connexion'))
     
     
##########################################################################################################################################################
#
#
#
#check logged user for admission
#
#
#
##########################################################################################################################################################

@Esagschool.route('/procedure_admission', methods=['GET'])
def procedure_admission():
    return render_template('procedureadmission.html')


##########################################################################################################################################################
#
#
#
#Dashboard etudiant
#
#
#
##########################################################################################################################################################

@Esagschool.route('/dashbord', methods=['GET'])
def dashbord():
    return render_template('dashbord.html')


##########################################################################################################################################################
#
#
#
#demande admission
#
#
#
##########################################################################################################################################################


##########################################################################################################################################################
#
#
#
#demande admission
#
#
#
##########################################################################################################################################################

@Esagschool.route('/demande_admission', methods=['GET'])
def demande_admission():
    return render_template('dashbord.html')
     



if __name__=="__name__":
    Esagschool.run(debug=True)