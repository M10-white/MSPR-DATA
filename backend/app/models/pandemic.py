from sqlalchemy import Column, Integer, String, Float
from app.utils.database import Base

class CovidData(Base):
    __tablename__ = 'covid_data'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    country = Column(String, index=True)
    confirmed = Column(Integer)
    deaths = Column(Integer)
    recovered = Column(Integer)

class CountryData(Base):
    __tablename__ = 'country_data'
    
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, unique=True, index=True)
    confirmed = Column(Integer)
    deaths = Column(Integer)
    recovered = Column(Integer)
    active = Column(Integer)
    new_cases = Column(Integer)
    new_deaths = Column(Integer)
    new_recovered = Column(Integer)
    death_percentage = Column(Float)
    recovery_percentage = Column(Float)