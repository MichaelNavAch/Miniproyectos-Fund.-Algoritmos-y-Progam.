import tkinter as tk
from tkinter import ttk, messagebox

universidades = {}  
deportistas = {}     
disciplinas = {}    
inscripciones = []   
resultados = []      
resultados_ind = []  # [id_disciplina, id_deportista, posicion]  -- solo disciplinas individuales

visibles = {"uni": [], "dep": [], "dis": [], "ins": [], "res": []}  
opciones = {"uni": {}, "dep": {}, "dis": {}}   

TIPOS_PARTICIPACION = ["Nacional", "Internacional"]
TIPOS_DOCUMENTO = ["CC", "TI", "CE", "Pasaporte"]
MODALIDADES = ["Individual", "Por equipos"]
POSICIONES = ["Oro", "Plata", "Bronce"]
PUNTOS = {"Oro": 3, "Plata": 2, "Bronce": 1}
DIGITOS = "0123456789"
MAX_TEXTO = 50 
MAX_DOCUMENTO = 15  

def error(mensaje):

    messagebox.showerror("Error", mensaje)


def texto_correcto(texto, campo, permite_numeros):
    if texto == "":
        error("El campo " + campo + " es obligatorio.")
        return False
    if len (texto) > MAX_TEXTO:
        error("El campo " + campo + " no puede tener más de " + str(MAX_TEXTO) + " caracteres.")
        return False
    if texto[0] == " " or texto[-1] == " " or "  " in texto:
        error("El campo " + campo + " no puede empezar ni terminar con espacio, ni tener espacios dobles.")
        return False
    tiene_contenido = False
    for c in texto:
        es_letra = c.isalpha()
        es_numero = c in DIGITOS
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

    if numero == "":
        error("El número de documento es obligatorio.")
        return False
    if len(numero) > MAX_DOCUMENTO:
        error("El número de documento no puede tener más de " + str(MAX_DOCUMENTO) + " caracteres.")
        return False
    for c in numero:
        if c in DIGITOS:
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

    for id_, fila in datos.items():
        if id_ != ignorar and fila[campo].lower() == valor.lower():
            return True
    return False


def siguiente_id(datos):

    if len(datos) == 0:
        return 1
    return max(datos) + 1


def elegido(clave, lista, mensaje):

    # curselection() devuelve una tupla con la posición de la fila que el
    # usuario marcó con el clic. Si no marcó nada, la tupla está vacía: ().
    seleccion = lista.curselection()
    if len(seleccion) == 0:
        error(mensaje)
        return None
    return visibles[clave][seleccion[0]]


def vaciar(entradas, combos):

    for entrada in entradas:
        entrada.delete(0, tk.END)
    for combo in combos:
        combo.set("")


def mostrar(clave, lista, lineas, ids):

    lista.delete(0, tk.END)
    for linea in lineas:
        lista.insert(tk.END, linea)
    visibles[clave] = ids


def poner_valores(combo, valores, por_defecto=""):

    combo["values"] = valores
    if combo.get() not in valores:
        combo.set(por_defecto)


def llenar_combos():

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

    vaciar([ent_uni_nombre, ent_uni_pais, ent_uni_ciudad], [cmb_uni_tipo])


def leer_universidad(ignorar=None):

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
    if tipo not in TIPOS_PARTICIPACION:
        error("Seleccione el tipo de participación (Nacional o Internacional).")
        return None
    if repetido(universidades, "nombre", nombre, ignorar):
        error("Ya existe una universidad con ese nombre.")
        return None
    return {"nombre": nombre, "pais": pais, "ciudad": ciudad, "tipo": tipo}


def cargar_universidad(evento=None):

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

    u = leer_universidad()
    if u is not None:
        universidades[siguiente_id(universidades)] = u
        borrar_campos_uni()
        refrescar()


def actualizar_universidad():

    id_ = elegido("uni", lst_uni, "Seleccione una universidad de la lista para actualizarla.")
    if id_ is None:
        return
    u = leer_universidad(id_)
    if u is not None:
        universidades[id_] = u
        borrar_campos_uni()
        refrescar()


def eliminar_universidad():

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

    vaciar([ent_dep_nombre, ent_dep_numero], [cmb_dep_tipo, cmb_dep_uni])


def leer_deportista(ignorar=None):

    nombre = ent_dep_nombre.get()
    tipo = cmb_dep_tipo.get()
    numero = ent_dep_numero.get()
    id_uni = opciones["uni"].get(cmb_dep_uni.get())
    if not texto_correcto(nombre, "nombre completo", False):
        return None
    if tipo not in TIPOS_DOCUMENTO:
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

    d = leer_deportista()
    if d is not None:
        deportistas[siguiente_id(deportistas)] = d
        borrar_campos_dep()
        refrescar()


def actualizar_deportista():

    id_ = elegido("dep", lst_dep, "Seleccione un deportista de la lista para actualizarlo.")
    if id_ is None:
        return
    d = leer_deportista(id_)
    if d is not None:
        deportistas[id_] = d
        borrar_campos_dep()
        refrescar()


def eliminar_deportista():

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

    vaciar([ent_dis_nombre], [cmb_dis_modalidad])


def leer_disciplina(ignorar=None):

    nombre = ent_dis_nombre.get()
    modalidad = cmb_dis_modalidad.get()
    if not texto_correcto(nombre, "nombre de la disciplina", True):
        return None
    if modalidad not in MODALIDADES:
        error("Seleccione la modalidad (Individual o Por equipos).")
        return None
    if repetido(disciplinas, "nombre", nombre, ignorar):
        error("Ya existe una disciplina con ese nombre.")
        return None
    return {"nombre": nombre, "modalidad": modalidad}


def cargar_disciplina(evento=None):

    seleccion = lst_dis.curselection()
    if len(seleccion) == 0:
        return
    d = disciplinas[visibles["dis"][seleccion[0]]]
    vaciar([ent_dis_nombre], [cmb_dis_modalidad])
    ent_dis_nombre.insert(0, d["nombre"])
    cmb_dis_modalidad.set(d["modalidad"])


def crear_disciplina():

    d = leer_disciplina()
    if d is not None:
        disciplinas[siguiente_id(disciplinas)] = d
        borrar_campos_dis()
        refrescar()


def actualizar_disciplina():

    id_ = elegido("dis", lst_dis, "Seleccione una disciplina de la lista para actualizarla.")
    if id_ is None:
        return
    d = leer_disciplina(id_)
    if d is not None:
        disciplinas[id_] = d
        borrar_campos_dis()
        refrescar()


def eliminar_disciplina():

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

    filtro = opciones["dis"].get(cmb_ins_filtro.get())   # None = todas
    lineas = []
    posiciones = []
    for id_dis, disc in disciplinas.items():
        if filtro is None or filtro == id_dis:
            for i in range(len(inscripciones)):
                if inscripciones[i][1] == id_dis:
                    d = deportistas[inscripciones[i][0]]
                    lineas.append(str(len(lineas) + 1) + ". " + disc["nombre"] + " | " +
                                  d["nombre"] + " | " + universidades[d["uni"]]["nombre"])
                    posiciones.append(i)
    mostrar("ins", lst_ins, lineas, posiciones)


def inscribir_deportista():

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

    pos = elegido("ins", lst_ins, "Seleccione una inscripción de la lista para eliminarla.")
    if pos is None:
        return
    if messagebox.askyesno("Confirmar", "¿Eliminar la inscripción seleccionada?"):
        inscripciones.pop(pos)
        refrescar()


def mostrar_resultados(evento=None):
    """
    Entradas: evento del combobox de filtro (no se usa directamente).
    Salidas: ninguna.
    Procedimiento: recorre ambas matrices (resultados y resultados_ind) y
    muestra todas las filas que coincidan con el filtro de disciplina
    elegido, ordenadas por disciplina y luego por posición (Oro, Plata,
    Bronce). Cada elemento guardado en visibles["res"] es una tupla
    ("g", i) para resultados grupales o ("i", i) para individuales, donde
    i es el índice real en la matriz correspondiente; así eliminar_resultado
    sabe de qué lista quitar la fila sin ambigüedad.
    """
    filtro = opciones["dis"].get(cmb_res_filtro.get())   # None = todas
    lineas = []
    claves = []   # lista de tuplas ("g", indice) o ("i", indice)
    for id_dis, disc in disciplinas.items():
        if filtro is not None and filtro != id_dis:
            continue
        for posicion in POSICIONES:
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
    """
    Entradas: disciplina, posición y —según el tipo elegido— universidad
              (cmb_res_uni) o deportista (cmb_res_dep). El tipo se lee de
              cmb_res_tipo ("Por equipos" o "Individual").
    Salidas: ninguna.
    Procedimiento: valida que la disciplina y la posición existan; si el
    tipo es "Por equipos" valida y guarda en resultados (igual que antes);
    si es "Individual" valida que la disciplina sea de modalidad Individual,
    que el deportista esté inscrito en ella y que no tenga ya una posición
    en esa disciplina, luego guarda en resultados_ind. En ambos casos
    verifica que la posición no esté ya ocupada en la disciplina y refresca.
    """
    id_dis = opciones["dis"].get(cmb_res_dis.get())
    posicion = cmb_res_pos.get()
    tipo = cmb_res_tipo.get()
    if id_dis is None:
        error("Seleccione una disciplina que exista.")
        return
    if posicion not in POSICIONES:
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
    """
    Entradas: línea seleccionada en el Listbox lst_res.
    Salidas: ninguna.
    Procedimiento: obtiene la tupla (tipo, indice) guardada en
    visibles["res"]; si el tipo es "g" elimina de resultados, si es "i"
    elimina de resultados_ind; pide confirmación antes de borrar y luego
    refresca la interfaz.
    """
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


# ----------------------------------------------------------------------
# RESULTADOS INDIVIDUALES (GANADORES PERSONALES)
# ----------------------------------------------------------------------
def consulta_ganadores_ind():
    """
    Entradas: ninguna (usa los datos globales resultados_ind, disciplinas,
              deportistas y universidades).
    Salidas: lista de líneas de texto con la clasificación de ganadores
             individuales por disciplina, ordenada Oro → Plata → Bronce.
    Procedimiento: recorre todas las disciplinas de modalidad Individual
    que tengan al menos un resultado registrado en resultados_ind, y para
    cada una muestra el podio en orden Oro, Plata, Bronce indicando el
    nombre del deportista y su universidad. Si no hay resultados individuales
    registrados, devuelve un mensaje informativo.
    """
    lineas = []
    for id_dis, disc in disciplinas.items():
        if disc["modalidad"] != "Individual":
            continue
        podio = []
        for posicion in POSICIONES:
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

    medallero = {}
    for id_ in universidades:
        medallero[id_] = {"Oro": 0, "Plata": 0, "Bronce": 0}
    for fila in resultados:
        medallero[fila[1]][fila[2]] += 1
    return medallero


def consulta_deportistas():

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

    lineas = []
    medallero = calcular_medallero()
    for id_, m in medallero.items():
        lineas.append(universidades[id_]["nombre"] + " | Oro: " + str(m["Oro"]) +
                      " | Plata: " + str(m["Plata"]) + " | Bronce: " + str(m["Bronce"]))
    if len(lineas) == 0:
        lineas.append("No hay universidades registradas.")
    return lineas


def consulta_ganadora():

    tabla = []
    for id_, m in calcular_medallero().items():
        if m["Oro"] + m["Plata"] + m["Bronce"] > 0:
            puntos = m["Oro"] * PUNTOS["Oro"] + m["Plata"] * PUNTOS["Plata"] + m["Bronce"] * PUNTOS["Bronce"]
            tabla.append([puntos, m["Oro"], m["Plata"], m["Bronce"], universidades[id_]["nombre"]])
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

    nacionales = 0
    for u in universidades.values():
        if u["tipo"] == "Nacional":
            nacionales += 1
    return ["Estadísticas de la Copa Loyola",
            "Universidades: " + str(len(universidades)),
            "Nacionales: " + str(nacionales) + " | Internacionales: " + str(len(universidades) - nacionales),
            "Deportistas: " + str(len(deportistas)) + " | Disciplinas: " + str(len(disciplinas)),
            "Inscripciones: " + str(len(inscripciones)) + " | Medallas: " + str(len(resultados))]


def ejecutar_consulta():

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
    lst_consulta.delete(0, tk.END)
    for linea in lineas:
        lst_consulta.insert(tk.END, linea)



def crear_formulario(padre, titulo):

    form = ttk.Frame(padre)
    form.pack(side="left", fill="y", padx=15, pady=10)
    ttk.Label(form, text=titulo, font=("Arial", 14, "bold")).pack(anchor="w")
    return form


def crear_lista(padre, titulo):

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

    ttk.Label(form, text=texto).pack(anchor="w", pady=(8, 0))
    entry = ttk.Entry(form, width=32)
    entry.pack(anchor="w")
    return entry


def crear_combo(form, texto, valores):

    ttk.Label(form, text=texto).pack(anchor="w", pady=(8, 0))
    combo = ttk.Combobox(form, values=valores, state="readonly", width=30)
    combo.pack(anchor="w")
    return combo


def crear_botones(form, botones):

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
cmb_uni_tipo = crear_combo(form, "Tipo de participación", TIPOS_PARTICIPACION)
crear_botones(form, [["Crear", crear_universidad], ["Actualizar", actualizar_universidad],
                     ["Eliminar", eliminar_universidad]])
lst_uni = crear_lista(tab, "Universidades registradas")
lst_uni.bind("<<ListboxSelect>>", cargar_universidad)

#       Deportistas
tab = ttk.Frame(notebook)
notebook.add(tab, text="Deportistas")
form = crear_formulario(tab, "Deportistas")
ent_dep_nombre = crear_entry(form, "Nombre completo")
cmb_dep_tipo = crear_combo(form, "Tipo de documento", TIPOS_DOCUMENTO)
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
cmb_dis_modalidad = crear_combo(form, "Modalidad", MODALIDADES)
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
cmb_res_pos = crear_combo(form, "Posición obtenida", POSICIONES)
cmb_res_filtro = crear_combo(form, "Ver resultados de", ["Todas"])
cmb_res_filtro.set("Todas")
cmb_res_filtro.bind("<<ComboboxSelected>>", mostrar_resultados)
crear_botones(form, [["Registrar", registrar_resultado], ["Eliminar", eliminar_resultado]])
lst_res = crear_lista(tab, "Todos los resultados")

#       Consultas
tab = ttk.Frame(notebook)
notebook.add(tab, text="Consultas")
form = crear_formulario(tab, "Consultas")
cmb_consulta = crear_combo(form, "Seleccione la consulta",
                           ["Deportistas participantes", "Medallero por universidad",
                            "Universidad ganadora", "Estadísticas",
                            "Ganadores individuales"])
crear_botones(form, [["Consultar", ejecutar_consulta]])
lst_consulta = crear_lista(tab, "Resultado de la consulta")

refrescar()
ventana.mainloop()