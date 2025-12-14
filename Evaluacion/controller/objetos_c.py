import re
from model.objetos_m import InsumosModel, RecetasModel, ConsultasModel, AgendaModel
from model.personas_m import PacienteModel, MedicoModel
from view.objetos_v import InsumosView, RecetasView, ConsultasView, AgendaView

SUS_KEYS = [
    r";", r"--", r"/\*", r"\bOR\b", r"\bAND\b", r"\bUNION\b",
    r"\bSELECT\b", r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b",
    r"\bDROP\b", r"\bEXEC\b"
]

patron = re.compile("|".join(SUS_KEYS), re.IGNORECASE)

class ObjetosController:
    """Controlador para gestionar insumos, recetas, consultas y agenda con vistas."""

    def __init__(self, db):
        self.db = db
        self.insumos_view = InsumosView()
        self.recetas_view = RecetasView()
        self.consultas_view = ConsultasView()
        self.agenda_view = AgendaView()


    def gestionar_insumos(self):
        """Gestión de Insumos"""
        while True:
            print("\n--- Gestión de Insumos ---")
            print("1. Crear insumo")
            print("2. Listar insumos")
            print("3. Eliminar insumo")
            print("4. Actualizar stock")
            print("0. Volver")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                nombre = input("Nombre del insumo: ").strip()
                tipo = input("Tipo: ").strip()
                try:
                    stock = int(input("Stock inicial: ").strip())
                    costo_usd = float(input("Costo en USD: ").strip())
                except ValueError:
                    print("[ERROR]: Valores numéricos inválidos para stock o costo.")
                    continue
                insumo = InsumosModel(self.db, nombre=nombre, tipo=tipo, stock=stock, costo_usd=costo_usd)
                insumo.crear_insumo()

            elif opcion == "2":
                insumo = InsumosModel(self.db)
                lista = insumo.listar_insumos()
                self.insumos_view.mostrar_insumos(lista)

            elif opcion == "3":
                try:
                    id_insumo = int(input("ID del insumo a eliminar: ").strip())
                except ValueError:
                    print("[ERROR]: ID inválido.")
                    continue
                insumo = InsumosModel(self.db, id=id_insumo)
                insumo.eliminar_insumo()

            elif opcion == "4":
                try:
                    id_insumo = int(input("ID del insumo a actualizar: ").strip())
                    nuevo_stock = int(input("Nuevo stock: ").strip())
                except ValueError:
                    print("[ERROR]: Valores inválidos.")
                    continue
                insumo = InsumosModel(self.db, id=id_insumo)
                insumo.actualizar_stock(nuevo_stock)

            elif opcion == "0":
                break
            else:
                print("[ERROR]: Opción inválida.")

    def cargar_insumos_json(self):
        """Carga insumos desde datos/insumos.json y los inserta en BD."""
        import json
        import os
        ruta = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datos', 'insumos.json')
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("[ERROR]: No se encuentra el archivo datos/insumos.json")
            return
        except Exception as e:
            print(f"[ERROR]: No se pudo leer el JSON → {e}")
            return

        cargados = 0
        for item in data:
            try:
                nombre = item.get('nombre')
                tipo = item.get('tipo')
                stock = int(item.get('stock') or 0)
                costo_usd = float(item.get('costo_usd') or 0.0)
                insumo = InsumosModel(self.db, nombre=nombre, tipo=tipo, stock=stock, costo_usd=costo_usd)
                if insumo.crear_insumo():
                    cargados += 1
            except Exception as e:
                print(f"[WARN]: No se pudo cargar insumo '{item}': {e}")

        print(f"[INFO]: Carga completada. Insumos insertados: {cargados}")


    def gestionar_recetas(self, medico: MedicoModel):
        """Gestión de Recetas"""
        while True:
            print("\n--- Gestión de Recetas ---")
            print("1. Crear receta")
            print("2. Ver receta por ID")
            print("3. Eliminar receta")
            print("4. Listar todas las recetas")
            print("5. Asociar insumo a receta")
            print("0. Volver")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                try:
                    id_paciente = int(input("ID del paciente: ").strip())
                    costo_clp = float(input("Costo en CLP: ").strip())
                except ValueError:
                    print("[ERROR]: ID o costo inválido.")
                    continue
                descripcion = input("Descripción de la receta: ").strip()
                medicamentos = input("Medicamentos recetados: ").strip()
                paciente = PacienteModel(self.db, id=id_paciente)
                receta = RecetasModel(self.db, paciente=paciente, medico=medico, descripcion=descripcion, medicamentos_recetados=medicamentos, costo_clp=costo_clp)
                receta.crear_receta()

            elif opcion == "2":
                try:
                    id_receta = int(input("ID de la receta: ").strip())
                except ValueError:
                    print("[ERROR]: ID inválido.")
                    continue
                receta_model = RecetasModel(self.db)
                datos = receta_model.obtener_receta(id_receta)
                if datos:
                    receta_obj = RecetasModel(self.db, id=datos[0],
                                              paciente=PacienteModel(self.db, id=datos[1]),
                                              medico=MedicoModel(self.db, id=datos[2]),
                                              descripcion=datos[3], medicamentos_recetados=datos[4], costo_clp=datos[5])
                    self.recetas_view.mostrar_receta(receta_obj)
                else:
                    print("[ERROR]: Receta no encontrada.")

            elif opcion == "3":
                try:
                    id_receta = int(input("ID de la receta a eliminar: ").strip())
                except ValueError:
                    print("[ERROR]: ID inválido.")
                    continue
                receta = RecetasModel(self.db)
                receta.eliminar_receta(id_receta)

            elif opcion == "4":
                receta_model = RecetasModel(self.db)
                lista = receta_model.listar_recetas()
                self.recetas_view.mostrar_recetas(lista)

            elif opcion == "5":
           
                insumo_model = InsumosModel(self.db)
                disponibles = insumo_model.listar_insumos()
                if disponibles:
                    print("\n[INFO]: Insumos disponibles (ID - Nombre - Tipo - Stock):")
                    for ins in disponibles:
                        print(f"  {ins.id} - {ins.nombre} - {ins.tipo} - stock: {ins.stock}")
                try:
                    id_receta = int(input("ID de la receta: ").strip())
                    id_insumo = int(input("ID del insumo: ").strip())
                    cantidad = int(input("Cantidad: ").strip())
                except ValueError:
                    print("[ERROR]: Valores inválidos.")
                    continue
                receta_model = RecetasModel(self.db)
                datos = receta_model.obtener_receta(id_receta)
                if not datos:
                    print("[ERROR]: Receta no encontrada.")
                else:
                
                    insumo_validacion = None
                    for ins in disponibles:
                        if ins.id == id_insumo:
                            insumo_validacion = ins
                            break
                    receta_obj = RecetasModel(self.db, id=datos[0])
                    if receta_obj.agregar_insumo(id_insumo, cantidad):
                        if insumo_validacion:
                            print(f"[INFO]: Asociado '{insumo_validacion.nombre}' (ID {id_insumo}) a receta {id_receta}.")
                        else:
                            print(f"[INFO]: Insumo ID {id_insumo} asociado a receta {id_receta}.")

            elif opcion == "0":
                break
            else:
                print("[ERROR]: Opción inválida.")


    def gestionar_consultas(self, medico: MedicoModel):
        """Gestión de Consultas"""
        while True:
            print("\n--- Gestión de Consultas ---")
            print("1. Crear consulta")
            print("2. Listar todas las consultas")
            print("0. Volver")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                try:
                    id_paciente = int(input("ID del paciente: ").strip())
                    id_receta = input("ID de la receta (opcional): ").strip()
                    id_receta = int(id_receta) if id_receta else None
                    valor = float(input("Valor en CLP: ").strip())
                except ValueError:
                    print("[ERROR]: Valores inválidos.")
                    continue
                fecha = input("Fecha de la consulta (YYYY-MM-DD): ").strip()
                comentarios = input("Comentarios: ").strip()

                paciente = PacienteModel(self.db, id=id_paciente)
                receta = RecetasModel(self.db, id=id_receta) if id_receta else None
                consulta = ConsultasModel(self.db, paciente=paciente, medico=medico,
                                          receta=receta, fecha=fecha, comentarios=comentarios, valor=valor)
                consulta.crear_consulta()

            elif opcion == "2":
                consulta_model = ConsultasModel(self.db)
                lista = consulta_model.listar_consultas()
                self.consultas_view.mostrar_consultas(lista)

            elif opcion == "0":
                break
            else:
                print("[ERROR]: Opción inválida.")


    def gestionar_agenda(self, medico: MedicoModel):
        """ Gestion de la Agenda Médica"""
        while True:
            print("\n--- Agenda Médica ---")
            print("1. Agendar consulta")
            print("2. Actualizar estado de consulta")
            print("3. Listar toda la agenda")
            print("0. Volver")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                try:
                    id_paciente = int(input("ID del paciente: ").strip())
                except ValueError:
                    print("[ERROR]: ID inválido.")
                    continue
                fecha_consulta = input("Fecha de consulta (YYYY-MM-DD): ").strip()
                estado = "pendiente"
                paciente = PacienteModel(self.db, id=id_paciente)
                agenda = AgendaModel(self.db, paciente=paciente, medico=medico,
                                     fecha_consulta=fecha_consulta, estado=estado)
                agenda.agendar_consulta()

            elif opcion == "2":
                try:
                    id_agenda = int(input("ID de la agenda: ").strip())
                except ValueError:
                    print("[ERROR]: ID inválido.")
                    continue
                nuevo_estado = input("Nuevo estado (pendiente/realizada/cancelada): ").strip()
                agenda = AgendaModel(self.db, id=id_agenda)
                agenda.actualizar_estado(nuevo_estado)

            elif opcion == "3":
                agenda_model = AgendaModel(self.db)
                lista = agenda_model.listar_agenda()
                self.agenda_view.mostrar_agendas(lista)

            elif opcion == "0":
                break
            else:
                print("[ERROR]: Opción inválida.")
