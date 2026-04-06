from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Table, Column , ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


favorite_table = Table(
    "favorites",
    db.Model.metadata,
    Column("user_id",ForeignKey("user.id"),primary_key= True),
    Column("character_id", ForeignKey("character.id"), primary_key= True )
)



class User(db.Model):
    __tablename__= "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    user_name: Mapped[str] = mapped_column(String(120),nullable=True)
    favorites: Mapped[list["Character"]] = relationship(
        "Character",
        secondary= favorite_table,
        back_populates= "favorited_by"
    )


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name":self.name,
            "favorites": [character.serialize() for character in self.favorites]

            # do not serialize the password, its a security breach
        }


class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    quote: Mapped[str] = mapped_column(String(120), nullable=False)
    image: Mapped[str] = mapped_column(String(120), nullable=True)
    location_city:Mapped[int]= mapped_column(ForeignKey("location.id"),nullable=True)
    
    favorited_by: Mapped[list["User"]] = relationship(
        "User",
        secondary= favorite_table,
        back_populates= "favorites"
    )
    origin_location:Mapped[list["Location"]]= relationship(
        "Location",
        back_populates="residents"
    )
    


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "quote": self.quote,
            "image": self.image,
            "favorited_by":[user.serialize() for user in self.favorited_by],
            "location_city":self.location_city


        }


class Location(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description:Mapped[str]= mapped_column(String(500),nullable=True)
    image: Mapped[str]= mapped_column(String(500),nullable=True)
    

    residents: Mapped[list["Character"]] = relationship(
        "Character",
        back_populates="origin_location"
    )

    def serialize(self):
        return {
            "id": self.id,
            "name":self.name,
            "description":self.description,
            "image":self.image
        }
