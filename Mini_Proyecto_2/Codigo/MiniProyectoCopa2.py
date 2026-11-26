import tkinter as tk
from tkinter import ttk, messagebox
import json
import csv
import os

# Pandas se importa con try para que, si no está instalado, el resto del
# programa siga funcionando y solo el botón del reporte muestre un error.
try:
    import pandas as pd
except ImportError:
    pd = None

# Los archivos se guardan en la misma carpeta donde está este programa.
CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_JSON = "copa_loyola_datos.json"
ARCHIVO_MEDALLERO = "medallero.csv"
ARCHIVO_REPORTE = "reporte_copa_loyola.csv"

universidades = {}
deportistas = {}     
disciplinas = {}    
inscripciones = []   
resultados = []      
resultados_ind = []  # [id_disciplina, id_deportista, posicion]  -- solo disciplinas individuales

visibles = {"uni": [], "dep": [], "dis": [], "ins": [], "res": []}  
opciones = {"uni": {}, "dep": {}, "dis": {}}   

Tipoparticipacion = ["Nacional", "Internacional"]
TipoDoc = ["CC", "TI", "CE", "Pasaporte"]
modalidades = ["Individual", "Por equipos"]
posiciones = ["Oro", "Plata", "Bronce"]
puntos = {"Oro": 3, "Plata": 2, "Bronce": 1}
Numerospos = "0123456789"
Maxtex = 50 
MaxDoc = 15  

def error(mensaje):
    #Entradas: recibe el mensaje que se quiere mostrar.
    #Procedimiento: muestra ese mensaje en una ventanita de error.
    #Salidas:se ve el mensaje en pantalla.
    messagebox.showerror("Error", mensaje)


def texto_correcto(texto, campo, permite_numeros):
#Entradas: recibe el texto escrito, el nombre del campo y si se permiten números o no.
#Procedimiento: revisa que el texto no esté vacío, no sea muy largo, no tenga espacios mal puestos y solo tenga los caracteres permitidos, y si algo falla muestra un mensaje explicando qué pasó.
#Salidas: devuelve verdadero si el texto está bien y falso si tiene algún problema.
    if texto == "":
        error("El campo " + campo + " es obligatorio.")
        return False
    if len (texto) > Maxtex:
        error("El campo " + campo + " no puede tener más de " + str(Maxtex) + " caracteres.")
        return False
    if texto[0] == " " or texto[-1] == " " or "  " in texto:
        error("El campo " + campo + " no puede empezar ni terminar con espacio, ni tener espacios dobles.")
        return False
    tiene_contenido = False
    for c in texto:
        es_letra = c.isalpha()
        es_numero = c in Numerospos
        es_signo = c in " .'-"
        if not (es_letra or es_signo or (permite_numeros and es_numero)):
            if permite_numeros:
                error("El campo " + campo + " solo puede tener letras y números.")
            else:
                error("El campo " + campo + " solo puede tener letras (no números ni símbolos).")
            return False
        if es_letra or es_numero:
            tiene_contenido = True
    if not tiene_contenido:
        error("El campo " + campo + " debe tener al menos una letra o un número.")
        return False
    return True


def documento_correcto(numero, tipo):
#Entradas: recibe el número de documento y el tipo de documento.
#Procedimiento: revisa que no esté vacío, que no sea muy largo y que solo tenga números (o también letras si es pasaporte), y si algo falla muestra un mensaje.
#Salidas: devuelve verdadero si el documento está bien y falso si no.
    if numero == "":
        error("El número de documento es obligatorio.")
        return False
    if len(numero) > MaxDoc:
        error("El número de documento no puede tener más de " + str(MaxDoc) + " caracteres.")
        return False
    for c in numero:
        if c in Numerospos:
            continue
        if tipo == "Pasaporte" and c.isalpha() and c != " ":
            continue
        if tipo == "Pasaporte":
            error("El pasaporte solo puede tener letras y números (sin espacios ni símbolos).")
        else:
            error("El número de documento solo puede tener números.")
        return False
    return True


def repetido(datos, campo, valor, ignorar=None):
#Entradas: recibe los datos guardados, el campo a comparar, el valor buscado y opcionalmente un registro que se debe ignorar.
#Procedimiento: recorre los datos y compara el valor con cada registro sin importar mayúsculas, saltándose el que se debe ignorar.
#Salidas: devuelve verdadero si ya existe algo igual y falso si no.
    for id_, fila in datos.items():
        if id_ != ignorar and fila[campo].lower() == valor.lower():
            return True
    return False


def siguiente_id(datos):
#Entradas: recibe los datos guardados.
#Procedimiento: mira cuál es el número de identificación más alto y le suma uno, o empieza en uno si no hay nada guardado.
#Salidas: devuelve el número que se usará para el nuevo registro.
    if len(datos) == 0:
        return 1
    return max(datos) + 1


def elegido(clave, lista, mensaje):
#Entradas: recibe el tipo de lista, la lista de la pantalla y el mensaje que se mostraría si no se escoge nada.
#Procedimiento: mira qué fila marcó el usuario y busca a qué registro corresponde, y si no marcó ninguna muestra el mensaje.
#Salidas: devuelve el identificador del registro escogido o nada si no se escogió ninguno.
    # curselection() devuelve una tupla con la posición de la fila que el
    # usuario marcó con el clic. Si no marcó nada, la tupla está vacía: ().
    seleccion = lista.curselection()
    if len(seleccion) == 0:
        error(mensaje)
        return None
    return visibles[clave][seleccion[0]]

def vaciar(entradas, combos):
#Entradas: recibe una lista de campos de texto y una lista de cajas de selección.
#Procedimiento: borra lo escrito en cada campo y deja en blanco cada caja de selección.
#Salidas:limpia la pantalla.
    for entrada in entradas:
        entrada.delete(0, tk.END)
    for combo in combos:
        combo.set("")


def mostrar(clave, lista, lineas, ids):
#Entradas: recibe el tipo de lista, la lista de la pantalla, las líneas de texto y los identificadores de cada línea.
#Procedimiento: borra lo que había en la lista de la pantalla, escribe las líneas nuevas y guarda los identificadores para saber a qué registro pertenece cada línea.
#Salidas:actualiza lo que se ve en la lista.
    lista.delete(0, tk.END)
    for linea in lineas:
        lista.insert(tk.END, linea)
    visibles[clave] = ids


def poner_valores(combo, valores, por_defecto=""):
#Entradas: recibe una caja de selección, las opciones nuevas y un valor por defecto.
#Procedimiento: le pone las opciones nuevas a la caja y, si lo que estaba escogido ya no existe, lo cambia por el valor por defecto.
#Salidas: actualiza la caja.
    combo["values"] = valores
    if combo.get() not in valores:
        combo.set(por_defecto)


def llenar_combos():
#Entradas:usa las universidades, deportistas y disciplinas guardadas.
#Procedimiento: arma las opciones con los nombres de lo que existe y se las pone a todas las cajas de selección del programa.
#Salidas: deja las cajas con las opciones al día.
    opciones["uni"] = {}
    for id_, u in universidades.items():
        opciones["uni"][u["nombre"]] = id_
    opciones["dep"] = {}
    for id_, d in deportistas.items():
        opciones["dep"][d["nombre"] + " | " + d["tipo_doc"] + " " + d["numero"]] = id_
    opciones["dis"] = {}
    for id_, d in disciplinas.items():
        opciones["dis"][d["nombre"]] = id_
    nombres_uni = list(opciones["uni"])
    nombres_dis = list(opciones["dis"])
    poner_valores(cmb_dep_uni, nombres_uni)
    poner_valores(cmb_ins_dep, list(opciones["dep"]))
    poner_valores(cmb_ins_dis, nombres_dis)
    poner_valores(cmb_ins_filtro, ["Todas"] + nombres_dis, "Todas")
    poner_valores(cmb_res_dis, nombres_dis)
    poner_valores(cmb_res_uni, nombres_uni)
    poner_valores(cmb_res_dep, list(opciones["dep"]))
    poner_valores(cmb_res_filtro, ["Todas"] + nombres_dis, "Todas")


def refrescar():
#Entradas:usa los datos guardados.
#Procedimiento: vuelve a escribir las listas de universidades, deportistas y disciplinas en pantalla y actualiza las cajas, las inscripciones y los resultados.
#Salidas: actualiza toda la pantalla.
    lineas = []
    ids = []
    for id_, u in universidades.items():
        lineas.append(str(len(lineas) + 1) + ". " + u["nombre"] + " | " + u["pais"] +
                      " | " + u["ciudad"] + " | " + u["tipo"])
        ids.append(id_)
    mostrar("uni", lst_uni, lineas, ids)

    lineas = []
    ids = []
    for id_, d in deportistas.items():
        lineas.append(str(len(lineas) + 1) + ". " + d["nombre"] + " | " + d["tipo_doc"] +
                      " " + d["numero"] + " | " + universidades[d["uni"]]["nombre"])
        ids.append(id_)
    mostrar("dep", lst_dep, lineas, ids)

    lineas = []
    ids = []
    for id_, d in disciplinas.items():
        lineas.append(str(len(lineas) + 1) + ". " + d["nombre"] + " | " + d["modalidad"])
        ids.append(id_)
    mostrar("dis", lst_dis, lineas, ids)

    llenar_combos()
    mostrar_inscripciones()
    mostrar_resultados()


def borrar_campos_uni():
#Entradas: usa los campos del formulario de universidades.
#Procedimiento: limpia el nombre, el país, la ciudad y el tipo de participación.
#Salidas: deja el formulario vacío.
    vaciar([ent_uni_nombre, ent_uni_pais, ent_uni_ciudad], [cmb_uni_tipo])


def leer_universidad(ignorar=None):
#Entradas: recibe el identificador de la universidad que se está editando y usa lo escrito en el formulario.
#Procedimiento: revisa que el nombre, el país, la ciudad y el tipo estén bien escritos y que el nombre no esté repetido, y si algo falla muestra un mensaje.
#Salidas: devuelve los datos de la universidad ya organizados o nada si hubo un error.
    nombre = ent_uni_nombre.get()
    pais = ent_uni_pais.get()
    ciudad = ent_uni_ciudad.get()
    tipo = cmb_uni_tipo.get()
    if not texto_correcto(nombre, "nombre de la universidad", True):
        return None
    if not texto_correcto(pais, "país", False):
        return None
    if not texto_correcto(ciudad, "ciudad", False):
        return None
    if tipo not in Tipoparticipacion:
        error("Seleccione el tipo de participación (Nacional o Internacional).")
        return None
    if repetido(universidades, "nombre", nombre, ignorar):
        error("Ya existe una universidad con ese nombre.")
        return None
    return {"nombre": nombre, "pais": pais, "ciudad": ciudad, "tipo": tipo}


def cargar_universidad(evento=None):
#Entradas: recibe el aviso del clic en la lista, que no se usa, y mira qué universidad se marcó.
#Procedimiento: toma la universidad marcada y escribe sus datos en el formulario.
#Salidas:llena el formulario.
    seleccion = lst_uni.curselection()
    if len(seleccion) == 0:
        return
    u = universidades[visibles["uni"][seleccion[0]]]
    vaciar([ent_uni_nombre, ent_uni_pais, ent_uni_ciudad], [cmb_uni_tipo])
    ent_uni_nombre.insert(0, u["nombre"])
    ent_uni_pais.insert(0, u["pais"])
    ent_uni_ciudad.insert(0, u["ciudad"])
    cmb_uni_tipo.set(u["tipo"])


def crear_universidad():
#Entradas: usa lo escrito en el formulario.
#Procedimiento: si los datos están bien, guarda la universidad con un número nuevo, limpia el formulario y actualiza la pantalla.
#Salidas:agrega la universidad a las guardadas.
    u = leer_universidad()
    if u is not None:
        universidades[siguiente_id(universidades)] = u
        borrar_campos_uni()
        refrescar()


def actualizar_universidad():
#Entradas: usa la universidad marcada y lo escrito en el formulario.
#Procedimiento: revisa los datos nuevos y, si están bien, reemplaza los datos de la universidad marcada, limpia el formulario y actualiza la pantalla.
#Salidas: cambia los datos de esa universidad.
    id_ = elegido("uni", lst_uni, "Seleccione una universidad de la lista para actualizarla.")
    if id_ is None:
        return
    u = leer_universidad(id_)
    if u is not None:
        universidades[id_] = u
        borrar_campos_uni()
        refrescar()


def eliminar_universidad():
#Entradas: usa la universidad marcada en la lista.
#Procedimiento: revisa que no tenga deportistas ni resultados asociados, y si está libre pregunta si de verdad se quiere borrar y, si se acepta, la elimina y actualiza la pantalla.
#Salidas:borra la universidad o muestra un mensaje explicando por qué no se pudo.
    id_ = elegido("uni", lst_uni, "Seleccione una universidad de la lista para eliminarla.")
    if id_ is None:
        return
    for d in deportistas.values():
        if d["uni"] == id_:
            error("No se puede eliminar: la universidad tiene deportistas asociados.")
            return
    for fila in resultados:
        if fila[1] == id_:
            error("No se puede eliminar: la universidad tiene resultados registrados.")
            return
    for dep_id, d in deportistas.items():
        if d["uni"] == id_:
            for fila in resultados_ind:
                if fila[1] == dep_id:
                    error("No se puede eliminar: la universidad tiene resultados individuales registrados.")
                    return
    if messagebox.askyesno("Confirmar", "¿Eliminar la universidad '" + universidades[id_]["nombre"] + "'?"):
        del universidades[id_]
        borrar_campos_uni()
        refrescar()


def borrar_campos_dep():
#Entradas: usa los campos del formulario de deportistas.
#Procedimiento: limpia el nombre, el tipo de documento, el número y la universidad.
#Salidas: vacia el formulario .
    vaciar([ent_dep_nombre, ent_dep_numero], [cmb_dep_tipo, cmb_dep_uni])


def leer_deportista(ignorar=None):
#Entradas: recibe el identificador del deportista que se está editando y usa lo escrito en el formulario.
#Procedimiento: revisa que el nombre, el documento y la universidad estén bien y que no exista otro deportista con el mismo documento, y si algo falla muestra un mensaje.
#Salidas: devuelve los datos del deportista ya organizados o nada si hubo un error.
    nombre = ent_dep_nombre.get()
    tipo = cmb_dep_tipo.get()
    numero = ent_dep_numero.get()
    id_uni = opciones["uni"].get(cmb_dep_uni.get())
    if not texto_correcto(nombre, "nombre completo", False):
        return None
    if tipo not in TipoDoc:
        error("Seleccione el tipo de documento.")
        return None
    if not documento_correcto(numero, tipo):
        return None
    if id_uni is None:
        error("Seleccione la universidad que representa el deportista.")
        return None
    for id_, d in deportistas.items():
        if id_ != ignorar and d["tipo_doc"] == tipo and d["numero"].lower() == numero.lower():
            error("Ya existe un deportista con ese documento.")
            return None
    return {"nombre": nombre, "tipo_doc": tipo, "numero": numero, "uni": id_uni}


def cargar_deportista(evento=None):
#Entradas: recibe el aviso del clic en la lista, que no se usa, y mira qué deportista se marcó.
#Procedimiento: toma el deportista marcado y escribe sus datos en el formulario.
#Salidas: llena el formulario.
    seleccion = lst_dep.curselection()
    if len(seleccion) == 0:
        return
    d = deportistas[visibles["dep"][seleccion[0]]]
    vaciar([ent_dep_nombre, ent_dep_numero], [cmb_dep_tipo, cmb_dep_uni])
    ent_dep_nombre.insert(0, d["nombre"])
    ent_dep_numero.insert(0, d["numero"])
    cmb_dep_tipo.set(d["tipo_doc"])
    cmb_dep_uni.set(universidades[d["uni"]]["nombre"])


def crear_deportista():
#Entradas:datos escritos en el formulario.
#Procedimiento: si los datos están bien, guarda el deportista con un número nuevo, limpia el formulario y actualiza la pantalla.
#Salidas: agrega al deportista a los guardados.
    d = leer_deportista()
    if d is not None:
        deportistas[siguiente_id(deportistas)] = d
        borrar_campos_dep()
        refrescar()


def actualizar_deportista():
#Entradas: deportista marcado y lo escrito en el formulario.
#Procedimiento: revisa los datos nuevos y, si están bien, reemplaza los datos del deportista marcado, limpia el formulario y actualiza la pantalla.
#Salidas:cambia los datos de ese deportista.
    id_ = elegido("dep", lst_dep, "Seleccione un deportista de la lista para actualizarlo.")
    if id_ is None:
        return
    d = leer_deportista(id_)
    if d is not None:
        deportistas[id_] = d
        borrar_campos_dep()
        refrescar()


def eliminar_deportista():
#Entradas: el deportista marcado en la lista.
#Procedimiento: revisa que no tenga inscripciones ni resultados, y si está libre pregunta si de verdad se quiere borrar y, si se acepta, lo elimina y actualiza la pantalla.
#Salidas: borra al deportista o muestra un mensaje explicando por qué no se pudo.
    id_ = elegido("dep", lst_dep, "Seleccione un deportista de la lista para eliminarlo.")
    if id_ is None:
        return
    for fila in inscripciones:
        if fila[0] == id_:
            error("No se puede eliminar: el deportista tiene inscripciones. Elimínelas primero.")
            return
    for fila in resultados_ind:
        if fila[1] == id_:
            error("No se puede eliminar: el deportista tiene resultados individuales registrados. Elimínelos primero.")
            return
    if messagebox.askyesno("Confirmar", "¿Eliminar al deportista '" + deportistas[id_]["nombre"] + "'?"):
        del deportistas[id_]
        borrar_campos_dep()
        refrescar()


def borrar_campos_dis():
#Entradas: los campos del formulario de disciplinas.
#Procedimiento: limpia el nombre y la modalidad.
#Salidas: vacia el formulario.
    vaciar([ent_dis_nombre], [cmb_dis_modalidad])


def leer_disciplina(ignorar=None):
#Entradas: recibe el identificador de la disciplina que se está editando y usa lo escrito en el formulario.
#Procedimiento: revisa que el nombre esté bien escrito, que se haya escogido la modalidad y que el nombre no esté repetido, y si algo falla muestra un mensaje.
#Salidas: devuelve los datos de la disciplina ya organizados o nada si hubo un error.
    nombre = ent_dis_nombre.get()
    modalidad = cmb_dis_modalidad.get()
    if not texto_correcto(nombre, "nombre de la disciplina", True):
        return None
    if modalidad not in modalidades:
        error("Seleccione la modalidad (Individual o Por equipos).")
        return None
    if repetido(disciplinas, "nombre", nombre, ignorar):
        error("Ya existe una disciplina con ese nombre.")
        return None
    return {"nombre": nombre, "modalidad": modalidad}


def cargar_disciplina(evento=None):
#Entradas: recibe el aviso del clic en la lista, que no se usa, y mira qué disciplina se marcó.
#Procedimiento: toma la disciplina marcada y escribe sus datos en el formulario.
#Salidas: no devuelve nada, solo llena el formulario.
    seleccion = lst_dis.curselection()
    if len(seleccion) == 0:
        return
    d = disciplinas[visibles["dis"][seleccion[0]]]
    vaciar([ent_dis_nombre], [cmb_dis_modalidad])
    ent_dis_nombre.insert(0, d["nombre"])
    cmb_dis_modalidad.set(d["modalidad"])


def crear_disciplina():
#Entradas: usa lo escrito en el formulario.
#Procedimiento: si los datos están bien, guarda la disciplina con un número nuevo, limpia el formulario y actualiza la pantalla.
#Salidas: agrega la disciplina a las guardadas.
    d = leer_disciplina()
    if d is not None:
        disciplinas[siguiente_id(disciplinas)] = d
        borrar_campos_dis()
        refrescar()


def actualizar_disciplina():
#Entradas: usa la disciplina marcada y lo escrito en el formulario.
#Procedimiento: revisa los datos nuevos y, si están bien, reemplaza los datos de la disciplina marcada, limpia el formulario y actualiza la pantalla.
#Salidas: cambia los datos de esa disciplina.
    id_ = elegido("dis", lst_dis, "Seleccione una disciplina de la lista para actualizarla.")
    if id_ is None:
        return
    d = leer_disciplina(id_)
    if d is not None:
        disciplinas[id_] = d
        borrar_campos_dis()
        refrescar()


def eliminar_disciplina():
#Entradas: usa la disciplina marcada en la lista.
#Procedimiento: revisa que no tenga inscripciones ni resultados, y si está libre pregunta si de verdad se quiere borrar y, si se acepta, la elimina y actualiza la pantalla.
#Salidas: borra la disciplina o muestra un mensaje explicando por qué no se pudo.
    id_ = elegido("dis", lst_dis, "Seleccione una disciplina de la lista para eliminarla.")
    if id_ is None:
        return
    for fila in inscripciones:
        if fila[1] == id_:
            error("No se puede eliminar: la disciplina tiene inscripciones.")
            return
    for fila in resultados:
        if fila[0] == id_:
            error("No se puede eliminar: la disciplina tiene resultados registrados.")
            return
    for fila in resultados_ind:
        if fila[0] == id_:
            error("No se puede eliminar: la disciplina tiene resultados individuales registrados.")
            return
    if messagebox.askyesno("Confirmar", "¿Eliminar la disciplina '" + disciplinas[id_]["nombre"] + "'?"):
        del disciplinas[id_]
        borrar_campos_dis()
        refrescar()


def mostrar_inscripciones(evento=None):
#Entradas: recibe el aviso del cambio en el filtro, que no se usa, y mira qué disciplina se escogió en el filtro.
#Procedimiento: busca las inscripciones de la disciplina escogida (o de todas) y escribe en la lista el nombre de la disciplina, del deportista y de su universidad.
#Salidas: actualiza la lista de inscripciones en pantalla.
    filtro = opciones["dis"].get(cmb_ins_filtro.get())   # None = todas
    lineas = []
    posiciones_lista = []
    for id_dis, disc in disciplinas.items():
        if filtro is None or filtro == id_dis:
            for i in range(len(inscripciones)):
                if inscripciones[i][1] == id_dis:
                    d = deportistas[inscripciones[i][0]]
                    lineas.append(str(len(lineas) + 1) + ". " + disc["nombre"] + " | " +
                                  d["nombre"] + " | " + universidades[d["uni"]]["nombre"])
                    posiciones_lista.append(i)
    mostrar("ins", lst_ins, lineas, posiciones_lista)


def inscribir_deportista():
#Entradas: el deportista y la disciplina escogidos en las cajas de selección.
#Procedimiento: revisa que se hayan escogido ambos y que el deportista no esté ya inscrito en esa disciplina, y si todo está bien guarda la inscripción y actualiza la pantalla.
#Salidas: agrega la inscripción o muestra un mensaje si hubo un problema.
    id_dep = opciones["dep"].get(cmb_ins_dep.get())
    id_dis = opciones["dis"].get(cmb_ins_dis.get())
    if id_dep is None:
        error("Seleccione un deportista.")
        return
    if id_dis is None:
        error("Seleccione una disciplina.")
        return
    for fila in inscripciones:
        if fila[0] == id_dep and fila[1] == id_dis:
            error("El deportista ya está inscrito en esa disciplina.")
            return
    inscripciones.append([id_dep, id_dis])
    refrescar()


def eliminar_inscripcion():
#Entradas: la inscripción marcada en la lista.
#Procedimiento: pregunta si de verdad se quiere borrar y, si se acepta, elimina la inscripción y actualiza la pantalla.
#Salidas:borra la inscripción.
    pos = elegido("ins", lst_ins, "Seleccione una inscripción de la lista para eliminarla.")
    if pos is None:
        return
    if messagebox.askyesno("Confirmar", "¿Eliminar la inscripción seleccionada?"):
        inscripciones.pop(pos)
        refrescar()


def mostrar_resultados(evento=None):
#Entradas: recibe el aviso del cambio en el filtro que no se usa, y mira qué disciplina se escogió en el filtro.
#Procedimiento: busca los resultados de equipos e individuales de la disciplina escogida y los escribe en la lista ordenados por oro, plata y bronce.
#Salidas:actualiza la lista de resultados en pantalla.
    filtro = opciones["dis"].get(cmb_res_filtro.get())   # None = todas
    lineas = []
    claves = []   # lista de tuplas ("g", indice) o ("i", indice)
    for id_dis, disc in disciplinas.items():
        if filtro is not None and filtro != id_dis:
            continue
        for posicion in posiciones:
            # Resultados grupales (por universidad)
            for i in range(len(resultados)):
                if resultados[i][0] == id_dis and resultados[i][2] == posicion:
                    uni_nombre = universidades[resultados[i][1]]["nombre"]
                    lineas.append("[Equipos] " + disc["nombre"] + " | " +
                                  uni_nombre + " | " + posicion)
                    claves.append(("g", i))
            # Resultados individuales (por deportista)
            for i in range(len(resultados_ind)):
                if resultados_ind[i][0] == id_dis and resultados_ind[i][2] == posicion:
                    dep = deportistas[resultados_ind[i][1]]
                    uni_nombre = universidades[dep["uni"]]["nombre"]
                    lineas.append("[Individual] " + disc["nombre"] + " | " +
                                  dep["nombre"] + " (" + uni_nombre + ") | " + posicion)
                    claves.append(("i", i))
    mostrar("res", lst_res, lineas, claves)


def registrar_resultado():
#Entradas:la disciplina, la posición, el tipo de resultado y la universidad o el deportista escogidos.
#Procedimiento: revisa que todo esté escogido y que la posición no esté ocupada ni repetida, y en el caso individual también que la disciplina sea individual y el deportista esté inscrito, y si todo está bien guarda el resultado y actualiza la pantalla.
#Salidas:agrega el resultado o muestra un mensaje si hubo un problema.
    id_dis = opciones["dis"].get(cmb_res_dis.get())
    posicion = cmb_res_pos.get()
    tipo = cmb_res_tipo.get()
    if id_dis is None:
        error("Seleccione una disciplina que exista.")
        return
    if posicion not in posiciones:
        error("La posición debe ser Oro, Plata o Bronce.")
        return
    if tipo not in ["Por equipos", "Individual"]:
        error("Seleccione el tipo de resultado: Por equipos o Individual.")
        return
    if tipo == "Por equipos":
        id_uni = opciones["uni"].get(cmb_res_uni.get())
        if id_uni is None:
            error("Seleccione una universidad que exista.")
            return
        for fila in resultados:
            if fila[0] == id_dis and fila[2] == posicion:
                error("Esa posición ya está asignada en esta disciplina (equipos).")
                return
            if fila[0] == id_dis and fila[1] == id_uni:
                error("Esa universidad ya tiene una posición en esta disciplina.")
                return
        resultados.append([id_dis, id_uni, posicion])
    else:
        if disciplinas[id_dis]["modalidad"] != "Individual":
            error("Solo se pueden registrar ganadores individuales en disciplinas de modalidad Individual.")
            return
        id_dep = opciones["dep"].get(cmb_res_dep.get())
        if id_dep is None:
            error("Seleccione un deportista que exista.")
            return
        inscrito = False
        for fila in inscripciones:
            if fila[0] == id_dep and fila[1] == id_dis:
                inscrito = True
        if not inscrito:
            error("El deportista no está inscrito en esa disciplina. Inscríbalo primero.")
            return
        for fila in resultados_ind:
            if fila[0] == id_dis and fila[2] == posicion:
                error("Esa posición ya está asignada en esta disciplina (individual).")
                return
            if fila[0] == id_dis and fila[1] == id_dep:
                error("Ese deportista ya tiene una posición en esta disciplina individual.")
                return
        resultados_ind.append([id_dis, id_dep, posicion])
    refrescar()


def eliminar_resultado():
#Entradas:el resultado marcado en la lista.
#Procedimiento: pregunta si de verdad se quiere borrar y, si se acepta, elimina el resultado de la lista de equipos o de la individual según corresponda y actualiza la pantalla.
#Salidas: borra el resultado.
    clave = elegido("res", lst_res, "Seleccione un resultado de la lista para eliminarlo.")
    if clave is None:
        return
    if messagebox.askyesno("Confirmar", "¿Eliminar el resultado seleccionado?"):
        tipo, indice = clave
        if tipo == "g":
            resultados.pop(indice)
        else:
            resultados_ind.pop(indice)
        refrescar()


# RESULTADOS INDIVIDUALES (GANADORES PERSONALES)

def consulta_ganadores_ind():
#Entradas:usa el medallero calculado, los puntos de cada medalla y las universidades guardadas.
#Procedimiento: calcula los puntos de cada universidad (oro 3, plata 2, bronce 1), las ordena de mayor a menor, da el mismo puesto a las que empatan y revisa si hay una sola ganadora o un empate.
#Salidas: devuelve una lista de líneas con la clasificación y la universidad ganadora, o un mensaje diciendo que no hay resultados.

    lineas = []
    for id_dis, disc in disciplinas.items():
        if disc["modalidad"] != "Individual":
            continue
        podio = []
        for posicion in posiciones:
            for fila in resultados_ind:
                if fila[0] == id_dis and fila[2] == posicion:
                    dep = deportistas[fila[1]]
                    uni_nombre = universidades[dep["uni"]]["nombre"]
                    podio.append(posicion + ": " + dep["nombre"] + " (" + uni_nombre + ")")
        if len(podio) > 0:
            lineas.append("--- " + disc["nombre"] + " ---")
            for entrada in podio:
                lineas.append("  " + entrada)
    if len(lineas) == 0:
        lineas.append("No hay resultados individuales registrados.")
    return lineas


def calcular_medallero():
#Entradas: usa las universidades, los resultados por equipos, los resultados individuales y los deportistas guardados.
#Procedimiento: crea un contador de oros, platas y bronces para cada universidad, suma las medallas por equipos y luego las individuales, que se le suman a la universidad del deportista que la ganó.
#Salidas: devuelve un diccionario con la cantidad de medallas de cada tipo por universidad.
    medallero = {}
    for id_ in universidades:
        medallero[id_] = {"Oro": 0, "Plata": 0, "Bronce": 0}
    for fila in resultados:
        medallero[fila[1]][fila[2]] += 1
    for fila in resultados_ind:
        id_uni = deportistas[fila[1]]["uni"]
        medallero[id_uni][fila[2]] += 1
    return medallero


def consulta_deportistas():
#Entradas: los deportistas, universidades, inscripciones y disciplinas guardadas.
#Procedimiento: por cada deportista junta las disciplinas en las que está inscrito y arma una línea con su nombre, universidad, país y disciplinas.
#Salidas: devuelve una lista de líneas con esa información o un mensaje diciendo que no hay deportistas.
    lineas = []
    for id_, d in deportistas.items():
        u = universidades[d["uni"]]
        sus_disciplinas = []
        for fila in inscripciones:
            if fila[0] == id_:
                sus_disciplinas.append(disciplinas[fila[1]]["nombre"])
        if len(sus_disciplinas) == 0:
            texto = "Sin disciplinas"
        else:
            texto = ", ".join(sus_disciplinas)
        lineas.append(d["nombre"] + " | " + u["nombre"] + " | " + u["pais"] + " | " + texto)
    if len(lineas) == 0:
        lineas.append("No hay deportistas registrados.")
    return lineas


def consulta_medallero():
#Entradas: usa el medallero calculado y las universidades guardadas.
#Procedimiento: arma una línea por universidad con su cantidad de oros, platas y bronces.
#Salidas: devuelve una lista de líneas con el medallero o un mensaje diciendo que no hay universidades.
    lineas = []
    medallero = calcular_medallero()
    for id_, m in medallero.items():
        lineas.append(universidades[id_]["nombre"] + " | Oro: " + str(m["Oro"]) +
                      " | Plata: " + str(m["Plata"]) + " | Bronce: " + str(m["Bronce"]))
    if len(lineas) == 0:
        lineas.append("No hay universidades registradas.")
    return lineas


def consulta_ganadora():
#Entradas:el medallero calculado, los puntos de cada medalla y las universidades guardadas.
#Procedimiento: calcula los puntos de cada universidad (oro 3, plata 2, bronce 1), las ordena de mayor a menor, da el mismo puesto a las que empatan y revisa si hay una sola ganadora o un empate.
#Salidas: devuelve una lista de líneas con la clasificación y la universidad ganadora, o un mensaje diciendo que no hay resultados.
    tabla = []
    for id_, m in calcular_medallero().items():
        if m["Oro"] + m["Plata"] + m["Bronce"] > 0:
            puntos_totales = m["Oro"] * puntos["Oro"] + m["Plata"] * puntos["Plata"] + m["Bronce"] * puntos["Bronce"]
            tabla.append([puntos_totales, m["Oro"], m["Plata"], m["Bronce"], universidades[id_]["nombre"]])
    if len(tabla) == 0:
        return ["No hay resultados registrados."]
    tabla.sort(reverse=True)
    lineas = ["Clasificación general"]
    puesto = 0
    for i in range(len(tabla)):
        f = tabla[i]
        if i == 0 or f[:4] != tabla[i - 1][:4]:
            puesto = i + 1
        lineas.append(str(puesto) + ". " + f[4] + " | " + str(f[0]) + " puntos | Oro: " +
                      str(f[1]) + " | Plata: " + str(f[2]) + " | Bronce: " + str(f[3]))
    ganadoras = []
    for f in tabla:
        if f[:4] == tabla[0][:4]:
            ganadoras.append(f[4])
    lineas.append("")
    if len(ganadoras) == 1:
        lineas.append("Universidad ganadora: " + ganadoras[0])
    else:
        lineas.append("Empate total entre: " + ", ".join(ganadoras))
    return lineas


def consulta_estadisticas():
#Entradas: las universidades, deportistas, disciplinas, inscripciones y resultados guardados.
#Procedimiento: cuenta cuántas universidades son nacionales e internacionales y cuántos deportistas, disciplinas, inscripciones y medallas hay (sumando las de equipos y las individuales).
#Salidas: devuelve una lista de seis líneas con esas cantidades.
    nacionales = 0
    for u in universidades.values():
        if u["tipo"] == "Nacional":
            nacionales += 1
    internacionales = len(universidades) - nacionales
    medallas = len(resultados) + len(resultados_ind)
    return ["Estadísticas de la Copa Loyola",
            "Universidades: " + str(len(universidades)),
            "Nacionales: " + str(nacionales) + " | Internacionales: " + str(internacionales),
            "Deportistas: " + str(len(deportistas)) + " | Disciplinas: " + str(len(disciplinas)),
            "Inscripciones: " + str(len(inscripciones)) + " | Medallas: " + str(medallas),
            "Medallas por equipos: " + str(len(resultados)) + " | Medallas individuales: " + str(len(resultados_ind))]


def ejecutar_consulta():
#Entradas: la consulta escogida en la caja de selección.
#Procedimiento: según lo escogido llama a la consulta que corresponde, y si no se escogió ninguna muestra un mensaje; si hay una, muestra el resultado con mostrar_info.
#Salidas: muestra el resultado de la consulta en la lista.
    opcion = cmb_consulta.get()
    if opcion == "Deportistas participantes":
        lineas = consulta_deportistas()
    elif opcion == "Medallero por universidad":
        lineas = consulta_medallero()
    elif opcion == "Universidad ganadora":
        lineas = consulta_ganadora()
    elif opcion == "Estadísticas":
        lineas = consulta_estadisticas()
    elif opcion == "Ganadores individuales":
        lineas = consulta_ganadores_ind()
    else:
        error("Seleccione una consulta.")
        return
    mostrar_info(lineas)


def mostrar_info(lineas):
#Entradas: recibe una lista de líneas de texto.
#Procedimiento: borra lo que había en la lista de la pestaña Consultas y escribe cada línea.
#Salidas: muestra la información en pantalla.
    lst_consulta.delete(0, tk.END)
    for linea in lineas:
        lst_consulta.insert(tk.END, linea)



# MINI PROYECTO 2: MANEJO DE ARCHIVOS (JSON Y CSV)

def ruta(nombre_archivo):
#Entradas: recibe el nombre de un archivo.
#Procedimiento: le pega adelante la carpeta donde está guardado el programa.
#Salidas: devuelve la ruta completa del archivo.
    return os.path.join(CARPETA, nombre_archivo)


def datos_a_json():
#Entradas: usa las universidades, deportistas, disciplinas, inscripciones y resultados guardados.
#Procedimiento: arma un solo diccionario con toda la información; como JSON solo acepta textos como llaves, los identificadores de los diccionarios se pasan a texto.
#Salidas: devuelve el diccionario listo para escribirlo en el archivo JSON.
    datos = {"universidades": {}, "deportistas": {}, "disciplinas": {},
             "inscripciones": [], "resultados": [], "resultados_ind": []}
    for id_, u in universidades.items():
        datos["universidades"][str(id_)] = u
    for id_, d in deportistas.items():
        datos["deportistas"][str(id_)] = d
    for id_, d in disciplinas.items():
        datos["disciplinas"][str(id_)] = d
    for fila in inscripciones:
        datos["inscripciones"].append(list(fila))
    for fila in resultados:
        datos["resultados"].append(list(fila))
    for fila in resultados_ind:
        datos["resultados_ind"].append(list(fila))
    return datos


def es_texto(valor):
#Entradas: recibe cualquier valor.
#Procedimiento: revisa si el valor es un texto que no esté vacío.
#Salidas: devuelve verdadero si es un texto con contenido y falso si no.
    return isinstance(valor, str) and valor.strip() != ""


def validar_estructura(datos):
#Entradas: recibe el diccionario con toda la información (con llaves en texto, como queda en el JSON).
#Procedimiento: revisa que estén las cinco secciones obligatorias (si falta la de resultados individuales la crea vacía), que cada registro tenga sus campos con valores permitidos y que las inscripciones y resultados apunten a universidades, deportistas y disciplinas que sí existen.
#Salidas: devuelve un texto vacío si todo está bien, o un texto explicando el primer problema encontrado.
    if not isinstance(datos, dict):
        return "El archivo no contiene un diccionario con los datos."
    for seccion in ["universidades", "deportistas", "disciplinas", "inscripciones", "resultados"]:
        if seccion not in datos:
            return "Falta la sección '" + seccion + "'."
    if "resultados_ind" not in datos:
        datos["resultados_ind"] = []
    for seccion in ["universidades", "deportistas", "disciplinas"]:
        if not isinstance(datos[seccion], dict):
            return "La sección '" + seccion + "' debe ser un diccionario."
        for id_ in datos[seccion]:
            if not id_.isdigit():
                return "El identificador '" + id_ + "' de " + seccion + " no es un número."
    for seccion in ["inscripciones", "resultados", "resultados_ind"]:
        if not isinstance(datos[seccion], list):
            return "La sección '" + seccion + "' debe ser una lista."

    for id_, u in datos["universidades"].items():
        if not isinstance(u, dict):
            return "La universidad " + id_ + " no tiene un formato válido."
        for campo in ["nombre", "pais", "ciudad"]:
            if not es_texto(u.get(campo)):
                return "La universidad " + id_ + " no tiene un " + campo + " válido."
        if u.get("tipo") not in Tipoparticipacion:
            return "La universidad " + id_ + " tiene un tipo de participación inválido."

    for id_, d in datos["deportistas"].items():
        if not isinstance(d, dict):
            return "El deportista " + id_ + " no tiene un formato válido."
        if not es_texto(d.get("nombre")) or not es_texto(d.get("numero")):
            return "El deportista " + id_ + " no tiene nombre o número de documento válido."
        if d.get("tipo_doc") not in TipoDoc:
            return "El deportista " + id_ + " tiene un tipo de documento inválido."
        if str(d.get("uni")) not in datos["universidades"]:
            return "El deportista " + id_ + " pertenece a una universidad que no existe."

    for id_, d in datos["disciplinas"].items():
        if not isinstance(d, dict):
            return "La disciplina " + id_ + " no tiene un formato válido."
        if not es_texto(d.get("nombre")):
            return "La disciplina " + id_ + " no tiene un nombre válido."
        if d.get("modalidad") not in modalidades:
            return "La disciplina " + id_ + " tiene una modalidad inválida."

    for fila in datos["inscripciones"]:
        if not isinstance(fila, list) or len(fila) != 2:
            return "Hay una inscripción con formato inválido."
        if str(fila[0]) not in datos["deportistas"] or str(fila[1]) not in datos["disciplinas"]:
            return "Hay una inscripción con un deportista o una disciplina que no existe."

    for fila in datos["resultados"]:
        if not isinstance(fila, list) or len(fila) != 3:
            return "Hay un resultado por equipos con formato inválido."
        if str(fila[0]) not in datos["disciplinas"] or str(fila[1]) not in datos["universidades"]:
            return "Hay un resultado por equipos con una disciplina o universidad que no existe."
        if fila[2] not in posiciones:
            return "Hay un resultado por equipos con una medalla inválida."

    for fila in datos["resultados_ind"]:
        if not isinstance(fila, list) or len(fila) != 3:
            return "Hay un resultado individual con formato inválido."
        if str(fila[0]) not in datos["disciplinas"] or str(fila[1]) not in datos["deportistas"]:
            return "Hay un resultado individual con una disciplina o deportista que no existe."
        if fila[2] not in posiciones:
            return "Hay un resultado individual con una medalla inválida."
    return ""


#CONJUNTOS (SETS) PARA DETECTAR DUPLICADOS

def detectar_duplicados(datos):
#Entradas: recibe el diccionario con toda la información (como queda en el JSON).
#Procedimiento: recorre universidades, disciplinas y deportistas guardando en un conjunto (set) el dato que identifica a cada uno (nombre de la universidad, nombre de la disciplina y tipo + número de documento del deportista); si un dato ya estaba en el conjunto, es un repetido. También revisa inscripciones repetidas.
#Salidas: devuelve una lista de líneas con los datos repetidos (vacía si no hay ninguno).
    set_universidades = set()
    set_disciplinas = set()
    set_deportistas = set()
    set_inscripciones = set()
    repetidos = []

    for u in datos["universidades"].values():
        clave = u["nombre"].strip().lower()
        if clave in set_universidades:
            repetidos.append("Universidad: " + u["nombre"])
        set_universidades.add(clave)

    for d in datos["disciplinas"].values():
        clave = d["nombre"].strip().lower()
        if clave in set_disciplinas:
            repetidos.append("Disciplina: " + d["nombre"])
        set_disciplinas.add(clave)

    for d in datos["deportistas"].values():
        clave = d["tipo_doc"] + " " + d["numero"].strip().lower()
        if clave in set_deportistas:
            repetidos.append("Deportista: " + d["nombre"] + " (" + d["tipo_doc"] + " " + d["numero"] + ")")
        set_deportistas.add(clave)

    for fila in datos["inscripciones"]:
        clave = (fila[0], fila[1])
        if clave in set_inscripciones:
            dep = datos["deportistas"][str(fila[0])]["nombre"]
            dis = datos["disciplinas"][str(fila[1])]["nombre"]
            repetidos.append("Inscripción: " + dep + " en " + dis)
        set_inscripciones.add(clave)
    return repetidos


def avisar_duplicados(repetidos):
#Entradas: recibe la lista de datos repetidos.
#Procedimiento: si la lista tiene algo, arma un mensaje con cada repetido y lo muestra como advertencia.
#Salidas: devuelve verdadero si mostró la advertencia y falso si no había repetidos.
    if len(repetidos) == 0:
        return False
    messagebox.showwarning("Registros repetidos",
                           "Se encontraron los siguientes datos repetidos:\n\n- " +
                           "\n- ".join(repetidos))
    return True


def resumen_datos():
#Entradas: usa los datos guardados en el programa.
#Procedimiento: cuenta cuántos registros hay de cada tipo.
#Salidas: devuelve una lista de líneas con las cantidades.
    return ["Universidades: " + str(len(universidades)) + " | Deportistas: " + str(len(deportistas)),
            "Disciplinas: " + str(len(disciplinas)) + " | Inscripciones: " + str(len(inscripciones)),
            "Resultados por equipos: " + str(len(resultados)) +
            " | Resultados individuales: " + str(len(resultados_ind))]


def guardar_datos():
#Entradas: usa toda la información guardada en el programa.
#Procedimiento: arma el diccionario para el JSON, revisa que su estructura sea válida, busca repetidos con conjuntos (y si hay, avisa y pregunta si se quiere guardar igual), escribe el archivo copa_loyola_datos.json con el módulo json y luego genera automáticamente medallero.csv.
#Salidas: crea o reemplaza los archivos y muestra en pantalla si todo salió bien o qué error ocurrió.
    datos = datos_a_json()
    problema = validar_estructura(datos)
    if problema != "":
        error("No se guardaron los datos porque la estructura no es válida:\n" + problema)
        return
    if avisar_duplicados(detectar_duplicados(datos)):
        if not messagebox.askyesno("Confirmar", "¿Desea guardar los datos de todas formas?"):
            return
    try:
        with open(ruta(ARCHIVO_JSON), "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)
    except OSError as e:
        error("No se pudo guardar el archivo " + ARCHIVO_JSON + ":\n" + str(e))
        return
    lineas = ["Datos guardados correctamente.", "Archivo: " + ARCHIVO_JSON] + resumen_datos()
    if generar_medallero_csv(False):
        lineas.append("Medallero exportado en: " + ARCHIVO_MEDALLERO)
    mostrar_info(lineas)
    messagebox.showinfo("Guardar datos", "Los datos se guardaron correctamente en " + ARCHIVO_JSON +
                        " y el medallero en " + ARCHIVO_MEDALLERO + ".")


def reemplazar_datos(datos):
#Entradas: recibe el diccionario leído del JSON, ya validado.
#Procedimiento: borra la información actual del programa y la llena con la del archivo, pasando los identificadores de texto otra vez a números.
#Salidas: deja las estructuras del programa reconstruidas.
    universidades.clear()
    deportistas.clear()
    disciplinas.clear()
    for id_, u in datos["universidades"].items():
        universidades[int(id_)] = {"nombre": u["nombre"], "pais": u["pais"],
                                   "ciudad": u["ciudad"], "tipo": u["tipo"]}
    for id_, d in datos["deportistas"].items():
        deportistas[int(id_)] = {"nombre": d["nombre"], "tipo_doc": d["tipo_doc"],
                                 "numero": d["numero"], "uni": int(d["uni"])}
    for id_, d in datos["disciplinas"].items():
        disciplinas[int(id_)] = {"nombre": d["nombre"], "modalidad": d["modalidad"]}
    inscripciones.clear()
    for fila in datos["inscripciones"]:
        inscripciones.append([int(fila[0]), int(fila[1])])
    resultados.clear()
    for fila in datos["resultados"]:
        resultados.append([int(fila[0]), int(fila[1]), fila[2]])
    resultados_ind.clear()
    for fila in datos["resultados_ind"]:
        resultados_ind.append([int(fila[0]), int(fila[1]), fila[2]])


def cargar_datos():
#Entradas: usa el archivo copa_loyola_datos.json.
#Procedimiento: revisa que el archivo exista, lo lee con el módulo json (manejando el error si está dañado o no se puede leer), valida su estructura, avisa si tiene repetidos, reconstruye los datos del programa y actualiza la pantalla.
#Salidas: carga la información en el programa y muestra si todo salió bien o qué error ocurrió.
    if not os.path.exists(ruta(ARCHIVO_JSON)):
        error("No existe el archivo " + ARCHIVO_JSON + ". Primero guarde los datos.")
        return
    try:
        with open(ruta(ARCHIVO_JSON), "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except json.JSONDecodeError:
        error("El archivo " + ARCHIVO_JSON + " tiene un formato JSON inválido.")
        return
    except (OSError, UnicodeDecodeError) as e:
        error("No se pudo leer el archivo " + ARCHIVO_JSON + ":\n" + str(e))
        return
    problema = validar_estructura(datos)
    if problema != "":
        error("No se cargaron los datos porque la estructura del archivo no es válida:\n" + problema)
        return
    avisar_duplicados(detectar_duplicados(datos))
    if messagebox.askyesno("Confirmar", "Se reemplazará la información actual por la del archivo. ¿Continuar?"):
        reemplazar_datos(datos)
        refrescar()
        mostrar_info(["Datos cargados correctamente.", "Archivo: " + ARCHIVO_JSON] + resumen_datos())
        messagebox.showinfo("Cargar datos", "Los datos se cargaron correctamente.")


def generar_medallero_csv(avisar=True):
#Entradas: recibe si se debe mostrar un mensaje al terminar y usa el medallero calculado.
#Procedimiento: escribe el archivo medallero.csv con el módulo csv, con una fila por universidad con sus oros, platas, bronces, total de medallas y puntos; si ocurre un error lo informa.
#Salidas: devuelve verdadero si el archivo se creó y falso si hubo un error.
    try:
        with open(ruta(ARCHIVO_MEDALLERO), "w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["Universidad", "Oro", "Plata", "Bronce", "Total", "Puntos"])
            for id_, m in calcular_medallero().items():
                total = m["Oro"] + m["Plata"] + m["Bronce"]
                pts = m["Oro"] * puntos["Oro"] + m["Plata"] * puntos["Plata"] + m["Bronce"] * puntos["Bronce"]
                escritor.writerow([universidades[id_]["nombre"], m["Oro"], m["Plata"], m["Bronce"], total, pts])
    except OSError as e:
        error("No se pudo generar el archivo " + ARCHIVO_MEDALLERO + ":\n" + str(e))
        return False
    if avisar:
        mostrar_info(["Medallero exportado correctamente.", "Archivo: " + ARCHIVO_MEDALLERO] +
                     consulta_medallero())
        messagebox.showinfo("Medallero", "El medallero se exportó correctamente en " + ARCHIVO_MEDALLERO + ".")
    return True


# MINI PROYECTO 2: REPORTES CON PANDAS

def crear_dataframe_resultados():
#Entradas: usa los resultados por equipos, los resultados individuales, los deportistas, las universidades y las disciplinas.
#Procedimiento: arma una fila por cada medalla con el nombre de la universidad, el de la disciplina y la medalla; en las medallas individuales la universidad es la del deportista que la ganó. Con esas filas crea un DataFrame.
#Salidas: devuelve el DataFrame con las columnas Universidad, Disciplina y Medalla.
    filas = []
    for fila in resultados:
        filas.append([universidades[fila[1]]["nombre"], disciplinas[fila[0]]["nombre"], fila[2]])
    for fila in resultados_ind:
        id_uni = deportistas[fila[1]]["uni"]
        filas.append([universidades[id_uni]["nombre"], disciplinas[fila[0]]["nombre"], fila[2]])
    return pd.DataFrame(filas, columns=["Universidad", "Disciplina", "Medalla"])


def calcular_reporte(df):
#Entradas: recibe el DataFrame de resultados.
#Procedimiento: con Pandas agrupa por universidad y medalla y cuenta cuántas hay de cada tipo, calcula los puntos (oro 3, plata 2, bronce 1) y ordena de mayor a menor por puntos, y en empate por oros, platas y bronces.
#Salidas: devuelve un DataFrame con las columnas Universidad, Oro, Plata, Bronce y Puntos.
    conteo = df.groupby(["Universidad", "Medalla"]).size().unstack(fill_value=0)
    conteo = conteo.reindex(columns=posiciones, fill_value=0)
    conteo["Puntos"] = (conteo["Oro"] * puntos["Oro"] + conteo["Plata"] * puntos["Plata"] +
                        conteo["Bronce"] * puntos["Bronce"])
    conteo = conteo.sort_values(by=["Puntos", "Oro", "Plata", "Bronce"], ascending=False)
    tabla = conteo.reset_index()
    tabla.columns.name = None
    return tabla


def buscar_ganadoras(tabla):
#Entradas: recibe el DataFrame del reporte ya ordenado.
#Procedimiento: toma la primera fila y busca todas las universidades que tengan los mismos puntos, oros, platas y bronces que ella.
#Salidas: devuelve la lista de universidades ganadoras (más de una si hay empate total).
    primera = tabla.iloc[0]
    iguales = tabla[(tabla["Puntos"] == primera["Puntos"]) & (tabla["Oro"] == primera["Oro"]) &
                    (tabla["Plata"] == primera["Plata"]) & (tabla["Bronce"] == primera["Bronce"])]
    return list(iguales["Universidad"])


def exportar_reporte_csv(tabla, avisar=True):
#Entradas: recibe el DataFrame del reporte y si se debe mostrar un mensaje al terminar.
#Procedimiento: exporta el DataFrame al archivo reporte_copa_loyola.csv con Pandas y, si ocurre un error, lo informa.
#Salidas: devuelve verdadero si el archivo se creó y falso si hubo un error.
    try:
        tabla.to_csv(ruta(ARCHIVO_REPORTE), index=False, encoding="utf-8-sig")
    except OSError as e:
        error("No se pudo exportar el archivo " + ARCHIVO_REPORTE + ":\n" + str(e))
        return False
    if avisar:
        messagebox.showinfo("Exportar CSV", "El reporte se exportó correctamente en " + ARCHIVO_REPORTE + ".")
    return True


def mostrar_ventana_reporte(tabla, ganadoras):
#Entradas: recibe el DataFrame del reporte y la lista de universidades ganadoras.
#Procedimiento: abre una ventana nueva (Toplevel) con una tabla de universidades, medallas y puntos, la universidad ganadora y botones para exportar a CSV y cerrar.
#Salidas: muestra la ventana del reporte.
    ventana_rep = tk.Toplevel(ventana)
    ventana_rep.title("Reporte con Pandas")
    ventana_rep.geometry("560x380")
    ttk.Label(ventana_rep, text="Reporte: resultados de la Copa Loyola",
              font=("Arial", 13, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
    ttk.Label(ventana_rep, text="Agrupación: universidad | Oro = 3, Plata = 2, Bronce = 1 punto").pack(anchor="w", padx=12)

    columnas = ["Universidad", "Oro", "Plata", "Bronce", "Puntos"]
    arbol = ttk.Treeview(ventana_rep, columns=columnas, show="headings", height=8)
    for col in columnas:
        arbol.heading(col, text=col)
        if col == "Universidad":
            arbol.column(col, width=240, anchor="w")
        else:
            arbol.column(col, width=60, anchor="center")
    for i in range(len(tabla)):
        f = tabla.iloc[i]
        arbol.insert("", tk.END, values=[f["Universidad"], int(f["Oro"]), int(f["Plata"]),
                                         int(f["Bronce"]), int(f["Puntos"])])
    arbol.pack(fill="both", expand=True, padx=12, pady=8)

    if len(ganadoras) == 1:
        texto = "Universidad ganadora: " + ganadoras[0]
    else:
        texto = "Empate total entre: " + ", ".join(ganadoras)
    ttk.Label(ventana_rep, text=texto, font=("Arial", 11, "bold")).pack()
    crear_botones(ventana_rep, [["Exportar CSV", lambda: exportar_reporte_csv(tabla)],
                                ["Cerrar", ventana_rep.destroy]])


def generar_reporte():
#Entradas: usa los resultados guardados en el programa.
#Procedimiento: revisa que Pandas esté instalado y que haya resultados, crea el DataFrame de resultados, calcula el conteo de medallas y los puntos por universidad, busca la ganadora, exporta el reporte a CSV y lo muestra en una ventana nueva.
#Salidas: crea reporte_copa_loyola.csv, abre la ventana del reporte y muestra en pantalla si salió bien o qué error ocurrió.
    if pd is None:
        error("No se encontró la biblioteca Pandas.\nInstálela con: pip install pandas")
        return
    if len(resultados) + len(resultados_ind) == 0:
        error("No hay resultados registrados para generar el reporte.")
        return
    try:
        df = crear_dataframe_resultados()
        tabla = calcular_reporte(df)
        ganadoras = buscar_ganadoras(tabla)
    except Exception as e:
        error("Ocurrió un error al generar el reporte:\n" + str(e))
        return
    exportado = exportar_reporte_csv(tabla, False)
    lineas = ["Reporte generado con Pandas.", "Universidad | Oro | Plata | Bronce | Puntos"]
    for i in range(len(tabla)):
        f = tabla.iloc[i]
        lineas.append(f["Universidad"] + " | " + str(f["Oro"]) + " | " + str(f["Plata"]) +
                      " | " + str(f["Bronce"]) + " | " + str(f["Puntos"]))
    if len(ganadoras) == 1:
        lineas.append("Universidad ganadora: " + ganadoras[0])
    else:
        lineas.append("Empate total entre: " + ", ".join(ganadoras))
    if exportado:
        lineas.append("Reporte exportado en: " + ARCHIVO_REPORTE)
    mostrar_info(lineas)
    mostrar_ventana_reporte(tabla, ganadoras)
    if exportado:
        messagebox.showinfo("Reporte", "El reporte se generó correctamente y se exportó en " +
                            ARCHIVO_REPORTE + ".")



def crear_formulario(padre, titulo):
#Entradas: recibe la pestaña donde se va a crear y el título.
#Procedimiento: crea un espacio a la izquierda de la pestaña y le pone el título arriba.
#Salidas: devuelve ese espacio para poder agregarle campos.
    form = ttk.Frame(padre)
    form.pack(side="left", fill="y", padx=15, pady=10)
    ttk.Label(form, text=titulo, font=("Arial", 14, "bold")).pack(anchor="w")
    return form


def crear_lista(padre, titulo):
#Entradas: recibe la pestaña donde se va a crear y el título.
#Procedimiento: crea un espacio a la derecha con un título, una lista y una barra para desplazarse hacia arriba y abajo.
#Salidas: devuelve la lista creada.
    marco = ttk.Frame(padre)
    marco.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    ttk.Label(marco, text=titulo, font=("Arial", 10, "bold")).pack(anchor="w")
    interior = ttk.Frame(marco)
    interior.pack(fill="both", expand=True)
    barra = ttk.Scrollbar(interior, orient="vertical")
    lista = tk.Listbox(interior, yscrollcommand=barra.set, exportselection=False, activestyle="none")
    barra.config(command=lista.yview)
    barra.pack(side="right", fill="y")
    lista.pack(side="left", fill="both", expand=True)
    return lista


def crear_entry(form, texto):
#Entradas: recibe el formulario donde se va a agregar y el texto de la etiqueta.
#Procedimiento: pone una etiqueta con ese texto y debajo un campo para escribir.
#Salidas: devuelve el campo para escribir.
    ttk.Label(form, text=texto).pack(anchor="w", pady=(8, 0))
    entry = ttk.Entry(form, width=32)
    entry.pack(anchor="w")
    return entry


def crear_combo(form, texto, valores):
#Entradas: recibe el formulario donde se va a agregar, el texto de la etiqueta y las opciones.
#Procedimiento: pone una etiqueta con ese texto y debajo una caja de selección con las opciones.
#Salidas: devuelve la caja de selección.
    ttk.Label(form, text=texto).pack(anchor="w", pady=(8, 0))
    combo = ttk.Combobox(form, values=valores, state="readonly", width=30)
    combo.pack(anchor="w")
    return combo


def crear_botones(form, botones):
#Entradas: recibe el formulario donde se va a agregar y la lista de botones con su texto y lo que hacen.
#Procedimiento: crea una fila y pone un botón por cada elemento de la lista, conectado a su acción.
#Salidas: deja los botones en el formulario.
    fila = ttk.Frame(form)
    fila.pack(anchor="w", pady=14)
    for texto, comando in botones:
        ttk.Button(fila, text=texto, command=comando).pack(side="left", padx=3)



ventana = tk.Tk()
ventana.title("Copa Loyola - Sistema de Gestión Deportiva")
ventana.geometry("950x560")
ventana.minsize(850, 520)
notebook = ttk.Notebook(ventana)
notebook.pack(fill="both", expand=True, padx=8, pady=8)

#   Universidades
tab = ttk.Frame(notebook)
notebook.add(tab, text="Universidades")
form = crear_formulario(tab, "Universidades")
ent_uni_nombre = crear_entry(form, "Nombre de la universidad")
ent_uni_pais = crear_entry(form, "País")
ent_uni_ciudad = crear_entry(form, "Ciudad")
cmb_uni_tipo = crear_combo(form, "Tipo de participación", Tipoparticipacion)
crear_botones(form, [["Crear", crear_universidad], ["Actualizar", actualizar_universidad],
                     ["Eliminar", eliminar_universidad]])
lst_uni = crear_lista(tab, "Universidades registradas")
lst_uni.bind("<<ListboxSelect>>", cargar_universidad)

#       Deportistas
tab = ttk.Frame(notebook)
notebook.add(tab, text="Deportistas")
form = crear_formulario(tab, "Deportistas")
ent_dep_nombre = crear_entry(form, "Nombre completo")
cmb_dep_tipo = crear_combo(form, "Tipo de documento", TipoDoc)
ent_dep_numero = crear_entry(form, "Número de documento")
cmb_dep_uni = crear_combo(form, "Universidad", [])
crear_botones(form, [["Crear", crear_deportista], ["Actualizar", actualizar_deportista],
                     ["Eliminar", eliminar_deportista]])
lst_dep = crear_lista(tab, "Deportistas registrados")
lst_dep.bind("<<ListboxSelect>>", cargar_deportista)

#       Disciplinas
tab = ttk.Frame(notebook)
notebook.add(tab, text="Disciplinas")
form = crear_formulario(tab, "Disciplinas")
ent_dis_nombre = crear_entry(form, "Nombre de la disciplina")
cmb_dis_modalidad = crear_combo(form, "Modalidad", modalidades)
crear_botones(form, [["Crear", crear_disciplina], ["Actualizar", actualizar_disciplina],
                     ["Eliminar", eliminar_disciplina]])
lst_dis = crear_lista(tab, "Disciplinas registradas")
lst_dis.bind("<<ListboxSelect>>", cargar_disciplina)

#       Inscripciones
tab = ttk.Frame(notebook)
notebook.add(tab, text="Inscripciones")
form = crear_formulario(tab, "Inscripciones")
cmb_ins_dep = crear_combo(form, "Seleccionar deportista", [])
cmb_ins_dis = crear_combo(form, "Seleccionar disciplina", [])
cmb_ins_filtro = crear_combo(form, "Filtrar por disciplina", ["Todas"])
cmb_ins_filtro.set("Todas")
cmb_ins_filtro.bind("<<ComboboxSelected>>", mostrar_inscripciones)
crear_botones(form, [["Inscribir", inscribir_deportista], ["Eliminar", eliminar_inscripcion]])
lst_ins = crear_lista(tab, "Inscripciones por disciplina")

#       Resultados
tab = ttk.Frame(notebook)
notebook.add(tab, text="Resultados")
form = crear_formulario(tab, "Resultados")
cmb_res_dis = crear_combo(form, "Seleccionar disciplina", [])
cmb_res_tipo = crear_combo(form, "Tipo de resultado", ["Por equipos", "Individual"])
cmb_res_uni = crear_combo(form, "Universidad (equipos)", [])
cmb_res_dep = crear_combo(form, "Deportista (individual)", [])
cmb_res_pos = crear_combo(form, "Posición obtenida", posiciones)
cmb_res_filtro = crear_combo(form, "Ver resultados de", ["Todas"])
cmb_res_filtro.set("Todas")
cmb_res_filtro.bind("<<ComboboxSelected>>", mostrar_resultados)
crear_botones(form, [["Registrar", registrar_resultado], ["Eliminar", eliminar_resultado]])
lst_res = crear_lista(tab, "Todos los resultados")

#       Consultas / Archivos / Reportes
tab = ttk.Frame(notebook)
notebook.add(tab, text="Consultas / Archivos / Reportes")
form = crear_formulario(tab, "Consultas / Archivos / Reportes")
cmb_consulta = crear_combo(form, "Seleccione la consulta",
                           ["Deportistas participantes", "Medallero por universidad",
                            "Universidad ganadora", "Estadísticas",
                            "Ganadores individuales"])
crear_botones(form, [["Consultar", ejecutar_consulta]])
ttk.Separator(form, orient="horizontal").pack(fill="x", pady=4)
ttk.Label(form, text="Acción de almacenamiento", font=("Arial", 10, "bold")).pack(anchor="w")
ttk.Label(form, text="Archivo: " + ARCHIVO_JSON).pack(anchor="w")
crear_botones(form, [["Guardar datos (JSON)", guardar_datos], ["Cargar datos (JSON)", cargar_datos]])
crear_botones(form, [["Medallero (CSV)", generar_medallero_csv]])
ttk.Separator(form, orient="horizontal").pack(fill="x", pady=4)
ttk.Label(form, text="Reporte con Pandas", font=("Arial", 10, "bold")).pack(anchor="w")
crear_botones(form, [["Generar Reporte con Pandas", generar_reporte]])
lst_consulta = crear_lista(tab, "Información / resultados")

refrescar()
ventana.mainloop()
