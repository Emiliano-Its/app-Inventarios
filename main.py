import tkinter as tk
import requests


#Carga los los datos de la base de datos para que se impriman en la listbox
def cargar_elementos():
    mi_lista.delete(0, tk.END)   
    try:
        r = requests.get('http://127.0.0.1:5000/productos')
        if r.status_code == 200:
            #r.json para unicamente extraer la parte de json en el get, sin el encabezado de estatus
            for p in r.json():
                mi_lista.insert(tk.END, f'{p['id']}- Producto: {p['nombre']}, - Precio: {p['precio']} pesos Mx')

    except requests.exceptions.ConnectionError:
        mi_lista.insert(tk.END, 'error, no se pudo conectar con el servidor')


def agregar_elemento_lista():
    texto= entrada2.get()
    if texto:
        mi_lista.insert(tk.END, texto)
        entrada2.delete(0, tk.END)

def eliminar_elemento_lista():
    seleccion= mi_lista.curselection()
    if seleccion:
        mi_lista.delete(seleccion[0])

def modificar_elemento_lista():
    seleccion= mi_lista.curselection()
    texto= entrada2.get()
    if texto and seleccion:
        mi_lista.delete(seleccion[0])
        mi_lista.insert(seleccion[0], texto)
        entrada2.delete(0, tk.END)
        

ventana = tk.Tk()
ventana.title("Menu Principal")

mi_label= tk.Label(ventana, text= 'Texto de prueba')
mi_label.pack()
 
mi_lista= tk.Listbox(ventana, width= 80)
mi_lista.pack()

cargar_elementos()

entrada2= tk.Entry(ventana)
entrada2.pack()

boton2= tk.Button(ventana, text= "Agregar elemento", command= agregar_elemento_lista)
boton2.pack()

boton3= tk.Button(ventana, text= "Borrar elemento", command= eliminar_elemento_lista)
boton3.pack()

boton4= tk.Button(ventana, text= "Modificar elemento", command= modificar_elemento_lista)
boton4.pack()


ventana.mainloop()