import json
from json import JSONDecodeError
from flask import Flask, jsonify,request
import mysql.connector
from dotenv import load_dotenv
import os


load_dotenv()


#--------- Funcion para obtener conexion con la base de datos ------------
def obtenerConexion():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def cerrarConexion(conexion, cursor):
    try:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()
    except Exception as er:
        return(f"Error al cerrar conexion {er}")


#Crea una instancia en Flask para que se puede ejecutar despues
app = Flask(__name__)

#Linea para hacer que las respues de los jsonify returnen en el  orden en que se agrego
'app.json.sort_keys = False'

#Decorador para definir que la funcion se ejecute cuando se solicute con metodo GET, con la ruta /productos
@app.route('/productos', methods= ['GET'])
def obtener_productos():
    try:
        conexion= obtenerConexion()
        cursor= conexion.cursor(dictionary= True)
        cursor.execute(
            'SELECT id, precio, nombre, cantidad FROM productos'
        )
        #fethall sirve para extraer todos los resultados del cursor
        resultado= cursor.fetchall()
        return jsonify(resultado),200
    except Exception as er:
        return jsonify({'error':f'Hubo un error en la ejecucion {str(er)}'}),500
    finally:
        cerrarConexion(conexion, cursor)

@app.route('/productos', methods= ['POST'])
def agregar_productos():
    #recibe en formato json el nuevo producto
    nuevo_producto= request.get_json()

    nombre= nuevo_producto.get('nombre')
    precio= nuevo_producto.get('precio')
    cantidad= nuevo_producto.get('cantidad')
    if (nombre and precio and cantidad ):

        try:
            precio= float(precio)
            cantidad= int(cantidad)
            conexion= obtenerConexion()
            cursor= conexion.cursor()
            consulta= 'INSERT INTO productos (nombre, precio, cantidad) VALUES (%s, %s, %s)'
            valores= (nuevo_producto["nombre"], nuevo_producto["precio"], nuevo_producto["cantidad"])

            #Ejecuta para MySQL
            cursor.execute(consulta, valores)

            #Guarda los cambios realizados
            conexion.commit()
            #Adquiere el ultimo id utilizado en la base de datos
            nuevo_id= cursor.lastrowid
        
    
            return jsonify({"mensaje": "Producto agregado correctamente", 
                            "producto" : {
                                "id": nuevo_id,
                                "nombre" : nuevo_producto["nombre"],
                                "precio" : nuevo_producto["precio"],
                                "cantidad" : nuevo_producto["cantidad"]
            }}), 201
        except ValueError:
            return jsonify({'mensaje':''})
        except Exception as er:
            return jsonify({"mensaje": f"Ocurrio un error en el proceso {str(er)}"}) , 500
             
        finally:
            cerrarConexion(conexion, cursor)
    else: 
        return jsonify({"mensaje" : "Los campos no fueron llenados correctamente"}), 400
            

@app.route('/productos/<int:id>', methods= ['DELETE'])
def eliminar_producto(id):
    try:
        
        conexion= obtenerConexion()
        cursor= conexion.cursor(dictionary= True)

        cursor.execute("SELECT * FROM productos where id = %s ", (id,))
        #fethone sirve para extraer solo un resultado de cursor
        producto= cursor.fetchone()

        #comprueba si hay producto
        if not producto:
            cursor.close()
            conexion.close()
            return jsonify({"mensaje" : "producto no encontrado, verifique el id"}), 404

        cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
        conexion.commit()

        return jsonify({"mensaje": 'Producto eliminado correctamente',
                        "producto elimando": {
                            'id' : id,
                            'nombre' : producto["nombre"],
                            "precio": producto["precio"],
                            "cantidad": producto["cantidad"]
                        }})
    except Exception as er:
        return jsonify({"mensaje": f'Ocurrio un error en el proceso {str(er)}'}), 500
    
    finally:
            cerrarConexion(conexion, cursor)


@app.route('/productos/<int:id>', methods= ['PUT'])
def modificar_producto(id):
    producto_modificado= request.get_json()
    if 'nombre' in producto_modificado and 'precio' in producto_modificado and 'cantidad' in producto_modificado:
        try:
            conexion= obtenerConexion()
            cursor= conexion.cursor(dictionary= True)

            cursor.execute("SELECT * FROM productos where id = %s ", (id,))
            producto_viejo= cursor.fetchone()

            if not producto_viejo:
                cursor.close()
                conexion.close()
                return jsonify({"mensaje": "el producto seleccionado no existe"}), 401
            
            consulta= '''UPDATE productos
                        SET nombre= %s, precio = %s, cantidad= %s
                        Where id= %s''' 
    
            valores= (producto_modificado['nombre'], producto_modificado['precio'], producto_modificado['cantidad'], id)
            cursor.execute(consulta, valores)
            conexion.commit()

            return jsonify({"mensaje":'Producto modificado correctamente',
                            'Producto nuevo': {
                                'id' : id,
                                'nombre' : producto_modificado["nombre"],
                                'precio': producto_modificado["precio"],
                                'cantidad': producto_modificado["cantidad"]
                            }}),200
            
        except Exception as er:
            return jsonify({"mensaje": f"Ocurrio un error en el proceso {str(er)}"}), 500
        
        finally:
            cerrarConexion(conexion, cursor)
    else:
        return jsonify({"mensaje":"El producto no cumple con los campos necesarios para actualizarse"}), 400
    
    

if __name__ == '__main__':
    app.run(debug= True)





'''#Decorador para definir que la funcion se ejecute cuando se solicute con metodo POST, con la ruta /productos
@app.route('/productos', methods= ['POST'])
def recibir_productos():
    nuevo_producto= request.get_json()

    if "nombre" in nuevo_producto and "precio" in nuevo_producto:
        try:
            # se lee primero para convertir los datos json en lista
            with open('productos.json', 'r', encoding='utf-8') as ar:
                productos = json.load(ar)
        except(FileNotFoundError, JSONDecodeError):
            productos= []

        # se modifica la lista segun el requirimiento de la funcion, en este caso agregar producto
        nuevo_producto["id"]= generar_id(productos)
        productos.append(nuevo_producto)

        with open('productos.json', 'w', encoding= 'utf-8') as ar:
            json.dump(productos,ar, indent=4, ensure_ascii= False )
        return jsonify({"mensaje" : "producto agregado", "productos" : nuevo_producto}), 201
    else:
        return jsonify({"error" : "Campo de Nombre o Precio no ingresado"}), 400



@app.route('/')
def raiz():
    return "API de productos funcionando"


#se le pasa el indice usando <> y especificando el tipo de dato, esto le dice a la funcion el parametro a tomar en cuenta
@app.route('/productos/<int:id>', methods= ['DELETE'])
def borrar_productos(id):
    try:
        # se lee primero para convertir los datos json en lista
        with open('productos.json', 'r', encoding= 'utf-8') as ar:
            productos= json.load(ar)
    except(FileNotFoundError, JSONDecodeError):
        return jsonify({"mensaje": "no existen productos"}),404
    #se modifica la lista segun el requirimiento de la funcion, en este caso ELIMINAR producto

    producto_eliminado= None
    for i,p in enumerate(productos):
        if p["id"] == id:
            producto_eliminado= productos.pop(i)
            break

    if producto_eliminado:
        # se vuelve a abrir el json para introducir los datos actualizados
        with open('productos.json', 'w', encoding= 'utf-8') as ar:
            json.dump(productos, ar)
        return jsonify({"mensaje" : "producto eliminado", "productos" : producto_eliminado})
    else:
        return jsonify({"mensaje": "Error"}),404


def generar_id(productos):
    if productos:
        return max(p["id"] for p in productos ) + 1
    else:
        return 1

@app.route('/productos/<int:id>', methods= ['PUT'])
def modificar_productos(id):
    producto_modificado= request.get_json()
    if "nombre" in producto_modificado and "precio" in producto_modificado:
        try:
            with open("productos.json", 'r', encoding= 'utf-8') as ar:
                productos= json.load(ar)
        except(FileNotFoundError, JSONDecodeError):
            return jsonify({"mensaje": "no existen productos"}),400

        for i, p in enumerate(productos):
            if p["id"] == id:
                producto_modificado["id"] = id
                productos[i] = producto_modificado
                with open('productos.json', 'w', encoding= 'utf-8') as ar:
                    json.dump(productos, ar, indent= 4, ensure_ascii= False)
                return jsonify({"mensaje": "producto modificado"}), 200
        return jsonify({"error":"no existe producto con el id"}), 404
    else:
        return jsonify({"error": "campos de nombre o precio no ingresados correctamente"}), 400
'''