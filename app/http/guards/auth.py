import jwt 
from datetime import datetime, timedelta
from fastapi import Depends, Query, Header, HTTPException
import os 
from dotenv import load_dotenv
load_dotenv()

def is_authenticated(jwt_token: str = Header()):
    
    SECRET_HASH = os.getenv('SECRET_HASH')
    APP_CLIENT = os.getenv('APP_CLIENT')
    
    if jwt_token in [None, ""]:
        print('No access token found')
        raise HTTPException(status_code=401, detail='No access token found')
    
    try:
        token_decoded = jwt.decode(jwt_token, key=SECRET_HASH, algorithms='HS256') 
        if token_decoded['issuer'] not in APP_CLIENT:
            raise HTTPException(status_code=401, detail='Unauthorized')
        if token_decoded['exp'] < datetime.now().timestamp():
            raise HTTPException(status_code=401, detail='Token expired')
    except Exception:
        raise HTTPException(status_code=401, detail='Token not valid')
