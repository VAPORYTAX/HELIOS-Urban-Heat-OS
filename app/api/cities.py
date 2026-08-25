from fastapi import APIRouter,Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import City
from app.db.models_thermal import Area
from app.db.session import get_db
router=APIRouter(prefix='/cities',tags=['cities'])
@router.get('')
def cities(db:Session=Depends(get_db)):
    return [{'id':r.id,'name':r.name,'country_code':r.country_code,'timezone':r.timezone} for r in db.execute(select(City).order_by(City.name)).scalars().all()]
@router.get('/{city_id}/areas')
def areas(city_id:str,db:Session=Depends(get_db)):
    return [{'id':r.id,'name':r.name,'area_type':r.area_type} for r in db.execute(select(Area).where(Area.city_id==city_id)).scalars().all()]
