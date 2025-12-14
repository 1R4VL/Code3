import bcrypt

class UsuarioModel:
    def __init__(self, db, id=None, nombre_usuario=None, clave=None, nombre=None, apellido=None,
                 fecha_nacimiento=None, tipo=None, telefono=None, email=None):
        self.db = db
        self.id = id
        self.nombre_usuario = nombre_usuario
        self.clave = clave
        self.nombre = nombre
        self.apellido = apellido
        self.fecha_nacimiento = fecha_nacimiento
        self.tipo = tipo
        self.telefono = telefono
        self.email = email

    def obtener_datos_login(self, nombre_usuario):
        cursor = self.db.obtener_cursor()
        consulta = "SELECT clave, tipo FROM rr_usuario WHERE nombre_usuario=:1"
        try:
            cursor.execute(consulta, (nombre_usuario.strip(),))
            resultado = cursor.fetchone()
            if resultado:
                return resultado
            return None
        except Exception:
            return None
        finally:
            if cursor:
                cursor.close()

    def crear_usuario(self, usuario, clave, nombre, apellido, fecha_nacimiento, tipo):
        cursor = self.db.obtener_cursor()
        clave_encriptada = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            sql_usuario = """
                INSERT INTO rr_usuario (nombre_usuario, clave, nombre, apellido, fecha_nacimiento, tipo)
                VALUES (:usuario, :clave, :nombre, :apellido, TO_DATE(:fecha_nacimiento, 'YYYY-MM-DD'), :tipo)
                RETURNING id INTO :id
            """
            id_var = cursor.var(int)
            cursor.execute(sql_usuario, {
                'usuario': usuario,
                'clave': clave_encriptada,
                'nombre': nombre,
                'apellido': apellido,
                'fecha_nacimiento': fecha_nacimiento,
                'tipo': tipo,
                'id': id_var
            })
            nuevo_id = id_var.getvalue()[0]

            if tipo == "paciente":
                cursor.execute(
                    "INSERT INTO rr_paciente (id_paciente, comuna, fecha_primera_visita) VALUES (:id, NULL, SYSDATE)",
                    {'id': nuevo_id}
                )
            elif tipo == "medico":
                cursor.execute(
                    "INSERT INTO rr_medico (id_medico, especialidad, horario_atencion, fecha_ingreso) VALUES (:id, NULL, NULL, SYSDATE)",
                    {'id': nuevo_id}
                )

            self.db.connection.commit()
            return True
        except Exception:
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()

    def ver_usuario(self, nombre_usuario):
        cursor = self.db.obtener_cursor()
        consulta = "SELECT id, nombre_usuario, nombre, apellido, fecha_nacimiento, tipo, telefono, email FROM rr_usuario WHERE nombre_usuario=:1"
        try:
            cursor.execute(consulta, (nombre_usuario.strip(),))
            return cursor.fetchone()
        except Exception:
            return None
        finally:
            if cursor:
                cursor.close()

    def actualizar_usuario(self, nombre_usuario, nombre=None, apellido=None, fecha_nacimiento=None, telefono=None, email=None):
        cursor = self.db.obtener_cursor()
        datos = []
        valores = {'nombre_usuario': nombre_usuario.strip()}
        
        if nombre is not None:
            datos.append("nombre = :nombre")
            valores['nombre'] = nombre
        if apellido is not None:
            datos.append("apellido = :apellido")
            valores['apellido'] = apellido
        if fecha_nacimiento is not None:
           
            fecha_str = str(fecha_nacimiento).split()[0] if fecha_nacimiento else fecha_nacimiento
            datos.append("fecha_nacimiento = TO_DATE(:fecha_nacimiento, 'YYYY-MM-DD')")
            valores['fecha_nacimiento'] = fecha_str
        if telefono is not None:
            datos.append("telefono = :telefono")
            valores['telefono'] = telefono if telefono else None
        if email is not None:
            datos.append("email = :email")
            valores['email'] = email if email else None
            
        if not datos:
            return False
        
        consulta = f"UPDATE rr_usuario SET {', '.join(datos)} WHERE nombre_usuario = :nombre_usuario"
        try:
            cursor.execute(consulta, valores)
            self.db.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[DEBUG]: Error en actualizar_usuario: {e}")
            self.db.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def eliminar_usuario(self, nombre_usuario):
        cursor = self.db.obtener_cursor()
        try:
            consulta_select = "SELECT id, tipo FROM rr_usuario WHERE nombre_usuario=:1"
            cursor.execute(consulta_select, (nombre_usuario.strip(),))
            resultado = cursor.fetchone()
            if not resultado:
                return False
            user_id, user_type = resultado

            if user_type == "paciente":
                cursor.execute("DELETE FROM rr_paciente WHERE id_paciente=:1", (user_id,))
            elif user_type == "medico":
                cursor.execute("DELETE FROM rr_medico WHERE id_medico=:1", (user_id,))

            consulta_delete = "DELETE FROM rr_usuario WHERE id=:1"
            cursor.execute(consulta_delete, (user_id,))
            
            if cursor.rowcount > 0:
                self.db.connection.commit()
                return True
            else:
                self.db.connection.rollback()
                return False
        except Exception:
            self.db.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

class PacienteModel(UsuarioModel):
    def __init__(self, db, id=None, nombre_usuario=None, clave=None, nombre=None, apellido=None,
                 fecha_nacimiento=None, comuna=None, fecha_primera_visita=None):
        super().__init__(db, id, nombre_usuario, clave, nombre, apellido, fecha_nacimiento, tipo="paciente")
        self.comuna = comuna
        self.fecha_primera_visita = fecha_primera_visita

    def crear_paciente(self, nombre_usuario, clave, nombre, apellido, fecha_nacimiento, comuna, fecha_primera_visita):
        exito_usuario = super().crear_usuario(nombre_usuario, clave, nombre, apellido, fecha_nacimiento, "paciente")
        if not exito_usuario:
            return False

        cursor = self.db.obtener_cursor()
        try:
            consulta_id = "SELECT id FROM rr_usuario WHERE nombre_usuario = :1"
            cursor.execute(consulta_id, (nombre_usuario,))
            id_paciente = cursor.fetchone()[0]

            consulta = """
                UPDATE rr_paciente
                SET comuna = :comuna,
                    fecha_primera_visita = TO_DATE(:fecha_primera_visita, 'YYYY-MM-DD')
                WHERE id_paciente = :id
            """
            cursor.execute(consulta, {
                'comuna': comuna,
                'fecha_primera_visita': fecha_primera_visita,
                'id': id_paciente
            })
            self.db.connection.commit()
            return True
        except Exception:
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()

    def actualizar_paciente(self, id_paciente, comuna=None, fecha_primera_visita=None):
        cursor = self.db.obtener_cursor()
        campos, valores = [], {'id': id_paciente}
        if comuna:
            campos.append("comuna = :comuna")
            valores['comuna'] = comuna
        if fecha_primera_visita:
            campos.append("fecha_primera_visita = TO_DATE(:fecha, 'YYYY-MM-DD')")
            valores['fecha'] = fecha_primera_visita
        if not campos:
            return False
        consulta = f"UPDATE rr_paciente SET {', '.join(campos)} WHERE id_paciente = :id"
        try:
            cursor.execute(consulta, valores)
            self.db.connection.commit()
            return True
        except Exception:
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()

    def eliminar_paciente(self, id_paciente):
        cursor = self.db.obtener_cursor()
        try:
            cursor.execute("DELETE FROM rr_paciente WHERE id_paciente = :1", (id_paciente,))
            if cursor.rowcount > 0:
                self.db.connection.commit()
                return True
            else:
                return False
        except Exception:
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()

    def obtener_paciente(self, nombre_usuario):
        cursor = self.db.obtener_cursor()
        consulta = """
            SELECT u.id, u.nombre_usuario, u.nombre, u.apellido, u.fecha_nacimiento, p.comuna, p.fecha_primera_visita
            FROM rr_usuario u
            JOIN rr_paciente p ON u.id=p.id_paciente
            WHERE u.nombre_usuario = :1
        """
        try:
            cursor.execute(consulta, (nombre_usuario.strip(),))
            return cursor.fetchone()
        except Exception:
            return None
        finally:
            if cursor:
                cursor.close()

    def obtener_paciente_por_id(self, id_paciente):
        cursor = self.db.obtener_cursor()
        consulta = """
            SELECT u.id, u.nombre_usuario, u.nombre, u.apellido, u.fecha_nacimiento, p.comuna, p.fecha_primera_visita
            FROM rr_usuario u
            JOIN rr_paciente p ON u.id=p.id_paciente
            WHERE u.id = :1
        """
        try:
            cursor.execute(consulta, (id_paciente,))
            return cursor.fetchone()
        except Exception:
            return None
        finally:
            if cursor:
                cursor.close()

class MedicoModel(UsuarioModel):
    def __init__(self, db, id=None, nombre_usuario=None, clave=None, nombre=None, apellido=None,
                 fecha_nacimiento=None, especialidad=None, horario_atencion=None, fecha_ingreso=None):
        super().__init__(db, id, nombre_usuario, clave, nombre, apellido, fecha_nacimiento, tipo="medico")
        self.especialidad = especialidad
        self.horario_atencion = horario_atencion
        self.fecha_ingreso = fecha_ingreso

    def crear_medico(self, nombre_usuario, clave, nombre, apellido, fecha_nacimiento, especialidad, horario_atencion, fecha_ingreso, telefono=None, email=None):
        exito_usuario = super().crear_usuario(nombre_usuario, clave, nombre, apellido, fecha_nacimiento, "medico")
        if not exito_usuario:
            return False

        cursor = self.db.obtener_cursor()
        try:
            consulta_id = "SELECT id FROM rr_usuario WHERE nombre_usuario = :1"
            cursor.execute(consulta_id, (nombre_usuario,))
            id_medico = cursor.fetchone()[0]

            consulta = """
                UPDATE rr_medico
                SET especialidad = :especialidad,
                    horario_atencion = :horario,
                    fecha_ingreso = TO_DATE(:fecha_ingreso, 'YYYY-MM-DD')
                WHERE id_medico = :id
            """
            cursor.execute(consulta, {
                'especialidad': especialidad,
                'horario': horario_atencion,
                'fecha_ingreso': fecha_ingreso,
                'id': id_medico
            })
            self.db.connection.commit()
            return True
        except Exception:
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()

    def actualizar_medico(self, id_medico, especialidad=None, horario_atencion=None, fecha_ingreso=None):
        cursor = self.db.obtener_cursor()
        campos, valores = [], {'id': id_medico}
        if especialidad:
            campos.append("especialidad = :esp")
            valores['esp'] = especialidad
        if horario_atencion:
            campos.append("horario_atencion = :hor")
            valores['hor'] = horario_atencion
        if fecha_ingreso:
            campos.append("fecha_ingreso = TO_DATE(:fecha, 'YYYY-MM-DD')")
            valores['fecha'] = fecha_ingreso
        if not campos:
            return False
        consulta = f"UPDATE rr_medico SET {', '.join(campos)} WHERE id_medico = :id"
        try:
            cursor.execute(consulta, valores)
            self.db.connection.commit()
            return True
        except Exception:
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()

    def eliminar_medico(self, id_medico):
        cursor = self.db.obtener_cursor()
        try:
            cursor.execute("DELETE FROM rr_medico WHERE id_medico = :1", (id_medico,))
            if cursor.rowcount > 0:
                self.db.connection.commit()
                return True
            else:
                return False
        except Exception:
            self.db.connection.rollback()
            return False
        finally:
            cursor.close()

    def obtener_medico(self, nombre_usuario):
        cursor = self.db.obtener_cursor()
        consulta = """
            SELECT u.id, u.nombre_usuario, u.nombre, u.apellido, u.fecha_nacimiento,
                   m.especialidad, m.horario_atencion, m.fecha_ingreso
            FROM rr_usuario u
            JOIN rr_medico m ON u.id = m.id_medico
            WHERE u.nombre_usuario = :1
        """
        try:
            cursor.execute(consulta, (nombre_usuario.strip(),))
            return cursor.fetchone()
        except Exception:
            return None
        finally:
            if cursor:
                cursor.close()

    def listar_pacientes(self):
        cursor = self.db.obtener_cursor()
        consulta = """
            SELECT p.id_paciente, u.nombre_usuario, u.nombre, u.apellido, u.fecha_nacimiento, p.comuna, p.fecha_primera_visita
            FROM rr_paciente p
            INNER JOIN rr_usuario u ON p.id_paciente = u.id
            ORDER BY u.nombre ASC
        """
        try:
            cursor.execute(consulta)
            return cursor.fetchall()
        except Exception:
            return []
        finally:
            cursor.close()

class AdministradorModel(UsuarioModel):
    def __init__(self, db, id=None, nombre_usuario=None, clave=None, nombre=None, apellido=None,
                 fecha_nacimiento=None):
        super().__init__(db, id, nombre_usuario, clave, nombre, apellido, fecha_nacimiento, tipo="administrador")

    def crear_administrador(self, nombre_usuario, clave, nombre, apellido, fecha_nacimiento):
        exito_usuario = super().crear_usuario(nombre_usuario, clave, nombre, apellido, fecha_nacimiento, "administrador")
        if not exito_usuario:
            return False

        return True

    def listar_usuarios(self):
        cursor = self.db.obtener_cursor()
        consulta = """
            SELECT id, nombre_usuario, nombre, apellido, fecha_nacimiento, tipo, telefono, email
            FROM rr_usuario
            ORDER BY nombre ASC
        """
        try:
            cursor.execute(consulta)
            return cursor.fetchall()
        except Exception:
            return []
        finally:
            cursor.close()

    def listar_pacientes(self):
        """Lista todos los pacientes con su información completa."""
        cursor = self.db.obtener_cursor()
        consulta = """
            SELECT u.id, u.nombre_usuario, u.nombre, u.apellido, u.fecha_nacimiento, 
                   u.tipo, u.telefono, u.email, p.comuna, p.fecha_primera_visita
            FROM rr_usuario u
            JOIN rr_paciente p ON u.id = p.id_paciente
            ORDER BY u.nombre ASC
        """
        try:
            cursor.execute(consulta)
            return cursor.fetchall()
        except Exception:
            return []
        finally:
            cursor.close()

    def listar_medicos(self):
        """Lista todos los médicos con su información completa."""
        cursor = self.db.obtener_cursor()
        consulta = """
            SELECT u.id, u.nombre_usuario, u.nombre, u.apellido, u.fecha_nacimiento,
                   u.tipo, u.telefono, u.email, m.especialidad, m.horario_atencion, m.fecha_ingreso
            FROM rr_usuario u
            JOIN rr_medico m ON u.id = m.id_medico
            ORDER BY u.nombre ASC
        """
        try:
            cursor.execute(consulta)
            return cursor.fetchall()
        except Exception:
            return []
        finally:
            cursor.close()