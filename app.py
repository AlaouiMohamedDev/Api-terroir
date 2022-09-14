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
from datetime import date



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


#Setting Message Table

class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  email = db.Column(db.String(50))
  message = db.Column(db.String(80))
  seen = db.Column(db.Boolean)

  def __init__(self, name,email ,message,seen):
        self.name = name
        self.email = email
        self.message = message
        self.seen = seen

class MessageModelSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email','message' ,'seen')    

Message_schema = MessageModelSchema()
Messages_schema = MessageModelSchema(many=True)

#END of Setting Message Table

# class category

class Category(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50),unique=True)
  image = db.Column(db.String(80))
  

  def __init__(self, name, image):
        self.name = name
        self.image = image

# class coopérative
class Cooperative(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    email = db.Column(db.String,unique=True)
    adress= db.Column(db.String(300))
    tel= db.Column(db.String(300))
    description = db.Column(db.Text)
    image = db.Column(db.String(300))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
  
  
    def __init__(self, name, email,adress,tel,description,image):
        self.name = name
        self.email = email
        self.adress = adress
        self.tel=tel
        self.description = description
        self.image = image

# class produit
class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(300),unique=True)
    prix = db.Column(db.Float)
    description = db.Column(db.Text)
    category = db.Column(db.Integer,nullable = False)
    cooperative = db.Column(db.Integer,nullable = False)
    image = db.Column(db.String(300))
    qte = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

  
    def __init__(self, nom, prix, description, cooperative,category,qte,image):
        self.nom = nom
        self.prix = prix
        self.description = description
        self.category = category
        self.cooperative = cooperative
        self.qte = qte
        self.image = image


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  public_id = db.Column(db.String(50), unique=True)
  name = db.Column(db.String(50),unique=True)
  email = db.Column(db.String(300),unique=True)
  password = db.Column(db.String(80))
  tel = db.Column(db.String(80))
  adresse = db.Column(db.String(300))
  admin = db.Column(db.Boolean)
  isLogedIn = db.Column(db.Boolean)
  deletedAt = db.Column(db.Date)

 
class Panier(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  produit_id = db.Column(db.Integer)
  user_id = db.Column(db.Integer)
  qte_produit = db.Column(db.Integer)

  
  def __init__(self, produit_id, user_id,qte_produit):
      self. produit_id = produit_id
      self.user_id =user_id
      self.qte_produit = qte_produit

class Detail_commande(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  id_prod= db.Column(db.Integer)
  id_cmd = db.Column(db.Integer)
  qte = db.Column(db.Integer)

  
  def __init__(self,  id_prod, id_cmd,qte):
      self.  id_prod =  id_prod
      self.id_cmd = id_cmd
      self.qte = qte

class Commande(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  firstName = db.Column(db.String(500))
  lastName = db.Column(db.String(500))
  city = db.Column(db.String(500))
  adress = db.Column(db.String(500))
  statut = db.Column(db.String(500) ,default="En traitement")
  date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
  id_user = db.Column(db.Integer)
  prixT = db.Column(db.Float)
  tel = db.Column(db.String(500))

  def __init__(self ,adress,statut,city,tel,firstName,lastName,id_user,prixT):
    self.adress = adress
    self.city = city
    self.firstName = firstName
    self.lastName = lastName
    self.id_user = id_user
    self.prixT = prixT
    self.tel = tel
    self.statut  = statut




class CooperativeModelSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email','adress','date' ,'tel','description','image')


Cooperative_schema = CooperativeModelSchema()
Cooperatives_schema = CooperativeModelSchema(many=True)

class ProduitModelSchema(ma.Schema):
    class Meta:
        fields = ('id', 'nom', 'prix','cooperative','date','description','category','qte','image')


Produit_schema = ProduitModelSchema()
Produits_schema = ProduitModelSchema(many=True)

class PanierModelSchema(ma.Schema):
    class Meta:
      fields= ('id','produit_id', 'user_id','qte_produit')

Panier_schema= PanierModelSchema()
Paniers_schema= PanierModelSchema(many=True)

class CommandeModelSchema(ma.Schema):
    class Meta:
      field = ('id','adress', 'statut','date','city','lastName','firstName' ,'id_user','prixT' )

Commande_schema = CommandeModelSchema()
Commandes_schema = CommandeModelSchema(many=True)

class DetailCommandeModelSchema(ma.Schema):
    class Meta:
      field = ('id','id_prod','id_cmd','qte' )

DetailCommande_schema = DetailCommandeModelSchema()
DetailCommandes_schema = DetailCommandeModelSchema(many=True)

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
@app.route('/product',methods=['POST'])
@token_required
def ajouterProduit(current_user):
    nomProduit = request.json['name']
    prix = request.json['price']
    desc = request.json['description']
    category = request.json['catId']
    cooperative = request.json['coopId']
    image = request.json['image']
    qte = request.json['qte']
    produit = Produit(nom=nomProduit,prix=prix,description=desc,cooperative=cooperative,category=category,qte=qte,image=image)
    db.session.add(produit)
    db.session.commit()
    return jsonify({'status':200 ,'message': 'produit ajouter' })

@app.route('/products',methods=['GET'])

def afficherProduit():
  produit = Produit.query.all()
  output =[]
  for c in produit:
    pr_data= {}
    pr_data['id']= c.id
    pr_data['category']= c.category
    pr_data['cooperative']= c.cooperative
    pr_data['description']= c.description
    pr_data['image']= c.image
    pr_data['date']= c.date_created
    pr_data['nom']= c.nom
    pr_data['prix']= c.prix
    pr_data['qte']= c.qte
    output.append(pr_data)

  return jsonify(output)


@app.route('/product/<id>', methods=['PUT'])
@token_required
def update_produit(current_user,id):
  produit = Produit.query.get(id)
  nomProduit = request.json['name']
  prix = request.json['price']
  desc = request.json['description']
  category = request.json['catId']
  cooperative = request.json['coopId']
  image = request.json['image']
  qte = request.json['qte']
  produit.nom = nomProduit
  produit.prix = prix
  produit.desc = desc
  produit.category = category 
  produit.qte = qte
  if image:
    produit.image = image
  db.session.commit()
  return jsonify({'status':200, 'results': 'produit modifier' }) 


@app.route('/product/<id>', methods=['DELETE'])
@token_required
def delete_Produit(current_user,id):
  produit = Produit.query.get(id)
  if not produit:
    return jsonify({ 'status':400,'results': 'produit not found' }) 
  db.session.delete(produit)
  db.session.commit()

  return jsonify({ 'status':200,'results': 'produit deleted' }) 


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
@app.route('/commande',methods=['POST'])
@token_required
def ajouterCommande(current_user):
    firstName = request.json['firstName']
    lastName = request.json['lastName']
    city = request.json['city']
    tel = request.json['tel']
    adress = request.json['adress']
    id_user = request.json['id_user']
    prixT = request.json['prixT']
    commande = Commande(tel=tel,city =city,firstName=firstName,lastName =lastName,adress=adress,id_user=id_user ,prixT=prixT,statut="En traitement")
    db.session.add(commande)
    db.session.commit()
    
    cmd = Commande.query.all()
    idCmd=cmd[len(cmd)-1].id

    prods= request.json['prods']
    for i in range(len(prods)):
      produit = Produit.query.get(prods[i]['id_prod'])
      if prods[i]['qte'] > produit.qte :
        return jsonify({ 'status':400,'message':"Qunatité invalide"})
      produit.qte = produit.qte - prods[i]['qte']
      db.session.commit()
      detail=Detail_commande(id_prod=prods[i]['id_prod'],id_cmd=idCmd,qte=prods[i]['qte'])
      db.session.add(detail)
      db.session.commit()
    
    return jsonify({ 'status':200,'message':"Commande attribuer"})

@app.route('/commande/<id>',methods=['DELETE'])
def deleteCmd(id):
  commande = Commande.query.get(id)
  db.session.delete(commande)
  db.session.commit()
  details = Detail_commande.query.filter_by(id_cmd=id).all()
  for i in details:
    db.session.delete(i)
    db.session.commit()
  return jsonify({'message' : "Command deleted successufly"})


@app.route('/commande/<id>',methods=['PUT'])
def updateCmd(id):
  commande = Commande.query.get(id)
  commande.statut = request.json['statut']
  db.session.commit()
  return jsonify({'message' : "Command Updated"})

@app.route('/commandes',methods=['GET'])
def getAllCmd():
  commandes = Commande.query.all()
  output =[]
  for c in commandes:
    cmd_data= {}
    cmd_data['id']= c.id
    cmd_data['adress']= c.adress
    cmd_data['firstName'] = c.firstName
    cmd_data['lastName'] = c.lastName
    cmd_data['statut']= c.statut
    cmd_data['id_user']= c.id_user
    cmd_data['prixT']= c.prixT
    cmd_data['date']= c.date
    output.append(cmd_data)

  return jsonify(output)

@app.route('/details',methods=['GET'])
def getAlldetails():
  details = Detail_commande.query.all()
  output =[]
  for c in details:
    detail_data= {}
    detail_data['id']= c.id
    detail_data['qte']= c.qte
    detail_data['id_prod']= c.id_prod
    detail_data['id_cmd']= c.id_cmd
    output.append(detail_data)

  
  return jsonify(output)

@app.route('/commandes/<id>',methods=['GET'])
def afficher_commande(id):
  commandes = Commande.query.filter_by(id_user=id).all()  
  output =[]
  for c in commandes:
    cmd_data= {}
    cmd_data['adress']= c.adress
    cmd_data['statut']= c.statut
    cmd_data['id_user']= c.id_user
    cmd_data['prixT']= c.prixT
    cmd_data['date']= c.date
    output.append(cmd_data)

  
  return jsonify(output)

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
  user = User.query.filter_by(public_id=public_id).first()
  if not user:
    return jsonify({'message' : 'No user found!'})
  if not check_password_hash(user.password, request.json['password']):
    return jsonify({'message' : 'Password invalid!'})
  user.name = request.json['name']
  if request.json['adress'] !="":
    user.adresse = request.json['adress']
  if request.json['tel'] !="":
    user.tel = request.json['tel']
  db.session.commit()
  return jsonify({'status':200,'message' : 'The user has updated!'})


#login
@app.route('/login',methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message':'Email ou mot de passe incorrecte','status':401})
    
    if check_password_hash(user.password, password):
        token = jwt.encode({'public_id': user.public_id}, app.config['SECRET_KEY'], 'HS256')
        user.isLogedIn = True
        db.session.commit()
        return jsonify({'token' : token,
                        'status':200,
                        'public_id':user.public_id,
                        'id' : user.id,
                        'email' : user.email,
                        'name' : user.name,
                        'admin': user.admin,
                        'password': user.password,
                        'tel' : user.tel,
                        'adresse' : user.adresse,
                        'isLogedIn': user.isLogedIn
        })
    return jsonify({'error':"true",
                    'message':'Email ou mot de passe incorrecte'
        })

@app.route('/logout/<id>',methods=['GET'])
def logout(id):
  user = User.query.filter_by(id=id).first()
  user.isLogedIn= False
  db.session.commit()
  return jsonify({'status':"200",
                    'message':'logged out successfuly',
                    'isLogedIn': user.isLogedIn
        })
        
#getUser
@app.route('/getUser/<id>',methods=['GET'])
def getUser(id):
    user = User.query.filter_by(public_id=id).first()
    if not user:
      return jsonify({'msg': 'n existe pas'})
    user_data= {}
    user_data['id']= user.id
    user_data['public_id']= user.public_id
    user_data['name']= user.name
    user_data['password']= user.password
    user_data['admin']= user.admin
    user_data['isLogedIn']= user.isLogedIn
    
    return jsonify({'user': user_data,'status':200})

#getAllUsers
@app.route('/getUsers',methods=['GET'])
def getUsers():
    users = User.query.all()
    return jsonify(Users_schema.dump(users))


#DeleteUser
@app.route('/user',methods=['PUT'])
@token_required
def delete_user(current_user):
    user = User.query.get(request.json['idUser'])
    password = request.json['password']
    admin = User.query.get(request.json['idAdmin'])
    if check_password_hash(admin.password, password):
      user.deletedAt = date.today()
      db.session.commit()
      return jsonify({'status':200,'message':user.name+' deleted successfully'})
    else:
      return jsonify({'status':400,'message':'not deleted'})



@app.route('/promoteuser/<id>', methods=['PUT'])
@token_required
def promoteUser(current_user,id):
  user = User.query.get(id)
  password = request.json['password']
  admin = User.query.get(request.json['idAdmin'])
  if check_password_hash(admin.password, password):
    user.admin = True
    db.session.commit()
    return jsonify({'status':200,'message':user.name+'Has Been Promoted'})
  else:
    return jsonify({'status':400,'message':'not promoted'})


#RestoreUser
@app.route('/restorUser',methods=['PUT'])
@token_required
def restore_user(current_user):
    user = User.query.get(request.json['idUser'])
    password = request.json['password']
    admin = User.query.get(request.json['idAdmin'])
    if check_password_hash(admin.password, password):
      user.deletedAt = None
      db.session.commit()
      return jsonify({'status':200,'message':user.name+' Restored successfully'})
    else:
      return jsonify({'status':400,'message':'not restored'})


class UserModelSchema(ma.Schema):
    class Meta:
        fields = ('id','public_id','deletedAt','isLogedIn','name','email','admin','tel','image','adresse','password')


User_schema = UserModelSchema()
Users_schema = UserModelSchema(many=True)

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


@app.route('/category/<idc>', methods=['PUT'])
@token_required
def update_category(current_user,idc):
  category = Category.query.get(idc)
  name= request.json['name']
  image = request.json['image']
  category.name = name
  if image :
    category.image = image
  db.session.commit()
  return jsonify({ 'status':200,'message': 'category modifier' }) 

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
def afficherCategory():
  category = Category.query.all()
  return jsonify(Categories_schema.dump(category))

# add new coopérative
@app.route('/cooperative', methods=['POST'])
def add_cooperative():

  data = request.get_json()

  ExistCoop = Category.query.filter_by(name=data['email']).first()
  if ExistCoop:
    return jsonify({'error':"true",
                    'message':'Cooperative existe'
        })
  else:
    cooperative = Cooperative(name=data['name'],email=data['email'],adress=data['adress'],tel=data['tel'],description=data['description'],image=data['image'])
    db.session.add(cooperative)
    db.session.commit()
    return jsonify({'message' : 'cooperative ajouté par succée',
                    'status':200})

#modifier cooperative

@app.route('/cooperative/<idc>', methods=['PUT'])
@token_required
def update_cooperative(current_user,idc):
  cooperative = Cooperative.query.get(idc)
  name= request.json['name']
  email= request.json['email']
  adress = request.json['adress']
  tel= request.json['tel']
  description= request.json['description']
  image = request.json['image']
  cooperative.name = name
  cooperative.email = email
  cooperative.adress = adress
  cooperative.tel = tel
  cooperative.description = description
  if image :
    cooperative.image = image
  db.session.commit()
  return jsonify({ 'status':200,'message': 'cooperative modifier' }) 

@app.route('/cooperative/<id>', methods=['DELETE'])
@token_required
#delete cooperative
def delete_cooperative(current_user,id):

  cooperative = Cooperative.query.get(id)
  db.session.delete(cooperative)
  db.session.commit()

  return jsonify({ 'status':200,'message': 'cooperative deleted' }) 
#affichher all cooperative
@app.route('/cooperatives', methods=['GET'])
def affichercooperative():
  cooperative = Cooperative.query.all()
  return jsonify(Cooperatives_schema.dump(cooperative))



####################################   MESSAGES    ####################################  
# add new Message
@app.route('/message', methods=['POST'])
def add_message():
    data = request.get_json()
    message= Message(name=data['name'],email=data['email'],message=data['message'],seen=False)
    db.session.add(message)
    db.session.commit()
    return jsonify({'message' : 'message ajouté par succée',
                    'status':200})

#affichher all meassges
@app.route('/messages', methods=['GET'])
def affichermessages():
  message = Message.query.all()
  return jsonify(Messages_schema.dump(message))

@app.route('/message/<id>', methods=['PUT'])
def update_message(id):
  message = Message.query.get(id)
  message.seen = True
  db.session.commit()
  return jsonify({ 'status':200,'message': 'message modifier' }) 
#################################   END MESSAGES    ####################################  

@app.route('/topProducts', methods=['GET'])
def get_topProducts():
   details = Detail_commande.query.all()
   output =[]
   for d in details:
      data ={}
      product = Produit.query.get(d.id_prod)

      cooperative = Cooperative.query.get(product.cooperative)
      data['coopId'] = cooperative.id
      data['coopImage'] = cooperative.image
      data['coopName'] = cooperative.name
      data['coopJoined'] = cooperative.date 
      data['countProd'] = len(Produit.query.filter_by(cooperative=cooperative.id).all())
      data['image'] = product.image
      data['stock'] = product.qte
      data['prix'] = product.prix
      data['nom'] = product.nom
      data['created'] = str(product.date_created).split()[0]
      if len(output)==0:
        data['id_prod'] = d.id_prod
        data['qte'] = d.qte
        output.append(data)
      else:
        test = False
        qte=0
        for i in output:
          if i['id_prod'] == d.id_prod:
            test =True
            qte = i['qte']
            output.remove(i)
        if test:
          data['id_prod'] = d.id_prod
          data['qte'] = d.qte+qte
          output.append(data)
        else:
          data['id_prod'] = d.id_prod
          data['qte'] = d.qte
          output.append(data)

   newlist = sorted(output, key=lambda d: d['qte'], reverse=True)
   return jsonify(newlist)


#db.create_all()
# Run Server
if __name__ == '__main__':
  app.run(debug=True)

