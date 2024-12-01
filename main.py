from clase_celular import Dispositivo, Celular, Tablet, Celular_Nuevo, Celular_Viejo


def menu_principal():
    menu_principal=True
    while menu_principal:
        try:
            opcion = int(input("""
            MENU PRINCIPAL
            1. Crear nuevo dispositivo
            2. Usar dispositivo existente
            3. Administrar central
            4. Generar informe de dispositivos
            5. Salir
            Ingrese una opción: """))
        
            if opcion == 1:
                dispositivo = input("¿Qué tipo de dispositivo desea crear? (celular, tablet): ").strip().lower()
                if dispositivo == "celular":
                    try:
                        identificacion=input("(8 caracteres) ID del celular: "),
                        nombre=input("(obligatorio) Nombre del celular: "),
                        modelo=input("Modelo: "),
                        sistema_operativo=input("Sistema operativo (Android, iOS): "),
                        version=input("(X.Y.Z) Versión: "),
                        RAM=input("RAM (GB) (2, 4, 8, 16, 32): "),
                        almacenamiento=input("Almacenamiento (GB) (32, 64, 128, 256, 512): "),
                        num_telefonico=input("(8 dígitos) Número telefónico: ")
                        if version.split('.')[0] != '1':
                            nuevo_dispositivo = Celular_Nuevo(identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento, num_telefonico)
                        else:
                            nuevo_dispositivo = Celular_Viejo(identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento, num_telefonico)
                        print(f"Celular creado con número {nuevo_dispositivo.num_telefonico}")
                    
                    except ValueError as e:
                        print(f"No se pudo crear el celular: {str(e)}")
                elif dispositivo == "tablet":
                    try:
                        nueva_tablet = Tablet(
                            identificacion=input("(8 caracteres) ID de la tablet: "),
                            nombre=input("(obligatorio) Nombre de la tablet: "),
                            modelo=input("Modelo: "),
                            sistema_operativo=input("Sistema operativo (Android, iOS): "),
                            version=input("(X.Y.Z) Versión: "),
                            RAM=input("RAM (GB) (2, 4, 8, 16, 32): "),
                            almacenamiento=input("Almacenamiento (GB) (32, 64, 128, 256, 512): ")
                        )
                        print(f"Tablet creada con nombre {nueva_tablet.nombre}")
                    
                    except ValueError as e:
                        print(f"No se pudo crear la tablet: {str(e)}")
                else:
                    print('Ingreso invalido. ')
                
                
            elif opcion == 2:
                if not Dispositivo.dispositivos_instanciados:
                    print("No hay dispositivos creados todavía")
                    continue
                else:
                    try:
                        print("\Dispositivos disponibles:")
                        for i, disp in enumerate(Dispositivo.dispositivos_instanciados, start=1):
                            if isinstance(disp, Celular):
                                print(f"{i}. Celular: {disp.nombre} - Número: {disp.num_telefonico}")
                            else:
                                print(f"{i}. Tablet: {disp.nombre} - ID: {disp.identificacion}")
                        
                        seleccion = int(input("\nSeleccione el número de dispoitivo que desea usar: "))
                        if 1 <= seleccion <= len(Dispositivo.dispositivos_instanciados):
                            Dispositivo.dispositivos_instanciados[seleccion-1].menu_dispositivo()
                        else:
                            print("Selección inválida. Por favor, elija un número de la lista.")
                        
                    except ValueError:
                        print("Por favor, ingrese un número válido")
                    
            elif opcion == 3:
                try:
                    Celular.central.menu_admin()
                except Exception as e:
                    print(f"Error en el menú de administración: {str(e)}")
            
            elif opcion == 4:
                Dispositivo.generar_informe_txt()

            elif opcion == 5:
                print("¡Hasta luego!")
                menu_principal=False
                
            else:
                print("Opción inválida. Por favor, seleccione una opción del menú.")
        except ValueError:
            print("Por favor, ingrese un número. ")

"""
Estas lineas sirven para probar el programa y no tener que ingresar manualmente los datos

#Se crean celulares
celutomi=Celular("12345678",'tomas','c','ios','1.0','16','128','11111111')
celunico=Celular("87654321",'nicolas','c','Android','2.3.2','8','512','22222222')
celuian=Celular("11223344",'ian','c','anDroid','2.3','32','256','33333333')


#Se encienden
celutomi.encender_apagar()
celunico.encender_apagar()
celuian.encender_apagar()
"""

menu_principal()
