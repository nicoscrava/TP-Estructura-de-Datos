from clase_celular import Celular
from clase_central import Central


def menu_principal():

    while True:
        opcion = int(input("""
        MENU PRINCIPAL
        1. Crear nuevo celular
        2. Usar celular existente
        3. Administrar central
        4. Generar informe de celulares
        5. Salir
        Ingrese una opción: """))
        
        if opcion == 1:
            try:
                nuevo_celular = Celular(
                    identificacion=input("ID del celular: "),
                    nombre=input("Nombre del celular: "),
                    modelo=input("Modelo: "),
                    sistema_operativo=input("Sistema operativo: "),
                    version=input("Versión: "),
                    RAM=input("RAM (GB): "),
                    almacenamiento=input("Almacenamiento (GB): "),
                    num_telefonico=input("Número telefónico: ")
                )
                print(f"Celular creado con número {nuevo_celular.num_telefonico}")
                
            except ValueError as e:
                print(f"No se pudo crear el celular: {str(e)}")
            
            
        elif opcion == 2:
            if not Celular.celulares_registrados:
                print("No hay celulares creados todavía")
                continue
            else:
                try:
                    print("\nCelulares disponibles:")
                    for i, cel in enumerate(Celular.celulares_registrados, start=1):
                        print(f"{i}. {cel.nombre} - Número: {cel.num_telefonico}")
                    
                    seleccion = int(input("\nSeleccione el número de celular que desea usar: "))
                    if 1 <= seleccion <= len(Celular.celulares_registrados):
                        Celular.celulares_registrados[seleccion-1].menu_celular()
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
            Celular.generar_informe_csv()

        elif opcion == 5:
            print("¡Hasta luego!")
            break
            
        else:
            print("Opción inválida. Por favor, seleccione una opción del menú.")

celutomi=Celular("12345678",'tomas','c','Android','1','2','32','34382301')
celunico=Celular("87654321",'nicolas','c','Android','2','4','64','12345678')
celian=Celular("11223344",'ian','c','Android','2','16','128','55555555')
celutomi.encender_apagar()
celunico.encender_apagar()
menu_principal()
