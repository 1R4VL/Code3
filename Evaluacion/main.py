import sys
from controller.personas_c import UsuarioController
from controller.objetos_c import ObjetosController
from config.db_config import ConexionOracle, validar_tablas

def conectarBD():
    db = ConexionOracle("SYSTEM", "Jeloum3n12", "localhost:1521/XEPDB1")
    db.conectar()
    validar_tablas(db)
    return db

def menu_principal():
    db = conectarBD()
    usuario_controller = UsuarioController(db)
    objetos_controller = ObjetosController(db)
    usuario_logueado = None

    while True:
        if usuario_logueado:
            if usuario_logueado['tipo'] == 'paciente':
                usuario_controller.menu_paciente(usuario_logueado)
            elif usuario_logueado['tipo'] == 'medico':
                usuario_controller.menu_medico(usuario_logueado)
            elif usuario_logueado['tipo'] == 'administrador':
                usuario_controller.menu_administrador(usuario_logueado)
            usuario_logueado = None
        else:
            print("\n---- MediPlus - Menú Principal ----")
            print("1) Crear Usuario")
            print("2) Iniciar Sesión")
            print("3) Cargar Usuarios de Prueba (Contiene al Administrador)")
            print("4) Cargar Usuarios desde users.json (datos solicitados)")
            print("5) Cargar Insumos desde JSON (datos/insumos.json)")
            print("0) Salir")
            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                usuario_controller.crear_usuario()
            elif opcion == "2":
                exito, usuario = usuario_controller.inicio_sesion()
                if exito:
                    usuario_logueado = usuario
            elif opcion == "3":
                usuario_controller.cargar_usuarios_json()
            elif opcion == "4":
                usuario_controller.cargar_usuarios_desde_users_json()
            elif opcion == "5":
                objetos_controller.cargar_insumos_json()
            elif opcion == "0":
                print("Saliendo de la aplicación. ¡Hasta luego!")
                db.desconectar()
                break
            else:
                print("[ERROR]: Opción inválida. Intente nuevamente.")

def main():
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nInterrupción por el usuario. Saliendo...")
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()