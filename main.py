import tkinter as tk
import requests
from tkinter import messagebox

ruta_productos= 'http://127.0.0.1:5000/productos'

#Carga los los datos de la base de datos para que se impriman en la listbox
def cargar_elementos():
    mi_lista.delete(0, tk.END)   
    try:
        r = requests.get(ruta_productos)
        r.raise_for_status()
        #r.json para unicamente extraer la parte de json en el get, sin el encabezado de estatus
        for p in r.json():
            mi_lista.insert(tk.END, f'{p['id']}- Producto: {p['nombre']}, - Precio: {p['precio']} pesos Mx')

    except requests.exceptions.ConnectionError:
        mi_lista.insert(tk.END, 'Error, no se pudo conectar con el servidor')

def abrir_ventana():
     
     #Abrir ventana temporal
     ventana= tk.Toplevel()
     ventana.title("Agregar Productos")

     tk.Label(ventana, text='Nombre: ').grid(row= 0, column=0)
     entrada_nombre= tk.Entry(ventana)  
     entrada_nombre.grid(row=0, column= 1)

     tk.Label(ventana, text= 'Precio: ').grid(row= 1, column= 0)
     entrada_precio= tk.Entry(ventana)
     entrada_precio.grid(row= 1, column= 1)
     
     tk.Label(ventana, text= 'Cantidad: ').grid(row= 2, column= 0)
     entrada_cantidad= tk.Entry(ventana)
     entrada_cantidad.grid(row= 2, column= 1)

     def agregar_elemento_lista():
            nombre= entrada_nombre.get()
            precio= entrada_precio.get()
            cantidad= entrada_cantidad.get()
            
            try:
                 productos= {
                      'nombre' : nombre,
                      'precio' : precio,
                      'cantidad' : cantidad
                 }
                
                 r= requests.post(ruta_productos, json= productos)
                 r.raise_for_status()
                 messagebox.showinfo('Exito', 'Los productos se han introducido con exito')
                 ventana.destroy()
                 cargar_elementos()
            
            except ValueError:
                 messagebox.showerror('Error', 'Las cantidades no fueron correctas')
            except requests.exceptions.HTTPError as ar:
                if ar.response.status_code== 400:
                    messagebox.showerror('Error', 'Faltan campos por rellenar')
                elif ar.response.status_code == 500:
                    messagebox.showerror('Error', 'Se genero un error en la base de datos')
                       
                 
            except Exception:
                 messagebox.showerror('Error', 'Se ejecuto un error en el proceso')
                 
                
     tk.Button(ventana, text= 'Agregar Producto', command= agregar_elemento_lista).grid(row=3, column=0)

def eliminar_elemento_lista():
    #SELECCIONA UN ELEMENTO Y DEVUELVE EL INDICE EN UNA TUPLA, EN CASO DE SELECCIONAR VARIOS DEVULEVE UNA TUPLA CON MAS INDICES
    seleccion= mi_lista.curselection()
    if not seleccion:
            #Mensaje saliente
            messagebox.showwarning("NADA SELECCIONADO.", "SELECCIONA UN PODUCTO.")
            return 
    
    item=  mi_lista.get(seleccion[0])
    id_str= item.split('-')[0]
    try:
        id= int(id_str)
    except ValueError:
        messagebox.showerror("ERROR", "El producto no esta en el formato esperado")
        return
    #Promt de si o no, para confirmar
    if not messagebox.askyesno("Comfirmar", "¿Desea eliminar el producto?"):
        return
    try:

        r= requests.delete(f'{ruta_productos}/{id}')
        #Linea para comprobar en la base que todo salio correcto, nos evita el if==status.code
        r.raise_for_status()

        #Promt de si falla, y obtine el mensaje del json desde la API
        messagebox.showinfo("Elminado", r.json().get('mensaje', 'Producto eliminado'))
        cargar_elementos()

    except Exception as ar:
         messagebox.showerror("ERROR", f"No se pudo eliminar el producto:\n{ar}")    

def modificar_elemento_lista():
    seleccion= mi_lista.curselection()  
    if not seleccion:
            #Mensaje saliente
            messagebox.showwarning("NADA SELECCIONADO.", "SELECCIONA UN PODUCTO.")
        
    texto= entrada2.get()
    if texto and seleccion:
        mi_lista.delete(seleccion[0])
        mi_lista.insert(seleccion[0], texto)
        entrada2.delete(0, tk.END)
        

ventana = tk.Tk()
ventana.title("Menu Principal")

#Label sirve para mostrar texto o imagenes estaticas en la ventana
mi_label= tk.Label(ventana, text= 'Lista de Productos')
mi_label.pack()

#Sirve para mostrar listas
mi_lista= tk.Listbox(ventana, width= 80)
mi_lista.pack()

cargar_elementos()

entrada2= tk.Entry(ventana)
entrada2.pack()

boton2= tk.Button(ventana, text= "Agregar elemento", command= abrir_ventana)
boton2.pack()

boton3= tk.Button(ventana, text= "Borrar elemento", command= eliminar_elemento_lista)
boton3.pack()

boton4= tk.Button(ventana, text= "Modificar elemento", command= modificar_elemento_lista)
boton4.pack()


ventana.mainloop()