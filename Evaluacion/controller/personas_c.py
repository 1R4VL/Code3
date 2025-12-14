import json
import os
from model.personas_m import PacienteModel, MedicoModel, UsuarioModel, AdministradorModel

class UsuarioController:
    def __init__(self, db):
        self.db = db
        self.modelo = UsuarioModel(db)

    def inicio_sesion(self):
        print("\n--- Inicio de Sesión ---")
        usuario = input("Ingrese su nombre de usuario: ")
        clave = input("Ingrese su clave: ")
        
        datos_usuario = self.modelo.obtener_datos_login(usuario)

        if datos_usuario:
            hash_guardado = datos_usuario[0]
            tipo_usuario = datos_usuario[1]
            
            import bcrypt
            if bcrypt.checkpw(clave.encode('utf-8'), hash_guardado.encode('utf-8')):
                print(f"\n[INFO]: Bienvenid@ {usuario} ({tipo_usuario}). Acceso concedido.")
                user_data = self.modelo.ver_usuario(usuario)
                if user_data:
                    return True, {'id': user_data[0], 'nombre_usuario': user_data[1], 'nombre': user_data[2], 'apellido': user_data[3], 'fecha_nacimiento': user_data[4], 'tipo': user_data[5]}
                return True, {'nombre_usuario': usuario, 'tipo': tipo_usuario}
            else:
                print("[ERROR]: Clave incorrecta.")
        else:
            print("[ERROR]: Usuario no encontrado.")
        return False, None

    def crear_usuario(self, permitir_admin=False):
        print("\nCreando usuario nuevo...")
        nombre_user = input("Nombre de usuario: ")
        clave = input("Clave: ")
        nombre = input("Nombre real: ")
        apellido = input("Apellido: ")
        fecha_nac = input("Fecha Nacimiento (YYYY-MM-DD): ")
        
        if permitir_admin:
            tipo = input("Tipo (paciente/medico/administrador): ").lower()
        else:
            tipo = input("Tipo (paciente/medico): ").lower()

        if tipo == "paciente":
            comuna = input("Comuna: ")
            modelo_p = PacienteModel(self.db)
            exito = modelo_p.crear_paciente(nombre_user, clave, nombre, apellido, fecha_nac, comuna, "2024-01-01")
        elif tipo == "medico":
            especialidad = input("Especialidad: ")
            modelo_m = MedicoModel(self.db)
            exito = modelo_m.crear_medico(nombre_user, clave, nombre, apellido, fecha_nac, especialidad, "9-18", "2024-01-01")
        elif tipo == "administrador" and permitir_admin:
            exito = self.modelo.crear_usuario(nombre_user, clave, nombre, apellido, fecha_nac, tipo)
        else:
            print("[ERROR]: Tipo inválido o no autorizado.")
            return

        if exito:
            print("[EXITO]: Usuario creado correctamente.")
        else:
            print("[ERROR]: No se pudo crear. Quizás el usuario ya existe.")

    def cargar_usuarios_json(self):
        """Carga usuarios masivamente desde un archivo JSON."""
        ruta = "datos/usuarios.json"
        
        if not os.path.exists(ruta):
            print(f"[ERROR]: No se encuentra el archivo {ruta}")
            return

        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                usuarios = json.load(archivo)
            
            contador = 0
            for u in usuarios:
                tipo = u.get("tipo")
                if tipo == "paciente":
                    modelo = PacienteModel(self.db)
                    exito = modelo.crear_paciente(
                        u["nombre_usuario"], u["clave"], u["nombre"], u["apellido"], 
                        u["fecha_nacimiento"], u.get("comuna", "Sin Comuna"), "2024-01-01"
                    )
                elif tipo == "medico":
                    modelo = MedicoModel(self.db)
                    exito = modelo.crear_medico(
                        u["nombre_usuario"], u["clave"], u["nombre"], u["apellido"], 
                        u["fecha_nacimiento"], u.get("especialidad", "General"), 
                        "09:00-18:00", "2024-01-01"
                    )
                elif tipo == "administrador":
                    exito = self.modelo.crear_usuario(u["nombre_usuario"], u["clave"], u["nombre"], u["apellido"], u["fecha_nacimiento"], tipo)
                else:
                    exito = False
                
                if exito:
                    contador += 1
            
            print(f"[INFO]: Se cargaron {contador} usuarios desde JSON correctamente.")
            
        except Exception as e:
            print(f"[ERROR]: Fallo al leer JSON: {e}")

    def cargar_usuarios_desde_users_json(self):
        """Carga usuarios de prueba desde users.json con datos reales."""
        rutas_posibles = [
            "datos/users.json",
            "../datos/users.json",
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "datos", "users.json")
        ]
        
        ruta = None
        for r in rutas_posibles:
            if os.path.exists(r):
                ruta = r
                break
        
        if not ruta:
            print(f"[ERROR]: No se encuentra el archivo users.json en las rutas esperadas")
            print(f"Rutas buscadas: {rutas_posibles}")
            return

        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                usuarios = json.load(archivo)
            
            contador = 0
            existentes = 0
            print("\n[INFO]: Cargando usuarios de prueba desde users.json...")
            
            for u in usuarios:
                name_parts = u.get("name", "").split(" ", 1)
                nombre = name_parts[0] if len(name_parts) > 0 else "Usuario"
                apellido = name_parts[1] if len(name_parts) > 1 else "Test"
                nombre_usuario = u.get("username", f"user{u.get('id', contador)}")
                email = u.get("email", "")
                telefono = u.get("phone", "")
                ciudad = u.get("address", {}).get("city", "Sin Ciudad")
                
                if self.modelo.ver_usuario(nombre_usuario):
                    print(f"  ⚠ {nombre_usuario} ya existe en la base de datos")
                    existentes += 1
                    continue
                
                clave = "password123"
                fecha_nac = "1990-01-01"
                
                tipos = ["paciente", "medico", "administrador"]
                tipo = tipos[(contador + existentes) % 3]
                
                try:
                    if tipo == "paciente":
                        modelo = PacienteModel(self.db)
                        exito = modelo.crear_paciente(
                            nombre_usuario, clave, nombre, apellido, 
                            fecha_nac, ciudad, "2024-01-01"
                        )
                        if exito and (email or telefono):
                            self.modelo.actualizar_usuario(nombre_usuario, nombre, apellido, fecha_nac, telefono, email)
                    elif tipo == "medico":
                        modelo = MedicoModel(self.db)
                        exito = modelo.crear_medico(
                            nombre_usuario, clave, nombre, apellido, 
                            fecha_nac, "Medicina General", "09:00-18:00", "2024-01-01"
                        )
                        if exito and (email or telefono):
                            self.modelo.actualizar_usuario(nombre_usuario, nombre, apellido, fecha_nac, telefono, email)
                    else: 
                        exito = self.modelo.crear_usuario(nombre_usuario, clave, nombre, apellido, fecha_nac, tipo)
                        if exito and (email or telefono):
                            self.modelo.actualizar_usuario(nombre_usuario, nombre, apellido, fecha_nac, telefono, email)
                    
                    if exito:
                        contador += 1
                        print(f"  ✓ {nombre_usuario} ({tipo}) - {nombre} {apellido} - {ciudad}")
                except Exception as e:
                    print(f"  ✗ Error con {nombre_usuario}: {e}")
            
            if contador > 0:
                print(f"\n[INFO]: Se cargaron {contador} usuarios nuevos correctamente.")
            if existentes > 0:
                print(f"[INFO]: {existentes} usuarios ya estaban en la base de datos.")
            if contador == 0 and existentes == 0:
                print(f"\n[INFO]: No se cargaron usuarios.")
            
        except Exception as e:
            print(f"[ERROR]: Fallo al leer JSON: {e}")

    def editar_usuario(self, nombre_usuario=None):
        if not nombre_usuario:
            nombre_usuario = input("Nombre de usuario a editar: ").strip()
        
        datos = self.modelo.ver_usuario(nombre_usuario)
        if not datos:
            print("[ERROR]: Usuario no encontrado.")
            return
        
        print("Deja en blanco los campos que no quieras cambiar.")
        nombre_input = input(f"Nombre ({datos[2]}): ").strip()
        apellido_input = input(f"Apellido ({datos[3]}): ").strip()
        
        fecha_actual = str(datos[4]).split()[0] if datos[4] else "No registrada"
        fecha_nac_input = input(f"Fecha Nacimiento ({fecha_actual}): ").strip()
        
        telefono_actual = datos[6] if len(datos) > 6 and datos[6] else None
        email_actual = datos[7] if len(datos) > 7 and datos[7] else None
        
        telefono_display = telefono_actual if telefono_actual else "No registrado"
        email_display = email_actual if email_actual else "No registrado"
        
        telefono_input = input(f"Teléfono ({telefono_display}): ").strip()
        email_input = input(f"Email ({email_display}): ").strip()
        
   
        nombre = nombre_input if nombre_input else datos[2]
        apellido = apellido_input if apellido_input else datos[3]
        fecha_nac = fecha_nac_input if fecha_nac_input else fecha_actual
        telefono = telefono_input if telefono_input else telefono_actual
        email = email_input if email_input else email_actual
        

        hubo_cambios = (nombre != datos[2] or 
                       apellido != datos[3] or 
                       fecha_nac != fecha_actual or 
                       telefono != telefono_actual or 
                       email != email_actual)
        
        if not hubo_cambios:
            print(f"[INFO]: Usuario {nombre_usuario} no fue editado.")
            return
        
        exito = self.modelo.actualizar_usuario(nombre_usuario, nombre, apellido, fecha_nac, telefono, email)
        if exito:
            print("[EXITO]: Usuario actualizado.")
        else:
            print("[ERROR]: No se pudo actualizar.")

    def listar_usuarios_admin(self):
        """Método para que el admin liste todos los usuarios."""
        from view.personas_v import UsuarioView
        admin_model = AdministradorModel(self.db)
        usuario_view = UsuarioView()
        
        usuarios = admin_model.listar_usuarios()
        usuarios_objs = []
        for u in usuarios:
            usuario = UsuarioModel(self.db, id=u[0], nombre_usuario=u[1], nombre=u[2], apellido=u[3], 
                                 fecha_nacimiento=u[4], tipo=u[5], telefono=u[6] if len(u) > 6 else None, 
                                 email=u[7] if len(u) > 7 else None)
            usuarios_objs.append(usuario)
        usuario_view.mostrar_usuarios(usuarios_objs)

    def listar_pacientes_admin(self):
        """Método para que el admin liste todos los pacientes."""
        from view.personas_v import PacienteView
        admin_model = AdministradorModel(self.db)
        paciente_view = PacienteView()
        
        pacientes = admin_model.listar_pacientes()
        if not pacientes:
            print("[INFO]: No hay pacientes registrados.")
            return
            
        print(f"\n[INFO]: Total de pacientes: {len(pacientes)}")
        for p in pacientes:
            paciente = PacienteModel(self.db, id=p[0], nombre_usuario=p[1], nombre=p[2], apellido=p[3], 
                                   fecha_nacimiento=p[4], comuna=p[8] if len(p) > 8 else None, 
                                   fecha_primera_visita=p[9] if len(p) > 9 else None)
            paciente_view.mostrar_paciente(paciente)

    def listar_medicos_admin(self):
        """Método para que el admin liste todos los médicos."""
        from view.personas_v import MedicoView
        admin_model = AdministradorModel(self.db)
        medico_view = MedicoView()
        
        medicos = admin_model.listar_medicos()
        if not medicos:
            print("[INFO]: No hay médicos registrados.")
            return
            
        print(f"\n[INFO]: Total de médicos: {len(medicos)}")
        for m in medicos:
            medico = MedicoModel(self.db, id=m[0], nombre_usuario=m[1], nombre=m[2], apellido=m[3], 
                               fecha_nacimiento=m[4], especialidad=m[8] if len(m) > 8 else None, 
                               horario_atencion=m[9] if len(m) > 9 else None, 
                               fecha_ingreso=m[10] if len(m) > 10 else None)
            medico_view.mostrar_medico(medico)

    def ver_usuario_admin(self, nombre_usuario):
        """Método para que el admin vea detalles de un usuario."""
        from view.personas_v import UsuarioView
        usuario_view = UsuarioView()
        
        datos = self.modelo.ver_usuario(nombre_usuario)
        if datos:
            usuario = UsuarioModel(self.db, id=datos[0], nombre_usuario=datos[1], nombre=datos[2], 
                                 apellido=datos[3], fecha_nacimiento=datos[4], tipo=datos[5], 
                                 telefono=datos[6] if len(datos) > 6 else None, 
                                 email=datos[7] if len(datos) > 7 else None)
            usuario_view.mostrar_usuario(usuario)
        else:
            print("[ERROR]: Usuario no encontrado.")

    def eliminar_usuario_admin(self, nombre_usuario):
        """Método para que el admin elimine un usuario."""
        self.modelo.eliminar_usuario(nombre_usuario)
        print(f"[INFO]: Usuario {nombre_usuario} eliminado.")

    def menu_gestion_usuarios(self):
        """Menú de gestión de usuarios (para admin)."""
        while True:
            print("\n--- Gestión de Usuarios ---")
            print("1. Listar todos los usuarios")
            print("2. Listar pacientes")
            print("3. Listar médicos")
            print("4. Ver detalles de usuario")
            print("5. Crear usuario")
            print("6. Editar usuario")
            print("7. Eliminar usuario")
            print("0. Volver")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                self.listar_usuarios_admin()
            elif opcion == "2":
                self.listar_pacientes_admin()
            elif opcion == "3":
                self.listar_medicos_admin()
            elif opcion == "4":
                nombre_usuario = input("Nombre de usuario: ").strip()
                self.ver_usuario_admin(nombre_usuario)
            elif opcion == "5":
                self.crear_usuario(permitir_admin=True)
            elif opcion == "6":
                nombre = input("Nombre de usuario a editar: ").strip()
                self.editar_usuario(nombre)
            elif opcion == "7":
                nombre = input("Nombre de usuario a eliminar: ").strip()
                self.eliminar_usuario_admin(nombre)
            elif opcion == "0":
                break
            else:
                print("[ERROR]: Opción inválida.")

    def menu_paciente(self, usuario):
        """Menú del paciente con todas sus opciones."""
        from view.personas_v import PacienteView
        from model.objetos_m import RecetasModel, ConsultasModel
        from view.objetos_v import RecetasView, ConsultasView
        
        paciente_view = PacienteView()
        paciente_model = PacienteModel(self.db)
        
        while True:
            print("\n---- Menú Paciente ----")
            print("1) Ver mis datos")
            print("2) Editar mis datos")
            print("3) Ver mis recetas")
            print("4) Ver mis consultas")
            print("0) Cerrar sesión")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                datos = paciente_model.obtener_paciente(usuario['nombre_usuario'])
                if datos:
                    paciente = PacienteModel(self.db, id=datos[0], nombre_usuario=datos[1], nombre=datos[2], 
                                           apellido=datos[3], fecha_nacimiento=datos[4], comuna=datos[5], 
                                           fecha_primera_visita=datos[6])
                    paciente_view.mostrar_paciente(paciente)
                else:
                    print("Datos no encontrados.")
            elif opcion == "2":
                self.editar_usuario(usuario['nombre_usuario'])
            elif opcion == "3":
                recetas_model = RecetasModel(self.db)
                recetas_view = RecetasView()
                recetas = recetas_model.listar_recetas_paciente(usuario['nombre_usuario'])
                recetas_view.mostrar_recetas(recetas)
            elif opcion == "4":
                consultas_model = ConsultasModel(self.db)
                consultas_view = ConsultasView()
                consultas = consultas_model.listar_consultas_paciente(usuario['nombre_usuario'])
                consultas_view.mostrar_consultas(consultas)
            elif opcion == "0":
                print("Cerrando sesión.")
                break
            else:
                print("[ERROR]: Opción inválida.")

    def menu_medico(self, usuario):
        """Menú del médico con todas sus opciones."""
        from view.personas_v import MedicoView
        from model.objetos_m import RecetasModel, ConsultasModel, AgendaModel
        from view.objetos_v import RecetasView, ConsultasView, AgendaView
        
        medico_view = MedicoView()
        medico_model = MedicoModel(self.db)
        
        while True:
            print("\n---- Menú Médico ----")
            print("1) Ver mis datos")
            print("2) Editar mis datos")
            print("3) Gestionar pacientes")
            print("4) Gestionar insumos")
            print("5) Gestionar recetas")
            print("6) Gestionar consultas")
            print("7) Gestionar agenda")
            print("0) Cerrar sesión")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                datos = medico_model.obtener_medico(usuario['nombre_usuario'])
                if datos:
                    medico = MedicoModel(self.db, id=datos[0], nombre_usuario=datos[1], nombre=datos[2], 
                                        apellido=datos[3], fecha_nacimiento=datos[4], 
                                        especialidad=datos[5], horario_atencion=datos[6], fecha_ingreso=datos[7])
                    medico_view.mostrar_medico(medico)
                else:
                    print("Datos no encontrados.")
            elif opcion == "2":
                self.editar_usuario(usuario['nombre_usuario'])
            elif opcion == "3":
                self.menu_gestion_pacientes()
            elif opcion == "4":
                self._menu_gestion_insumos()
            elif opcion == "5":
                datos = medico_model.obtener_medico(usuario['nombre_usuario'])
                if datos:
                    medico = MedicoModel(self.db, id=datos[0], nombre_usuario=datos[1], nombre=datos[2], 
                                        apellido=datos[3], fecha_nacimiento=datos[4], 
                                        especialidad=datos[5], horario_atencion=datos[6], fecha_ingreso=datos[7])
                    self._menu_gestion_recetas(medico)
                else:
                    print("Error al obtener datos del médico.")
            elif opcion == "6":
                datos = medico_model.obtener_medico(usuario['nombre_usuario'])
                if datos:
                    medico = MedicoModel(self.db, id=datos[0], nombre_usuario=datos[1], nombre=datos[2], 
                                        apellido=datos[3], fecha_nacimiento=datos[4], 
                                        especialidad=datos[5], horario_atencion=datos[6], fecha_ingreso=datos[7])
                    self._menu_gestion_consultas(medico)
                else:
                    print("Error al obtener datos del médico.")
            elif opcion == "7":
                datos = medico_model.obtener_medico(usuario['nombre_usuario'])
                if datos:
                    medico = MedicoModel(self.db, id=datos[0], nombre_usuario=datos[1], nombre=datos[2], 
                                        apellido=datos[3], fecha_nacimiento=datos[4], 
                                        especialidad=datos[5], horario_atencion=datos[6], fecha_ingreso=datos[7])
                    self._menu_gestion_agenda(medico)
                else:
                    print("Error al obtener datos del médico.")
            elif opcion == "0":
                print("Cerrando sesión.")
                break
            else:
                print("[ERROR]: Opción inválida.")
    
    def _crear_receta(self, username_medico):
        """Crea una nueva receta."""
        from model.objetos_m import RecetasModel
        recetas_model = RecetasModel(self.db)
        try:
            nombre_paciente = input("Nombre de usuario del paciente: ").strip()
            medicamentos = input("Medicamentos recetados: ").strip()
            recetas_model.crear_receta(nombre_paciente, username_medico, medicamentos)
            print("✓ Receta creada exitosamente.")
        except Exception as e:
            print(f"[ERROR]: {e}")
    
    def _crear_consulta(self, username_medico):
        """Crea una nueva consulta."""
        from model.objetos_m import ConsultasModel
        consultas_model = ConsultasModel(self.db)
        try:
            nombre_paciente = input("Nombre de usuario del paciente: ").strip()
            tipo_consulta = input("Tipo de consulta: ").strip()
            consultas_model.crear_consulta(nombre_paciente, username_medico, tipo_consulta)
            print("✓ Consulta registrada exitosamente.")
        except Exception as e:
            print(f"[ERROR]: {e}")

    def menu_gestion_pacientes(self):
        """Menú para gestionar pacientes (accesible por médicos)."""
        from view.personas_v import PacienteView
        
        paciente_view = PacienteView()
        paciente_model = PacienteModel(self.db)
        
        while True:
            print("\n---- Gestión de Pacientes ----")
            print("1) Listar pacientes")
            print("2) Ver datos de un paciente")
            print("0) Volver")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                pacientes = paciente_model.listar_pacientes()
                for pac in pacientes:
                    paciente = PacienteModel(self.db, id=pac[0], nombre_usuario=pac[1], nombre=pac[2], 
                                           apellido=pac[3], fecha_nacimiento=pac[4], comuna=pac[5])
                    paciente_view.mostrar_paciente(paciente)
            elif opcion == "2":
                nombre_usuario = input("Nombre de usuario del paciente: ").strip()
                datos = paciente_model.obtener_paciente(nombre_usuario)
                if datos:
                    paciente = PacienteModel(self.db, id=datos[0], nombre_usuario=datos[1], nombre=datos[2], 
                                           apellido=datos[3], fecha_nacimiento=datos[4], comuna=datos[5])
                    paciente_view.mostrar_paciente(paciente)
                else:
                    print("Paciente no encontrado.")
            elif opcion == "0":
                break
            else:
                print("[ERROR]: Opción inválida.")

    def menu_administrador(self, usuario):
        """Menú del administrador con todas sus opciones."""
        from view.personas_v import UsuarioView
        
        usuario_view = UsuarioView()
        
        while True:
            print("\n---- Menú Administrador ----")
            print("1) Ver mis datos")
            print("2) Editar mis datos")
            print("3) Gestionar usuarios")
            print("4) Gestionar insumos")
            print("0) Cerrar sesión")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                datos = self.modelo.ver_usuario(usuario['nombre_usuario'])
                if datos:
                    usuario_obj = UsuarioModel(self.db, id=datos[0], nombre_usuario=datos[1], nombre=datos[2], 
                                             apellido=datos[3], fecha_nacimiento=datos[4], tipo=datos[5], 
                                             telefono=datos[6] if len(datos) > 6 else None, 
                                             email=datos[7] if len(datos) > 7 else None)
                    usuario_view.mostrar_usuario(usuario_obj)
                else:
                    print("Datos no encontrados.")
            elif opcion == "2":
                self.editar_usuario(usuario['nombre_usuario'])
            elif opcion == "3":
                self.menu_gestion_usuarios()
            elif opcion == "4":
                self._menu_gestion_insumos()
            elif opcion == "0":
                print("Cerrando sesión.")
                break
            else:
                print("[ERROR]: Opción inválida.")
    
    def _menu_gestion_insumos(self):
        """Menú para gestionar insumos (accesible por administrador)."""
        from controller.objetos_c import ObjetosController
        objetos_controller = ObjetosController(self.db)
        objetos_controller.gestionar_insumos()

    def _menu_gestion_recetas(self, medico):
        """Menú para gestionar recetas (accesible por médicos)."""
        from controller.objetos_c import ObjetosController
        objetos_controller = ObjetosController(self.db)
        objetos_controller.gestionar_recetas(medico)

    def _menu_gestion_consultas(self, medico):
        """Menú para gestionar consultas (accesible por médicos)."""
        from controller.objetos_c import ObjetosController
        objetos_controller = ObjetosController(self.db)
        objetos_controller.gestionar_consultas(medico)

    def _menu_gestion_agenda(self, medico):
        """Menú para gestionar agenda (accesible por médicos)."""
        from controller.objetos_c import ObjetosController
        objetos_controller = ObjetosController(self.db)
        objetos_controller.gestionar_agenda(medico)