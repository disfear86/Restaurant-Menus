from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    address = Column(String(200))
    image = Column(String(200))

    def update(self, new_name=None, new_address=None, new_image=None):
        if new_name:
            self.name = new_name
        if new_address:
            self.address = new_address
        if new_image:
            self.image = new_image

    @property
    def serialize(self):
        return {
                'id': self.id,
                'name': self.name,
                'address': self.address,
                'image': self.image
                }
