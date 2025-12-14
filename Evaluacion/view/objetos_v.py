from model.objetos_m import InsumosModel, RecetasModel, ConsultasModel, AgendaModel

class InsumosView:
    """Vista para mostrar información de insumos médicos."""

    def mostrar_insumo(self, insumo: InsumosModel):
        """
        Muestra en pantalla la información detallada de un insumo específico.
        """
        costo_clp = insumo.costo_usd * 950  
        print("\n--- Insumo ---")
        print(f"ID: {insumo.id}")
        print(f"Nombre: {insumo.nombre}")
        print(f"Tipo: {insumo.tipo}")
        print(f"Stock: {insumo.stock}")
        print(f"Costo: ${costo_clp:,.0f} CLP")
    
    def mostrar_insumos(self, insumos):
        """
        Muestra en pantalla la información de una lista de insumos.
        Si la lista está vacía, informa que no hay insumos registrados.
        """
        if not insumos:
            print("[INFO]: No hay insumos registrados.")
        for insumo in insumos:
            self.mostrar_insumo(insumo)


class RecetasView:
    """Vista para mostrar información de recetas."""
    def mostrar_receta(self, receta: RecetasModel):
        """Muestra una receta."""
        paciente_nombre = f"{receta.paciente.nombre} {receta.paciente.apellido}" if receta.paciente.nombre else receta.paciente.nombre_usuario
        medico_nombre = f"{receta.medico.nombre} {receta.medico.apellido}" if receta.medico.nombre else receta.medico.nombre_usuario
        print("\n--- Receta Médica ---")
        print(f"ID: {receta.id}")
        print(f"Paciente: {paciente_nombre}")
        print(f"Médico: {medico_nombre}")
        print(f"Descripción: {receta.descripcion}")
        print(f"Medicamentos Recetados: {receta.medicamentos_recetados}")
        print(f"Costo: ${receta.costo_clp:,.0f} CLP")
        insumos = receta.obtener_insumos()
        if insumos:
            print("Insumos asociados:")
            for insumo, cantidad in insumos:
                costo_insumo_clp = insumo.costo_usd * 950
                print(f" - {insumo.nombre} ({insumo.tipo}), cantidad: {cantidad}, costo: ${costo_insumo_clp:,.0f} CLP")
        else:
            print("No hay insumos asociados.")


    def mostrar_recetas(self, recetas):
        """
        Muestra en pantalla la información de una lista de recetas.
        Si la lista está vacía, informa que no hay recetas registradas.
        """
        if not recetas:
            print("[INFO]: No hay recetas registradas.")
        for receta in recetas:
            self.mostrar_receta(receta)


class ConsultasView:
    """Vista para mostrar información de consultas médicas."""

    def mostrar_consulta(self, consulta: ConsultasModel):
        """
        Muestra en pantalla la información detallada de una consulta médica.
        """
        paciente_nombre = f"{consulta.paciente.nombre} {consulta.paciente.apellido}" if consulta.paciente.nombre else consulta.paciente.nombre_usuario
        medico_nombre = f"{consulta.medico.nombre} {consulta.medico.apellido}" if consulta.medico.nombre else consulta.medico.nombre_usuario
        print("\n--- Consulta Médica ---")
        print(f"ID: {consulta.id}")
        print(f"Paciente: {paciente_nombre}")
        print(f"Médico: {medico_nombre}")
        print(f"Receta ID: {consulta.receta.id if consulta.receta else 'N/A'}")
        print(f"Fecha: {consulta.fecha}")
        print(f"Comentarios: {consulta.comentarios}")
        print(f"Valor: ${consulta.valor:,.0f} CLP")

    def mostrar_consultas(self, consultas):
        """
        Muestra en pantalla la información de una lista de consultas médicas.
        Si la lista está vacía, informa que no hay consultas registradas.
        """
        if not consultas:
            print("[INFO]: No hay consultas registradas.")
        for consulta in consultas:
            self.mostrar_consulta(consulta)


class AgendaView:
    """Vista para mostrar información de agendas médicas."""

    def mostrar_agenda(self, agenda: AgendaModel):
        """
        Muestra en pantalla la información detallada de una agenda médica.
        """
        paciente_nombre = f"{agenda.paciente.nombre} {agenda.paciente.apellido}" if agenda.paciente.nombre else agenda.paciente.nombre_usuario
        medico_nombre = f"{agenda.medico.nombre} {agenda.medico.apellido}" if agenda.medico.nombre else agenda.medico.nombre_usuario
        print("\n--- Agenda Médica ---")
        print(f"ID: {agenda.id}")
        print(f"Paciente: {paciente_nombre}")
        print(f"Médico: {medico_nombre}")
        print(f"Fecha Consulta: {agenda.fecha_consulta}")
        print(f"Estado: {agenda.estado}")

    def mostrar_agendas(self, agendas):
        """
        Muestra en pantalla la información de una lista de agendas médicas.
        Si la lista está vacía, informa que no hay agendas registradas.
        """
        if not agendas:
            print("\n[INFO]: No hay agendas registradas.")
            return
        print("\n" + "="*80)
        print("LISTA DE AGENDAS")
        print("="*80)
        print(f"{'ID':<5} {'Paciente':<20} {'Médico':<20} {'Fecha Consulta':<20} {'Estado':<10}")
        print("-"*80)
        for agenda in agendas:
            paciente_display = f"{agenda.paciente.nombre} {agenda.paciente.apellido}" if agenda.paciente.nombre and agenda.paciente.apellido else agenda.paciente.nombre_usuario
            medico_display = f"{agenda.medico.nombre} {agenda.medico.apellido}" if agenda.medico.nombre and agenda.medico.apellido else agenda.medico.nombre_usuario
            print(f"{agenda.id:<5} {paciente_display:<20} {medico_display:<20} {agenda.fecha_consulta.strftime('%Y-%m-%d %H:%M'):<20} {agenda.estado:<10}")
        print("="*80)
