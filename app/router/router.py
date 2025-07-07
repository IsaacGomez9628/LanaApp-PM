# APIRouter nos permite modularizar nuestros routers, esto divide las rutas de la aplicacion
from fastapi import APIRouter, Response, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_302_FOUND
from app.schema.user_schema import UserSchema, UserSchemaOut
from fastapi.responses import JSONResponse
from app.config.db import engine
from app.model.users import users
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List

user = APIRouter()


@user.post("/lanaapp/user", status_code=HTTP_201_CREATED)
def create_user(data_user: UserSchema):
    print("Datos recibidos", data_user.model_dump())
    # nuestros usuarios creados se van a convertir en un diccionario para que los pueda leer data_user
    # un diccionario tiene un clave, valor
    new_user = data_user.model_dump()
    # en el generate password hash se reciben dos parametros
    new_user["password_hash"] = generate_password_hash(data_user.password, "pbkdf2:sha256:30", 30)

    del new_user["password"]
    try: 
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(users.insert().values(new_user))
                print("Se agrego el usuario correctamente")
    except Exception as e:
        print("No se agrego el usuario correctamente")
    print("Usuarios insertados con datos", new_user)
    return Response(status_code=HTTP_201_CREATED)

@user.get("/lanaapp/user/{user_id}", response_model = UserSchemaOut)
def obtener_solo_un_usuario(user_id: int):
    try: 
        with engine.connect() as connection:
        # c en la parte de where se refiere a la columna
            result = connection.execute(users.select().where(users.c.id == user_id)).first()
            
            if result is None:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            user_data = dict(result._mapping)
            return user_data
            
    except Exception as e:
        print ("No se encontro el usuario", e)
        raise HTTPException(status_code=500, detail=str(e))

# List nos funciona para que sepamos que es lo que nos va a devolver esta ruta
@user.get("/lanaapp/user", response_model=List[UserSchema])
def obtener_usuarios():
    with engine.connect() as connection:
        # fetchall lo que hace es 
        result = connection.execute(users.select()).fetchall()
    return result




@user.put("/lanaapp/user")
def update_user():
    pass
