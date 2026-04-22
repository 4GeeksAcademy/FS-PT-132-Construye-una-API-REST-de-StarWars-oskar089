from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    #Relación para los favoritos
    fav_characters: Mapped[list["FavoriteCharacter"]] = relationship("FavoriteCharacter", back_populates="user")
    fav_fruits: Mapped[list["FavoriteFruit"]] = relationship("FavoriteFruit", back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,

            "total_fav_characters": len(self.fav_characters),
            "total_fav_fruits": len(self.fav_fruits)
            # "fav_characters": [character.serialize() for character in self.fav_characters],
            # "fav_fruits": [fruit.serialize() for fruit in self.fav_fruits]
        }

class Character(db.Model):
    __tablename__ = "character"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100),  nullable=False)
    role: Mapped[str] = mapped_column(String(100)) # Ejemplo: Espadachin, Navegante
    bounty: Mapped[str] = mapped_column(String(100)) #Recompensa

    fav_char_lists :Mapped[list["FavoriteCharacter"]] =db.relationship("FavoriteCharacter",back_populates="character")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "bounty": self.bounty,
            # "fav_char_lists":[fav.serialize() for fav in self.fav_char_lists]
        }

class Fruit(db.Model):
    __tablename__ = "fruit"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] =  mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50)) #Ejemplo: Paramecia, Zoan, Logia

    fav_fruit_lists: Mapped[list["FavoriteFruit"]] = db.relationship("FavoriteFruit", back_populates="fruit")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,

            # "fav_fruit_list":[fav.serialize()for fav in self.fav_fruit_lists]
        }


class FavoriteCharacter(db.Model):
    __tablename__ = "favorite_character"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"))
    
    character = db.relationship('Character',back_populates="fav_char_lists")
    user = db.relationship('User', back_populates="fav_characters")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "character_name": self.character.name
        }

class FavoriteFruit(db.Model):
    __tablename__ = "favorite_fruit"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    fruit_id: Mapped[int] = mapped_column(ForeignKey("fruit.id"))

    user: Mapped["User"] = relationship("User", back_populates="fav_fruits")
    fruit: Mapped["Fruit"] = relationship("Fruit", back_populates="fav_fruit_lists")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "fruit_id": self.fruit_id,
            "fruit_name": self.fruit.name
        }
            # do not serialize the password, its a security breach
