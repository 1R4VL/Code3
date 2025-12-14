from model.personas_m import PacienteModel, MedicoModel, UsuarioModel

class UsuarioView:
    """Vista para mostrar información de usuarios."""
    def mostrar_usuario(self, usuario: UsuarioModel):
        """
        Muestra en pantalla la información detallada de un usuario.
        """
        print("\n--- Usuario ---")
        print(f"ID Usuario: {usuario.id}")
        print(f"Nombre de Usuario: {usuario.nombre_usuario}")
        print(f"Nombre: {usuario.nombre} {usuario.apellido}")
        print(f"Fecha de Nacimiento: {usuario.fecha_nacimiento}")
        print(f"Teléfono: {usuario.telefono if usuario.telefono else 'No registrado'}")
        print(f"Email: {usuario.email if usuario.email else 'No registrado'}")
        print(f"Tipo: {usuario.tipo}")
    
    def mostrar_usuarios(self, usuarios):
        """
        Muestra en pantalla la información de una lista de usuarios.
        Si la lista está vacía, informa que no hay usuarios registrados.
        """
        if not usuarios:
            print("[INFO]: No hay usuarios registrados.")
        for usuario in usuarios:
            self.mostrar_usuario(usuario)

class PacienteView:
    """Vista para mostrar información de pacientes."""
    def mostrar_paciente(self, paciente: PacienteModel):
        """
        Muestra en pantalla la información detallada de un paciente.
        """
        print("\n--- Paciente ---")
        print(f"ID Paciente: {paciente.id}")
        print(f"Nombre de Usuario: {paciente.nombre_usuario}")
        print(f"Nombre: {paciente.nombre} {paciente.apellido}")
        print(f"Fecha de Nacimiento: {paciente.fecha_nacimiento}")
        print(f"Teléfono: {paciente.telefono if paciente.telefono else 'No registrado'}")
        print(f"Email: {paciente.email if paciente.email else 'No registrado'}")
        print(f"Comuna: {paciente.comuna if paciente.comuna else 'No registrada'}")
        print(f"Fecha de Primera Visita: {paciente.fecha_primera_visita if paciente.fecha_primera_visita else 'No registrada'}")
    
    def mostrar_pacientes(self, pacientes):
        """
        Muestra en pantalla la información de una lista de pacientes.
        Si la lista está vacía, informa que no hay pacientes registrados.
        """
        if not pacientes:
            print("[INFO]: No hay pacientes registrados.")
        for paciente in pacientes:
            self.mostrar_paciente(paciente)


class MedicoView:
    """Vista para mostrar información de médicos."""
    def mostrar_medico(self, medico: MedicoModel):
        """
        Muestra en pantalla la información detallada de un médico.
        """
        print("\n--- Médico ---")
        print(f"ID Médico: {medico.id}")
        print(f"Nombre de Usuario: {medico.nombre_usuario}")
        print(f"Nombre: {medico.nombre} {medico.apellido}")
        print(f"Fecha de Nacimiento: {medico.fecha_nacimiento}")
        print(f"Teléfono: {medico.telefono if medico.telefono else 'No registrado'}")
        print(f"Email: {medico.email if medico.email else 'No registrado'}")
        print(f"Especialidad: {medico.especialidad if medico.especialidad else 'No registrada'}")
        print(f"Horario de Atención: {medico.horario_atencion if medico.horario_atencion else 'No registrado'}")
        print(f"Fecha de Ingreso: {medico.fecha_ingreso if medico.fecha_ingreso else 'No registrada'}")
    
    def mostrar_medicos(self, medicos):
        """
        Muestra en pantalla la información de una lista de médicos.
        Si la lista está vacía, informa que no hay médicos registrados.
        """
        if not medicos:
            print("[INFO]: No hay médicos registrados.")
        for medico in medicos:
            self.mostrar_medico(medico)
