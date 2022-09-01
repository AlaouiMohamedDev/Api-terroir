import email
from enum import unique
import json
import stat
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
import jwt
import os
import uuid
from werkzeug.security import generate_password_hash,check_password_hash
import datetime 
from functools import wraps
from flask_cors import CORS


# Init app
app = Flask(__name__)
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))

app.secret_key = "0fce17cdea96d72c3290d216400b92a058900acfe9d882d3c0eaaf47256ffc8f"


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialisation de la base de données "db"
db = SQLAlchemy(app)
ma = Marshmallow(app)

# class category

class Category(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50),unique=True)
  image = db.Column(db.String(80))

  def __init__(self, name, image):
        self.name = name
        self.image = image


# class produit
class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(300),unique=True)
    prix = db.Column(db.Float)
    description = db.Column(db.String(300))
    category = db.Column(db.String(300))
    image = db.Column(db.String(300))
    qte = db.Column(db.Integer)
    children = db.relationship('Panier', backref='Produit')
  
    def __init__(self, nom, prix, description,category,qte,image):
        self.nom = nom
        self.prix = prix
        self.description = description
        self.category = category
        self.qte = qte
        self.image = image

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  public_id = db.Column(db.String(50), unique=True)
  name = db.Column(db.String(50),unique=True)
  email = db.Column(db.String(300),unique=True)
  password = db.Column(db.String(80))
  adresse = db.Column(db.String(300))
  admin = db.Column(db.Boolean)
  children = db.relationship('Panier', backref='User')
  children1 = db.relationship('Commande', backref='User')
 
class Panier(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  produit_id = db.Column(db.Integer, db.ForeignKey(Produit.id),nullable = False)
  user_id = db.Column(db.Integer, db.ForeignKey(User.id),nullable = False)
  qte_produit = db.Column(db.Integer)
  children = db.relationship('Commande', backref='Panier')
  
  
  def __init__(self, produit_id, user_id,qte_produit):
      self. produit_id = produit_id
      self.user_id =user_id
      self.qte_produit = qte_produit

class Commande(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  address = db.Column(db.String(500))
  statut = db.Column(db.String(500))
  date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
  id_user = db.Column(db.Integer,db.ForeignKey(User.id),nullable=False)
  id_panier = db.Column(db.Integer ,db.ForeignKey(Panier.id),nullable =False)
  prixT = db.Column(db.Float)

  def __init__(self ,address,id_panier, statut,id_user,prixT):
    self.address = address
    self.statut = statut
    self.id_user = id_user
    self.prixT = prixT
    self.id_panier = id_panier


class ProduitModelSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nom', 'prix', 'description','category','qte','image')


Produit_schema = ProduitModelSchema()
Produits_schema = ProduitModelSchema(many=True)

class PanierModelSchema(ma.Schema):
    class Meta:
      fields= ('id','produit_id', 'user_id','qte_produit')

Panier_schema= PanierModelSchema()
Paniers_schema= PanierModelSchema(many=True)

class CommandeModelSchema(ma.Schema):
    class Meta:
      field = ('id','address', 'statut','date','id_panier' ,'id_user','prixT' )

Commande_schema = CommandeModelSchema()
Commandes_schema = CommandeModelSchema(many=True)

## token verificatio
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        
        try: 
           data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
           current_user = User.query.filter_by(public_id=data['public_id']).first()   
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated



#######################Produit#########################
@app.route('/ajouter_produit',methods=['POST'])
@token_required
def ajouterProduit(current_user):
    nomProduit = request.json['nom_produit']
    prix = request.json['prix_produit']
    desc = request.json['desc_produit']
    category = request.json['category']
    image = request.json['image']
    qte = request.json['qte']
    produit = Produit(nom=nomProduit,prix=prix,description=desc,category=category,qte=qte)
    db.session.add(produit)
    db.session.commit()
    return jsonify({ 'results': 'produit ajouter' })

@app.route('/afficher_produit',methods=['GET'])
@token_required
def afficherProduit(current_user):
  produit = Produit.query.all()
  return jsonify(Produits_schema.dump(produit))

@app.route('/produit/<id>', methods=['PUT'])
@token_required
def update_produit(current_user,id):
  produit = Produit.query.get(id)

  nomProduit = request.json['nom_produit']
  prix = request.json['prix_produit']
  desc = request.json['desc_produit']
  category = request.json['category']
  image = request.json['image']
  qte = request.json['qte']
  produit.nom = nomProduit
  produit.prix = prix
  produit.desc = desc
  produit.category = category
  produit.qte = qte
  produit.image = image
  db.session.commit()
  return jsonify({ 'results': 'produit modifier' }) 


@app.route('/Produit_delet/<id>', methods=['DELETE'])
def delete_Produit(id):

  produit = Produit.query.get(id)
  db.session.delete(produit)
  db.session.commit()

  return jsonify({ 'results': 'produit deleted' }) 


@app.route('/produit/<id>',methods=['GET'])
@token_required
def getProduitById(current_user,id):
    produit = Produit.query.filter_by(id=id).first()
    return jsonify(Produit_schema.dump(produit))

#######################Panier#########################
@app.route('/ajout_panier',methods=['POST'])
@token_required
def ajouterPanier(current_user):
  produit_id = request.json['produit_id']
  user_id = request.json['user_id']
  qte_produit = request.json['qte_produit']
  panier = Panier(produit_id=produit_id,user_id=user_id,qte_produit=qte_produit)
  db.session.add(panier)
  db.session.commit()
  return jsonify ({"msg" : "panier ajoutee"})


@app.route('/afficher_panier/<id>',methods=['GET'])
@token_required
def afficher_panier(current_user,id):
  pan = Panier.query.filter_by(user_id=id ).all()
  resultat = Paniers_schema.dump(pan)
  return jsonify(resultat)

  

@app.route('/modifier_panier/<id>',methods=['PUT'])
@token_required
def modifier_panier(current_user,id):
  panier = Panier.query.get(id)
  produit_id = request.json['produit_id']
  user_id = request.json['user_id']
  qte_produit = request.json['qte_produit']
  panier.produit_id =produit_id
  panier.user_id =user_id
  panier.qte_produit =qte_produit
  db.session.commit()
  return jsonify(Produit_schema.dump(panier)) 

@app.route('/supprimer_panier/<id>', methods=['DELETE'])
@token_required
def delete_panier(current_user,id):

  panier = Panier.query.get(id)
  db.session.delete(panier)
  db.session.commit()
  return jsonify(Produit_schema.dump(panier)) 

######################commande########################
@app.route('/ajouter_commande',methods=['POST'])
@token_required
def ajouterCommnd(current_user):
    address = request.json['address']
    statut = request.json['statut']
    id_user = request.json['id_user']
    prixT = request.json['prixT']
    id_panier = request.json['id_panier']
    commande = Commande(address=address,statut=statut,id_panier=id_panier,id_user=id_user , prixT=prixT)
    db.session.add(commande)
    db.session.commit()
    return jsonify({ 'results': 'Commande ajouter' })


  
@app.route('/afficherComnd',methods=['GET'])
@token_required
def afficher_Commande(current_user):
  liste = Commande.query.all()
  output = []
  for i in liste:
    i_data= {}
    i_data['address']= i.address
    i_data['statut']= i.statut
    i_data['id_user']= i.id_user
    i_data['id_panier'] =i.id_panier
    i_data['prixT']= i.prixT
    i_data['date']= i.date
    output.append(i_data)

  return jsonify({'liste' : output})

@app.route('/afficher_commande/<id>',methods=['GET'])
@token_required
def afficher_commande(current_user,id):
  comd = Commande.query.filter_by(id_user=id).first()  
  cmd_data= {}
  cmd_data['address']= comd.address
  cmd_data['statut']= comd.statut
  cmd_data['id_user']= comd.id_user
  cmd_data['prixT']= comd.prixT
  cmd_data['date']= comd.date
  cmd_data['id_panier']=comd.id_panier
  

  
  return jsonify({'commande': cmd_data})

@app.route('/modifier_commande/<id>',methods=['PUT'])
@token_required
def modifier_commande(current_user,id):
  command = Commande.query.get(id)
  address = request.json['address']
  statut = request.json['statut']
  id_user = request.json['id_user']
  id_panier = request.json['id_panier']
  prixT = request.json['prixT']
  command.address =address
  command.statut =statut
  command.id_user =id_user
  command.id_panier=id_panier
  command.prixT =prixT
  db.session.commit()
  return jsonify(Commande_schema.dump(command)) 

@app.route('/supprimer_comande/<id>', methods=['DELETE'])
@token_required
def delete_comnd(current_user,id):
  cmd = Commande.query.get(id)
  db.session.delete(cmd)
  db.session.commit()
  return jsonify(Commande_schema.dump(cmd)) 



  

#######################User#########################

#afficher tout la liste d'utilisateur
@app.route('/user',methods=['GET'])
@token_required
def affiche_tout_user(current_user):
  if not current_user.admin:
    return jsonify({'msg': 'Connect perfom that function!'})
 
  users = User.query.all()
  output = []
  for user in users:
    user_data= {}
    user_data['id']= user.id
    user_data['public_id']= user.public_id
    user_data['name']= user.name
    user_data['password']= user.password
    user_data['admin']= user.admin
    output.append(user_data)

  return jsonify({'users' : output})

#afficher la liste des produits
@app.route('/afficher_list_produits',methods=['GET'])
@token_required
def listeProduits(current_user):
  liste = Produit.query.all()
  res = Produits_schema.dump(liste)
  return jsonify(res)

#afficher tout un seule d'utilisateur
@app.route('/user/<public_id>',methods=['GET'])
@token_required
def affiche_user(current_user, public_id):

  user = User.query.filter_by(public_id=public_id).first()
  if not user:
    return jsonify({'msg': 'n existe pas'})
  user_data= {}
  user_data['public_id']= user.public_id
  user_data['name']= user.name
  user_data['password']= user.password
  user_data['admin']= user.admin
   
  return jsonify({'user': user_data})

#registre un nouveau utilisateur
@app.route('/register', methods=['POST'])
def signup_user():
 
  data = request.get_json()
  hashed_password = generate_password_hash(data['password'], method='sha256')

  Email = User.query.filter_by(email=data['email']).first()
  if Email:
    return jsonify({'error':"true",
                    'message':'Email existe'
        })
  else:
    user = User(public_id=str(uuid.uuid4()), name=data['userName'],email=data['email'], password=hashed_password,admin=False)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message' : 'registered successfully',
                    'status':200})

#modifier un utilisateur
@app.route('/user/<public_id>',methods=['PUT'])
@token_required
def modifier_user(current_user, public_id):
  if not current_user.admin:
    return jsonify({'message' : 'Cannot perform that function!'})

  user = User.query.filter_by(public_id=public_id).first()

  if not user:
    return jsonify({'message' : 'No user found!'})

  user.admin = True
  db.session.commit()

  return jsonify({'message' : 'The user has been promoted!'})


#login
@app.route('/login',methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    user = User.query.filter_by(name=username).first()

    if not user:
        return jsonify({'message':'Email ou mot de passe incorrecte','status':401})
    
    if check_password_hash(user.password, password):
        token = jwt.encode({'public_id': user.public_id}, app.config['SECRET_KEY'], 'HS256')

        return jsonify({'token' : token,
                        'status':200,
                        'public_id':user.public_id,
                        'id' : user.id,
                        'email' : user.email,
                        'name' : user.name,
                        'admin': user.admin,
                        'password': user.password  
        })
    return jsonify({'error':"true",
                    'message':'Email ou mot de passe incorrecte'
        })

#getUser
@app.route('/getUser/<id>',methods=['GET'])
def getUser(id):
   
   
    user = User.query.filter_by(public_id=id).first()

    if not user:
      return jsonify({'msg': 'n existe pas'})
    user_data= {}
    user_data['public_id']= user.public_id
    user_data['name']= user.name
    user_data['password']= user.password
    user_data['admin']= user.admin
    
    return jsonify({'user': user_data,'status':200})




class CategoryModelSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'image')


Category_schema = CategoryModelSchema()
Categories_schema = CategoryModelSchema(many=True)

# add new category
@app.route('/category', methods=['POST'])
def add_category():

  data = request.get_json()

  ExistCat = Category.query.filter_by(name=data['name']).first()
  if ExistCat:
    return jsonify({'error':"true",
                    'message':'Category existe'
        })
  else:
    category = Category(name=data['name'],image=data['image'])
    db.session.add(category)
    db.session.commit()
    return jsonify({'message' : 'Category added successfully',
                    'status':200})


@app.route('/category/<id>', methods=['PUT'])
@token_required
def update_category(current_user,id):
  category = Category.query.get(id)
  name= request.json['name']
  ExistCat = Category.query.filter_by(name=request.json['name']).first()
  if ExistCat:
    return jsonify({'error':"true",
                    'message':'Category existe'
        })
  image = request.json['image']
  category.name = name
  if image !="":
    category.image = image
  db.session.commit()
  return jsonify({ 'results': 'category modifier' }) 

@app.route('/category/<id>', methods=['DELETE'])
@token_required
def delete_category(current_user,id):

  category = Category.query.get(id)
  if not category:
    return jsonify({'error':"true",
                    'message':'Category not existe'
        })
  db.session.delete(category )
  db.session.commit()

  return jsonify({ 'status':200,'message': 'category deleted' }) 

@app.route('/categories', methods=['GET'])
@token_required
def afficherCategory(current_user):
  category = Category.query.all()
  return jsonify(Categories_schema.dump(category))

# Run Server
if __name__ == '__main__':
  app.run(debug=True)
