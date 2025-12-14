from model.personas_m import PacienteModel, MedicoModel

class InsumosModel:
    """Modelo de los Insumos Médicos."""

    def __init__(self, db, id=None, nombre=None, tipo=None, stock=0, costo_usd= 0.0 or None):
        """Inicializa un insumo con sus atributos básicos."""
        self.db = db
        self.id = id
        self.nombre = nombre
        self.tipo = tipo
        self.stock = stock
        self.costo_usd = costo_usd
    
    def crear_insumo(self) -> bool:
        """Crea un nuevo insumo médico en la base de datos."""
        cursor = self.db.obtener_cursor()
        consulta = """INSERT INTO rr_insumos (nombre,tipo,stock,costo_usd) VALUES (:1, :2, :3, :4)"""
        try:
            cursor.execute(consulta, (self.nombre, self.tipo, self.stock, self.costo_usd))
            self.db.connection.commit()
            print(f"[INFO]: Insumo '{self.nombre}' creado correctamente.")
            return True
        except Exception as e:
            print(f"[ERROR]: No se pudo crear el insumo. {e}")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def listar_insumos(self):
        """Obtiene y devuelve todos los insumos médicos registrados."""
        cursor = self.db.obtener_cursor()
        consulta = """SELECT id, nombre, tipo, stock, costo_usd FROM rr_insumos"""
        try:
            cursor.execute(consulta)
            insumos = cursor.fetchall()
            lista_insumos = []
            for insumo in insumos:
                lista_insumos.append(InsumosModel(self.db, insumo[0], insumo[1], insumo[2], insumo[3], insumo[4]))
            return lista_insumos
        except Exception as e:
            print(f"[ERROR]: No se pudo listar los insumos. {e}")
            return []
        finally:
            cursor.close()
        
    def eliminar_insumo(self) -> bool:
        """Elimina un insumo médico por su ID."""
        cursor = self.db.obtener_cursor()
        consulta = """DELETE FROM rr_insumos WHERE id = :1"""
        try:
            cursor.execute(consulta, (self.id,))
            self.db.connection.commit()
            print(f"[INFO]: Insumo con ID '{self.id}' eliminado correctamente.")
            return True
        except Exception as e:
            print(f"[ERROR]: No se pudo eliminar el insumo. {e}")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()

    def actualizar_stock(self, nuevo_stock: int) -> bool:
        """Actualiza el stock de un insumo."""
        cursor = self.db.obtener_cursor()
        consulta = """UPDATE rr_insumos SET stock = :1 WHERE id = :2"""
        try:
            cursor.execute(consulta, (nuevo_stock, self.id))
            self.db.connection.commit()
            print(f"[INFO]: Stock del insumo ID '{self.id}' actualizado a {nuevo_stock}.")
            return True
        except Exception as e:
            print(f"[ERROR]: No se pudo actualizar el stock. {e}")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()


class RecetasModel:
    """Modelo de las Recetas Médicas."""

    def __init__(self, db, id=None, paciente: PacienteModel=None, medico: MedicoModel=None, descripcion=None, medicamentos_recetados=None, costo_clp=0.0, insumos=None):
        self.db = db
        self.id = id
        self.paciente = paciente
        self.medico = medico
        self.descripcion = descripcion
        self.medicamentos_recetados = medicamentos_recetados
        self.costo_clp = costo_clp
        self.insumos = insumos if insumos else []  

    def crear_receta(self) -> bool:
        cursor = self.db.obtener_cursor()
        try:
           
            consulta_receta = """INSERT INTO rr_recetas (id_paciente, id_medico, descripcion, medicamentos_recetados, costo_clp)
                                 VALUES (:1, :2, :3, :4, :5) RETURNING id INTO :6"""
            id_var = cursor.var(int)
            cursor.execute(consulta_receta, (self.paciente.id, self.medico.id, self.descripcion, self.medicamentos_recetados, self.costo_clp, id_var))
            self.id = id_var.getvalue()[0]

          

            self.db.connection.commit()
            print(f"[INFO]: Receta creada correctamente con ID {self.id}.")
            return True
        except Exception as e:
            print(f"[ERROR]: No se pudo crear la receta -> {e}.")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()

    def obtener_insumos(self):
        cursor = self.db.obtener_cursor()
        consulta = """
            SELECT i.id, i.nombre, i.tipo, i.stock, i.costo_usd, ri.cantidad
            FROM rr_receta_insumos ri
            JOIN rr_insumos i ON ri.id_insumo = i.id
            WHERE ri.id_receta = :1
        """
        try:
            cursor.execute(consulta, (self.id,))
            filas = cursor.fetchall()
            insumos = []
            for fila in filas:
                insumo = InsumosModel(self.db, id=fila[0], nombre=fila[1], tipo=fila[2], stock=fila[3], costo_usd=fila[4])
                insumos.append((insumo, fila[5]))
            return insumos
        except Exception as e:
            print(f"[ERROR]: No se pudieron obtener insumos de la receta -> {e}.")
            return []
        finally:
            cursor.close()

    def agregar_insumo(self, id_insumo:int, cantidad:int=1) -> bool:
        if not self.id:
            print("[ERROR]: La receta debe existir antes de asociar insumos.")
            return False
        cursor = self.db.obtener_cursor()
        consulta = """
            INSERT INTO rr_receta_insumos (id_receta, id_insumo, cantidad)
            VALUES (:1, :2, :3)
        """
        try:
            cursor.execute(consulta, (self.id, id_insumo, cantidad))
            self.db.connection.commit()
            print(f"[INFO]: Insumo {id_insumo} agregado a receta {self.id} (cantidad {cantidad}).")
            return True
        except Exception as e:
            print(f"[ERROR]: No se pudo asociar el insumo -> {e}.")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def obtener_receta(self, id_receta:int):
        """Obtiene una receta médica por su ID."""
        cursor = self.db.obtener_cursor()
        consulta = "SELECT id, id_paciente, id_medico, descripcion, medicamentos_recetados, costo_clp FROM rr_recetas WHERE id=:1"
        try:
            cursor.execute(consulta, (id_receta,))
            return cursor.fetchone()
        except Exception as e:
            print(f"[ERROR]: No se pudo obtener la receta -> {e}.")
            return None
        finally:
            cursor.close()
    
    def eliminar_receta(self, id_receta:int) -> bool:
        """Elimina una receta médica por su ID."""
        cursor = self.db.obtener_cursor()
        consulta = "DELETE FROM rr_recetas WHERE id=:1"
        try:
            cursor.execute(consulta, (id_receta,))
            if cursor.rowcount > 0:
                self.db.connection.commit()
                print(f"[INFO]: Receta con ID '{id_receta}' eliminada correctamente.")
                return True
            else:
                print(f"[ERROR]: No se encontró receta con ID '{id_receta}'.")
                return False
        except Exception as e:
            print(f"[ERROR]: No se pudo eliminar la receta. {e}")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()
            
    def listar_recetas_paciente(self, nombre_usuario: str):
        """Lista todas las recetas asociadas a un paciente por su nombre de usuario."""
        cursor = self.db.obtener_cursor()
        consulta = """
            SELECT r.id, r.descripcion, r.medicamentos_recetados, r.costo_clp, r.id_medico, u.id, u.nombre_usuario
            FROM rr_recetas r
            JOIN rr_paciente p ON r.id_paciente = p.id_paciente
            JOIN rr_usuario u ON p.id_paciente = u.id
            WHERE u.nombre_usuario = :1
        """
        try:
            cursor.execute(consulta, (nombre_usuario.strip(),))
            resultados = cursor.fetchall()
            recetas = []
            for fila in resultados:
                receta = RecetasModel(
                    self.db,
                    id=fila[0],
                    descripcion=fila[1],
                    medicamentos_recetados=fila[2],
                    costo_clp=fila[3],
                    medico=MedicoModel(self.db, id=fila[4]),
                    paciente=PacienteModel(self.db, id=fila[5], nombre_usuario=fila[6])
                )
                recetas.append(receta)
            return recetas
        except Exception as e:
            print(f"[ERROR]: No se pudieron listar las recetas del paciente -> {e}.")
            return []
        finally:
            cursor.close()

    def listar_recetas(self):
        """Lista todas las recetas."""
        cursor = self.db.obtener_cursor()
        consulta = """
            SELECT r.id, r.id_paciente, r.id_medico, r.descripcion, r.medicamentos_recetados, r.costo_clp,
                   u.nombre_usuario as paciente_usuario, u.nombre as paciente_nombre, u.apellido as paciente_apellido,
                   m.nombre_usuario as medico_usuario, m.nombre as medico_nombre, m.apellido as medico_apellido
            FROM rr_recetas r
            JOIN rr_usuario u ON r.id_paciente = u.id
            JOIN rr_usuario m ON r.id_medico = m.id
            ORDER BY r.id
        """
        try:
            cursor.execute(consulta)
            resultados = cursor.fetchall()
            recetas = []
            for fila in resultados:
                receta = RecetasModel(
                    self.db,
                    id=fila[0],
                    descripcion=fila[3],
                    medicamentos_recetados=fila[4],
                    costo_clp=fila[5],
                    paciente=PacienteModel(self.db, id=fila[1], nombre_usuario=fila[6], nombre=fila[7], apellido=fila[8]),
                    medico=MedicoModel(self.db, id=fila[2], nombre_usuario=fila[9], nombre=fila[10], apellido=fila[11])
                )
                recetas.append(receta)
            return recetas
        except Exception as e:
            print(f"[ERROR]: No se pudieron listar las recetas -> {e}.")
            return []
        finally:
            cursor.close()



class ConsultasModel:
    """Modelo de las Consultas Médicas."""

    def __init__(self, db, id=None, paciente: PacienteModel=None, medico: MedicoModel=None, receta: RecetasModel=None, fecha=None, comentarios=None, valor=0.0):
        """Inicializa una consulta con paciente, médico, receta, fecha y comentarios."""
        self.db = db
        self.id = id
        self.paciente = paciente
        self.medico = medico
        self.receta = receta
        self.fecha = fecha
        self.comentarios = comentarios
        self.valor = valor
    
    def crear_consulta(self) -> bool: 
        """Crea una nueva consulta médica en la base de datos."""
        cursor = self.db.obtener_cursor()
        consulta = """
            INSERT INTO rr_consultas (id_paciente, id_medico, id_receta, fecha, comentarios, valor)
            VALUES (:id_paciente, :id_medico, :id_receta, TO_DATE(:fecha, 'YYYY-MM-DD'), :comentarios, :valor)
        """
        try:
            cursor.execute(consulta, {
                'id_paciente': self.paciente.id,
                'id_medico': self.medico.id,
                'id_receta': self.receta.id if self.receta else None,
                'fecha': self.fecha,
                'comentarios': self.comentarios,
                'valor': self.valor
            })
            self.db.connection.commit()
            print(f"[INFO]: Consulta creada correctamente.")
            return True
        except Exception as e:
            print(f"[ERROR]: No se pudo crear la consulta -> {e}.")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()

    def listar_consultas(self):
        """Lista todas las consultas."""
        cursor = self.db.obtener_cursor()
        consulta = """
            SELECT c.id, c.id_paciente, c.id_medico, c.id_receta, c.fecha, c.comentarios, c.valor,
                   u.nombre_usuario as paciente_usuario, u.nombre as paciente_nombre, u.apellido as paciente_apellido,
                   m.nombre_usuario as medico_usuario, m.nombre as medico_nombre, m.apellido as medico_apellido
            FROM rr_consultas c
            JOIN rr_usuario u ON c.id_paciente = u.id
            JOIN rr_usuario m ON c.id_medico = m.id
            ORDER BY c.fecha DESC
        """
        try:
            cursor.execute(consulta)
            resultados = cursor.fetchall()
            consultas = []
            for fila in resultados:
                consulta_obj = ConsultasModel(
                    self.db,
                    id=fila[0],
                    fecha=fila[4],
                    comentarios=fila[5],
                    valor=fila[6],
                    paciente=PacienteModel(self.db, id=fila[1], nombre_usuario=fila[7], nombre=fila[8], apellido=fila[9]),
                    medico=MedicoModel(self.db, id=fila[2], nombre_usuario=fila[10], nombre=fila[11], apellido=fila[12]),
                    receta=RecetasModel(self.db, id=fila[3]) if fila[3] else None
                )
                consultas.append(consulta_obj)
            return consultas
        except Exception as e:
            print(f"[ERROR]: No se pudieron listar las consultas -> {e}.")
            return []
        finally:
            cursor.close()

    def listar_consultas_paciente(self, nombre_usuario: str):
        """Lista todas las consultas asociadas a un paciente por su nombre de usuario."""
        cursor = self.db.obtener_cursor()
        consulta = """
            SELECT c.id, c.id_paciente, c.id_medico, c.id_receta, c.fecha, c.comentarios, c.valor,
                   u.nombre_usuario as paciente_usuario, u.nombre as paciente_nombre, u.apellido as paciente_apellido,
                   m.nombre_usuario as medico_usuario, m.nombre as medico_nombre, m.apellido as medico_apellido
            FROM rr_consultas c
            JOIN rr_usuario u ON c.id_paciente = u.id
            JOIN rr_usuario m ON c.id_medico = m.id
            WHERE u.nombre_usuario = :1
            ORDER BY c.fecha DESC
        """
        try:
            cursor.execute(consulta, (nombre_usuario.strip(),))
            resultados = cursor.fetchall()
            consultas = []
            for fila in resultados:
                consulta_obj = ConsultasModel(
                    self.db,
                    id=fila[0],
                    fecha=fila[4],
                    comentarios=fila[5],
                    valor=fila[6],
                    paciente=PacienteModel(self.db, id=fila[1], nombre_usuario=fila[7], nombre=fila[8], apellido=fila[9]),
                    medico=MedicoModel(self.db, id=fila[2], nombre_usuario=fila[10], nombre=fila[11], apellido=fila[12]),
                    receta=RecetasModel(self.db, id=fila[3]) if fila[3] else None
                )
                consultas.append(consulta_obj)
            return consultas
        except Exception as e:
            print(f"[ERROR]: No se pudieron listar las consultas del paciente -> {e}.")
            return []
        finally:
            cursor.close()


class AgendaModel:
    """Modelo de la Agenda Médica."""

    def __init__(self, db, id=None, paciente:PacienteModel=None, medico:MedicoModel=None, fecha_consulta=None, estado=None):
        """Inicializa la agenda con paciente, médico, fecha y estado."""
        self.db = db
        self.id = id
        self.paciente = paciente
        self.medico = medico
        self.fecha_consulta = fecha_consulta
        self.estado = estado
        
    def agendar_consulta(self) -> bool:
        """Agrega una nueva consulta a la agenda."""
        cursor = self.db.obtener_cursor()
        consulta = """
            INSERT INTO rr_agenda (id_paciente, id_medico, fecha_consulta, estado)
            VALUES (:id_paciente, :id_medico, TO_DATE(:fecha_consulta, 'YYYY-MM-DD'), :estado)
        """
        try:
            cursor.execute(consulta, {
                'id_paciente': self.paciente.id,
                'id_medico': self.medico.id,
                'fecha_consulta': self.fecha_consulta,
                'estado': self.estado
            })
            self.db.connection.commit()
            print(f"[INFO]: Consulta agendada correctamente.")
            return True
        except Exception as e:
            print(f"[ERROR]: No se pudo agendar la consulta -> {e}.")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()

    def actualizar_estado(self, nuevo_estado: str) -> bool:
        """Actualiza el estado de una consulta en la agenda."""
        cursor = self.db.obtener_cursor()
        consulta = "UPDATE rr_agenda SET estado=:estado WHERE id=:id"
        try:
            cursor.execute(consulta, {'estado': nuevo_estado, 'id': self.id})
            self.db.connection.commit()
            print(f"[INFO]: Estado actualizado para agenda ID {self.id}.")
            return True
        except Exception as e:
            print(f"[ERROR]: No se pudo actualizar el estado -> {e}.")
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()

    def listar_agenda(self):
        """Lista toda la agenda."""
        cursor = self.db.obtener_cursor()
        consulta = """
            SELECT a.id, a.id_paciente, a.id_medico, a.fecha_consulta, a.estado,
                   u.nombre_usuario as paciente_usuario, u.nombre as paciente_nombre, u.apellido as paciente_apellido,
                   m.nombre_usuario as medico_usuario, m.nombre as medico_nombre, m.apellido as medico_apellido
            FROM rr_agenda a
            JOIN rr_usuario u ON a.id_paciente = u.id
            JOIN rr_usuario m ON a.id_medico = m.id
            ORDER BY a.fecha_consulta
        """
        try:
            cursor.execute(consulta)
            resultados = cursor.fetchall()
            agendas = []
            for fila in resultados:
                agenda_obj = AgendaModel(
                    self.db,
                    id=fila[0],
                    fecha_consulta=fila[3],
                    estado=fila[4],
                    paciente=PacienteModel(self.db, id=fila[1], nombre_usuario=fila[5], nombre=fila[6], apellido=fila[7]),
                    medico=MedicoModel(self.db, id=fila[2], nombre_usuario=fila[8], nombre=fila[9], apellido=fila[10])
                )
                agendas.append(agenda_obj)
            return agendas
        except Exception as e:
            print(f"[ERROR]: No se pudieron listar la agenda -> {e}.")
            return []
        finally:
            cursor.close()
