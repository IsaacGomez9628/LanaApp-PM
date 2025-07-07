# APIRouter nos permite modularizar nuestros routers, esto divide las rutas de la aplicacion
from fastapi import APIRouter, Response, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_302_FOUND
from app.schema.user_schema import UserSchema, UserSchemaOut
from fastapi.responses import JSONResponse
from app.config.db import engine
from app.model.users import users
from werkzeug.security import generate_password_hash, check_password_hash
from app.model.transaccion import transacciones
from app.schema.transaccion_schema import TransaccionSchema, TransaccionSchemaOut
from app.model.presupuestos import presupuestos
from app.schema.presupuesto_schema import PresupuestoSchema, PresupuestoSchemaOut

from app.model.categorias import categorias

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
        result = connection.execute(users.select()).fetchall()
    return result

@user.get("/lanaapp/transactions/", response_model=List[TransaccionSchemaOut])
def get_transacciones():
    with engine.connect() as connection:
        result = connection.execute(transacciones.select()).fetchall()
        return result
    
@user.post("/lanaapp/transactions/", status_code=HTTP_201_CREATED)
def create_transaccion(data: TransaccionSchema):
    nueva_transaccion = data.model_dump()
    try:
        with engine.connect() as connection:
            connection.execute(transacciones.insert().values(nueva_transaccion))
        return {"mensaje": "Transacción creada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@user.get("/lanaapp/transactions/{transaction_id}", response_model=TransaccionSchemaOut)
def get_transaccion(transaction_id: int):
    with engine.connect() as connection:
        result = connection.execute(
            transacciones.select().where(transacciones.c.id == transaction_id)
        ).first()
        if result is None:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
        return dict(result._mapping)

@user.put("/lanaapp/transactions/{transaction_id}")
def update_transaccion(transaction_id: int, data: TransaccionSchema):
    transaccion_actualizada = data.model_dump()
    try:
        with engine.connect() as connection:
            result = connection.execute(
                transacciones.update()
                .where(transacciones.c.id == transaction_id)
                .values(transaccion_actualizada)
            )
            if result.rowcount == 0:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
        return {"mensaje": "Transacción actualizada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user.delete("/lanaapp/transactions/{transaction_id}")
def delete_transaccion(transaction_id: int):
    with engine.connect() as connection:
        result = connection.execute(
            transacciones.delete().where(transacciones.c.id == transaction_id)
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Transacción no encontrada")
        return {"mensaje": "Transacción eliminada correctamente"}

@user.get("/api/transactions/categories/list")
def get_categories():
    with engine.connect() as connection:
        result = connection.execute(categorias.select()).fetchall()
        return result

@user.get("/lanaapp/presupuesto", response_model=List[PresupuestoSchemaOut])
def obtener_presupuestos():
    with engine.connect() as connection:
        result = connection.execute(presupuestos.select()).fetchall()
        return result

@user.post("/lanaapp/presupuesto", status_code=HTTP_201_CREATED)
def crear_presupuesto(data: PresupuestoSchema):
    nuevo_presupuesto = data.model_dump()
    try:
        with engine.connect() as connection:
            connection.execute(presupuestos.insert().values(nuevo_presupuesto))
        return {"mensaje": "Presupuesto creado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user.put("/lanaapp/presupuesto/{presupuesto_id}")
def actualizar_presupuesto(presupuesto_id: int, data: PresupuestoSchema):
    valores = data.model_dump()
    try:
        with engine.connect() as connection:
            result = connection.execute(
                presupuestos.update()
                .where(presupuestos.c.id == presupuesto_id)
                .values(valores)
            )
            if result.rowcount == 0:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Presupuesto no encontrado")
        return {"mensaje": "Presupuesto actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user.delete("/lanaapp/presupuesto/{presupuesto_id}")
def eliminar_presupuesto(presupuesto_id: int):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                presupuestos.delete().where(presupuestos.c.id == presupuesto_id)
            )
            if result.rowcount == 0:
                raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Presupuesto no encontrado")
        return {"mensaje": "Presupuesto eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user.put("/lanaapp/user")
def update_user():
    pass
