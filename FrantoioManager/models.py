from datetime import datetime
from app import db
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Cliente(db.Model):
    __tablename__ = 'clienti'
    
    id = db.Column(Integer, primary_key=True)
    nome = db.Column(String(100), nullable=False)
    cognome = db.Column(String(100), nullable=False)
    telefono = db.Column(String(20))
    indirizzo = db.Column(Text)
    email = db.Column(String(120))
    note = db.Column(Text)
    data_creazione = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationship with moliture
    moliture = relationship("Molitura", back_populates="cliente", cascade="all, delete-orphan")
    
    @property
    def nome_completo(self):
        return f"{self.nome} {self.cognome}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cognome': self.cognome,
            'nome_completo': self.nome_completo,
            'telefono': self.telefono,
            'indirizzo': self.indirizzo,
            'email': self.email,
            'note': self.note
        }

class Molitura(db.Model):
    __tablename__ = 'moliture'
    
    id = db.Column(Integer, primary_key=True)
    cliente_id = db.Column(Integer, ForeignKey('clienti.id'), nullable=False)
    sezione = db.Column(Integer, nullable=False)  # 1, 2, 3, 4
    data_ora = db.Column(DateTime, nullable=False)
    stato = db.Column(String(20), nullable=False, default='accettazione')  # accettazione, in molitura, completa, archiviata
    note = db.Column(Text)
    data_creazione = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cliente = relationship("Cliente", back_populates="moliture")
    cassoni = relationship("Cassone", back_populates="molitura", cascade="all, delete-orphan")
    
    @property
    def quantita_totale(self):
        return sum(cassone.quantita for cassone in self.cassoni)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'cliente_nome': self.cliente.nome_completo if self.cliente else '',
            'sezione': self.sezione,
            'data_ora': self.data_ora.strftime('%d/%m/%Y %H:%M') if self.data_ora else '',
            'stato': self.stato,
            'quantita_totale': self.quantita_totale,
            'note': self.note
        }

class Cassone(db.Model):
    __tablename__ = 'cassoni'
    
    id = db.Column(Integer, primary_key=True)
    molitura_id = db.Column(Integer, ForeignKey('moliture.id'), nullable=False)
    numero_cassone = db.Column(Integer, nullable=False)
    quantita = db.Column(Integer, nullable=False)  # quantità in kg
    note = db.Column(Text)
    
    # Relationship
    molitura = relationship("Molitura", back_populates="cassoni")
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_cassone': self.numero_cassone,
            'quantita': self.quantita,
            'note': self.note
        }

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(80), unique=True, nullable=False)
    password_hash = db.Column(String(256), nullable=False)
    ruolo = db.Column(String(20), nullable=False, default='limitato')  # 'limitato' (sezioni 1-2) o 'completo' (tutte)
    attivo = db.Column(Boolean, default=True)
    data_creazione = db.Column(DateTime, default=datetime.utcnow)
    ultimo_accesso = db.Column(DateTime)
    
    def set_password(self, password):
        """Imposta la password hashata"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la password"""
        return check_password_hash(self.password_hash, password)
    
    def can_access_section(self, sezione):
        """Verifica se l'utente può accedere a una sezione specifica"""
        if self.ruolo == 'completo':
            return True
        elif self.ruolo == 'limitato':
            return sezione in [1, 2]
        return False
    
    def get_accessible_sections(self):
        """Restituisce le sezioni accessibili all'utente"""
        if self.ruolo == 'completo':
            return [1, 2, 3, 4]
        elif self.ruolo == 'limitato':
            return [1, 2]
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'ruolo': self.ruolo,
            'attivo': self.attivo,
            'data_creazione': self.data_creazione.strftime('%d/%m/%Y') if self.data_creazione else '',
            'ultimo_accesso': self.ultimo_accesso.strftime('%d/%m/%Y %H:%M') if self.ultimo_accesso else ''
        }
