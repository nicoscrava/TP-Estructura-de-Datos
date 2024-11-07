from clase_central import Central, Comunicacion
from collections import deque
from clase_listaenlazada import ListaEnlazada, Nodo
from clase_email import Email, CentralGmail
from random import *
import funciones


class Celular:
    
    central = Central() #se crea central de comunicacion
    central_gmail = CentralGmail()
    celulares_registrados = []

    def __init__(self, identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento, num_telefonico) :
        
        # Validación de identificación
        if not isinstance(identificacion, str) or len(identificacion) != 8:
            raise ValueError("La identificación debe ser una cadena de 8 caracteres")
        self.identificacion = identificacion

        # Validación de nombre
        if not isinstance(nombre, str) or len(nombre.strip()) == 0:
            raise ValueError("El nombre no puede estar vacío")
        self.nombre = nombre.strip()
        
        #no le ponemos validacion porque puede ser cualquier tipo de modelo
        self.modelo=modelo
        

        # Validación de sistema operativo
        sistemas_validos = ['Android', 'iOS']
        if sistema_operativo not in sistemas_validos:
            raise ValueError(f"Sistema operativo debe ser uno de: {sistemas_validos}")
        self.sistema_operativo = sistema_operativo

        # Verificar si el número ya está registrado
        for celular in Celular.celulares_registrados:
            if celular.num_telefonico == num_telefonico:
                raise ValueError("Este número telefónico ya está registrado")
        self.num_telefonico = num_telefonico
        
                # Validación de versión
        try:
            version_float = float(version)
            if version_float <= 0:
                raise ValueError
            self.version = version_float
        except ValueError:
            raise ValueError("La versión debe ser un número positivo")

        # Validación de RAM
        try:
            ram_int = int(RAM)
            if ram_int not in [2, 4, 8, 16, 32]:
                raise ValueError
            self.RAM = ram_int
        except ValueError:
            raise ValueError("La RAM debe ser uno de estos valores: 2, 4, 8, 16, 32 GB")

        # Validación de almacenamiento
        try:
            almacenamiento_int = int(almacenamiento)
            if almacenamiento_int not in [32, 64, 128, 256, 512]:
                raise ValueError
            self.almacenamiento = float(almacenamiento_int) #se convierte a float para trabajar mejor 
        except ValueError:
            raise ValueError("El almacenamiento debe ser uno de estos valores: 32, 64, 128, 256, 512 GB")

        # Validación de número telefónico
        if not isinstance(num_telefonico, str) or not num_telefonico.isdigit() or len(num_telefonico) != 8:
            raise ValueError("El número telefónico debe contener exactamente 8 dígitos")

        #para poder usar EMAIl
        self.datos_moviles=False

        #atributos adicionales
        self.encendido = False #indica si esta encendido o apagado
        self.desbloqueado=False #indica si esta desbloqueado el celular
        self.codigo=None
        self.red_movil=False


        # se da de alta automaticamente al crear el celular
        self.central.alta_dispositivo(self)

        # Se encuentra disponible para la llamada
        self.disponible = True

        # Contiene el numero con el cual se esta en llamada
        self.llamada_actual = None
        
        #primero se inicializa la app de contactos
        contactos = Contactos(self)
        
        #aca se crea esta instancia para trabajar con las apps y su almacenamiento
        self.almacenamiento_disponible=0
        
        #creamos un diccionario para reflejar cada aplicacion y poder identificarla por su nombre
        #la app contactos ya fue creada para poder ser pasada como argumento
        self.apps={"contactos": contactos,
                   "sms": SMS(self, contactos), 
                   "email": AppEmail(self),
                   "telefono": Telefono(self, contactos),
                   'app store': App_Store(self), #accede al celular para modificar las apps dentro
                    'configuracion': Configuracion(self) #accede a toda la configuracion del celular
                   }
        
        # se agrega a la lista de celulares registrados para poder acceder a ellos desde el menu principal
        Celular.celulares_registrados.append(self)
    
    def encender_apagar(self):

        self.encendido = not self.encendido
        if self.encendido:
            self.apps['configuracion'].activar_red_movil()
            print("\nEl celular se ha prendido")

        else:
            #ACA deberia DESCONECTAR CON LA CENTRAL
            self.red_movil = False
            self.desbloqueado = False
            if self.llamada_actual != None:
                
                self.apps['telefono'].terminar_llamada() # Se termina la llamada en curso en el caso de existir
            print("\nHas apagado el celular")

    def menu_celular(self):
        while True:
            if not self.encendido:
                opcion = input("""
CELULAR APAGADO
1. Encender celular
2. Volver al menú principal

Ingrese una opción: """)
                
                if opcion == "1":
                    self.encender_apagar()
                elif opcion == "2":
                    break
                else:
                    print("Opción inválida")
                
            elif not self.desbloqueado:
                opcion = input("""
CELULAR BLOQUEADO
1. Desbloquear celular
2. Apagar celular
3. Volver al menú principal

Ingrese una opción: """)
                
                if opcion == "1":
                    self.bloq_desbloq()
                elif opcion == "2":
                    self.encender_apagar()
                elif opcion == "3":
                    break
                else:
                    print("Opción inválida")
                        
            else:
                opcion = input("""
MENU CELULAR
1. Abrir aplicación
2. Bloquear celular
3. Apagar celular
4. Volver al menú principal

Ingrese una opción: """)
                
                if opcion == "1":
                    try:
                        self.abrir_app()
                    except Exception as e:
                        print(f"Error al abrir la aplicación: {str(e)}")
                elif opcion == "2":
                    self.bloq_desbloq()
                elif opcion == "3":
                    self.encender_apagar()
                elif opcion == "4":
                    break
                else:
                    print("Opción inválida")

    def abrir_app(self):
        """Permite abrir una aplicación por su nombre"""
        print(f"\nAplicaciones disponibles: {', '.join(list(self.apps.keys()))}")
        
        app_nombre = input("\nIngrese el nombre de la aplicación: ").lower()
        if app_nombre in self.apps:
            self.apps[app_nombre].menu()
        else:
            print("\nAplicación no encontrada")


    #agregar contrasenia    
    def bloq_desbloq(self):
        if self.desbloqueado:
            # Si está desbloqueado, simplemente lo bloqueamos
            self.desbloqueado = False
            print("\nHas bloqueado el celular")
            return
        
        # Si está bloqueado, verificamos si tiene código
        if self.codigo is None:
            self.desbloqueado = True
            print("\nEl celular se ha desbloqueado")
            return
        
        # Si tiene código, pedimos que lo ingrese
        intentos = 3
        while intentos > 0:
            try:
                codigo_ingresado = int(input('\nIngrese el código de desbloqueo: '))
                if codigo_ingresado == self.codigo:
                    self.desbloqueado = True
                    print("\nEl celular se ha desbloqueado")
                    return
                else:
                    intentos -= 1
                    if intentos > 0:
                        print(f"\nCódigo incorrecto. Te quedan {intentos} intentos")
                    else:
                        print("\nDemasiados intentos fallidos. Vuelva a intentarlo.")
            except ValueError:
                print("\nEl código debe ser un número")
                intentos -= 1


    def validar_estado_emisor(self):

        if self.red_movil == False:
            print('Tu celular no puede enviar mensajes. Activa la red movil.')
            return False
        
        # Verifica que el celular emisor este registrado en la red
        elif self.num_telefonico not in self.central.dispositivos_registrados:
            print('Tu celular no se encuentra en la red.')
            return False
        
        else:
            return True

    def __str__(self):
        estado_red = "Activada" if self.red_movil else "Desactivada"
        estado_datos = "Activados" if self.datos_moviles else "Desactivados"
        
        return f"""
        Celular {self.nombre}
        ID: {self.identificacion}
        Modelo: {self.modelo}
        SO: {self.sistema_operativo} v{self.version}
        RAM: {self.RAM}GB
        Almacenamiento: {self.almacenamiento}GB
        Número: {self.num_telefonico}
        Red móvil: {estado_red}
        Datos móviles: {estado_datos}
        """
    @classmethod
    def generar_informe_csv(cls):
        """Genera un archivo CSV con información básica de todos los celulares registrados"""
        try:
            with open('informe_celulares.csv', 'w') as archivo:
                # Escribir encabezados
                archivo.write("Nombre,Numero,Red Movil\n")
                
                # Escribir datos de cada celular
                for celular in cls.celulares_registrados:
                    estado_red = "Activada" if celular.red_movil else "Desactivada"
                    
                    linea = f"{celular.nombre},{celular.num_telefonico},{estado_red}\n"
                    archivo.write(linea)
                    
            print("Informe generado exitosamente en 'informe_celulares.csv'")
            
        except Exception as e:
            print(f"Error al generar el informe: {str(e)}")
    
        


class Aplicacion():

    def __init__ (self, celular: Celular):
        self.celular = celular
        self.almacenamiento= None
        self.necesaria = False

    def menu(self):
        print("Esta aplicación no tiene menú disponible")
        


class Contactos(Aplicacion):

    def __init__(self, celular: Celular):
        super().__init__(celular)
        self.lista_de_contactos={}
        self.almacenamiento=1 #ocupa 1 gb
        celular.almacenamiento_disponible +=self.almacenamiento
        self.necesaria = True
    
    def ver_contactos(self):
        if not self.lista_de_contactos:
            print("No hay contactos guardados")
        else:
            print("\nLista de contactos:")
            for nombre, numero in self.lista_de_contactos.items():
                print(f"{nombre}: {numero}")

    def agregar_contacto(self):
        while True:
            numero = input("Ingrese número: ")
            if not numero.isdigit():
                print("El número debe contener solo dígitos")
                
            elif len(numero) != 8:
                print("El número debe tener 8 dígitos")
                
            elif numero in self.lista_de_contactos.values():
                print("Este número ya existe en contactos")
            else:
                break
        
        nombre = input("Ingrese nombre: ")
        self.lista_de_contactos[nombre] = numero
        print(f"Contacto agregado: {nombre} - {numero}")

    def menu(self):
        while True:
            opcion = input("""
            CONTACTOS
            1. Ver contactos
            2. Agregar contacto
            3. Volver
            Ingrese una opción: """)
            
            if opcion == "1":
                self.ver_contactos()
            elif opcion == "2":
                self.agregar_contacto()
            elif opcion == "3":
                break
            else:
                print("Opción inválida")


class SMS(Aplicacion):
    def __init__(self, celular: Celular, contactos: Contactos):
        super().__init__(celular)
        self.almacenamiento=1 #ocupa 1 gb
        celular.almacenamiento_disponible+=self.almacenamiento
        self.bandeja= ListaEnlazada() #lista enlazada 
        self.contactos=contactos
        self.en_espera = deque() # COLA Mensajes que te llegaron cuando no tenias la red movil activa
        self.necesaria = True
        
    def enviar_mensaje(self):
        # Primero mostramos los contactos disponibles
        self.contactos.ver_contactos()
        
        # Pedimos el destinatario (puede ser un número directo o nombre de contacto)
        receptor = input("\nIngrese un numero o un nombre de contacto: ")
        
        # Si el receptor está en las claves (nombres) de contactos, obtenemos su número
        if receptor in self.contactos.lista_de_contactos:
            receptor = self.contactos.lista_de_contactos[receptor]
        # Si no es un contacto, verificamos que sea un número válido
        elif not receptor.isdigit() or len(receptor) != 8:
            print("\nNúmero inválido. Debe contener 8 dígitos.")
            return
            
        mensaje = input("\nEscriba su mensaje: ")
        
        # La central maneja la comunicación
        self.celular.central.comunicacion_sms(self.celular, receptor, mensaje)
        

    
    def eliminar_mensajes(self):
        """Permite al usuario eliminar mensajes específicos"""
        if self.bandeja.esVacia():
            print("No hay mensajes para eliminar")
            return
            
        print("\nMensajes en la bandeja:")
        actual = self.bandeja.inicio
        indice = 1
        while actual:
            print(f"{indice}. {actual.dato}")
            actual = actual.siguiente
            indice += 1
            
        try:
            seleccion = int(input("\nIngrese el número del mensaje a eliminar (0 para cancelar): "))
            if seleccion == 0:
                return
                
            if 1 <= seleccion <= self.bandeja.tamanio():  # Necesitamos agregar este método
                # Eliminamos el mensaje seleccionado
                self.bandeja.eliminarPosicion(seleccion - 1)  # Y este método
                print("Mensaje eliminado exitosamente")
            else:
                print("Número de mensaje inválido")
        except ValueError:
            print("Por favor ingrese un número válido")
    
    def menu(self):
        while True:
            opcion = input("""
SMS
1. Ver bandeja de mensajes
2. Enviar mensaje
3. Eliminar mensajes
4. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                funciones.ver_bandeja(self)
            elif opcion == "2":
                if self.celular.validar_estado_emisor():
                    self.enviar_mensaje()
            elif opcion == "3":
                self.eliminar_mensajes()
            elif opcion == "4":
                break
            else:
                print("Opción inválida")
   
class Telefono(Aplicacion):
    def __init__(self, celular: Celular, contactos):
        super().__init__(celular)
        self.almacenamiento=1 #ocupa 1 gb
        celular.almacenamiento_disponible+=self.almacenamiento
        self.historial_llamadas=deque() #Pila para ver cual llega primero
        self.contactos=contactos
        self.necesaria = True
    
    def llamar(self):
        if self.celular.llamada_actual is None:
            # Primero mostramos los contactos disponibles
            self.contactos.ver_contactos()
            
            # Pedimos el destinatario (puede ser un número directo o nombre de contacto)
            receptor = input("\nIngrese un numero o un nombre de contacto: ")
            
            # Si el receptor está en las claves (nombres) de contactos, obtenemos su número
            if receptor in self.contactos.lista_de_contactos:
                receptor = self.contactos.lista_de_contactos[receptor]
            else:
                # Si no es un contacto, verificamos que sea un número válido
                if not receptor.isdigit() or len(receptor) != 8:
                    print("Número inválido. Debe contener 8 dígitos.")
                    return
            

            self.celular.central.comunicacion_telefonica(self.celular, receptor)
        else:
            print('\nYa tienes una llamada en curso.')
    
    def recibir_llamada(self, comunicacion: Comunicacion):

        # Si el celular no esta en llamada se le pide aceptar o rechazar la llamada
        
        if self.celular.disponible:
            # Buscamos si el número que llama está en los contactos
            nombre_contacto = None
            for nombre, numero in self.celular.apps['contactos'].lista_de_contactos.items():
                if numero == comunicacion.emisor.num_telefonico:
                    nombre_contacto = nombre
                    break
                    
            # Mostramos el nombre si existe, sino el número
            if nombre_contacto:
                eleccion = input(f'{nombre_contacto} te está llamando. ¿Desea aceptar la llamada? (si/no)')
            else:
                eleccion = input(f'El numero {comunicacion.emisor.num_telefonico} te esta llamando. Desea aceptar la llamada? (si/no)')
                
            if eleccion.lower() == 'si':
                self.celular.disponible = False
                self.celular.llamada_actual = comunicacion
                return True
            else:
                return False
        # Se agrega al historial de llamadas como llamada perdida
        else:
            self.agregar_historial_llamadas(comunicacion)

    def terminar_llamada(self):
        if not self.celular.disponible:
            self.celular.central.terminar_comunicacion_telefonica(self.celular.llamada_actual)
            print('Llamada finalizada. ')
        else:
            print('No hay una llamada en curso. ')

    
    def ver_historial_llamadas(self):
        if not self.historial_llamadas:
            print("No hay llamadas en el historial")
            return
        print("\nHistorial de llamadas:")
        for llamada in self.historial_llamadas:
            # Pasamos True si el emisor de la llamada es este celular
            vista_emisor = llamada.emisor == self.celular
            print(llamada.__str__(vista_emisor))

    def agregar_historial_llamadas(self, comunicacion: Comunicacion):
        self.historial_llamadas.appendleft(comunicacion)

    def menu(self):
        while True:
            opcion = input("""
TELÉFONO
1. Realizar llamada
2. Ver historial de llamadas
3. Terminar llamada actual
4. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                if self.celular.validar_estado_emisor():
                    self.llamar()
            elif opcion == "2":
                self.ver_historial_llamadas()
            elif opcion == "3":
                self.terminar_llamada()
            elif opcion == "4":
                break
            else:
                print("Opción inválida")
    
    
class AppEmail(Aplicacion):
    def __init__(self, celular: Celular):
        super().__init__(celular)
        self.almacenamiento=3 #ocupa 3gb
        celular.almacenamiento_disponible+=self.almacenamiento
        self.mail = f"{celular.nombre.lower().replace(' ', '')}@gmail.com"
        celular.central_gmail.usuarios_registrados[self.mail]=celular
        self.bandeja= ListaEnlazada() #lista enlazada 
        self.en_espera = deque() # Mensajes que te llegaron cuando no tenias la red movil activa
        self.bandeja_enviados = deque()  # pila para los emails enviados
        self.necesaria = True
        self.casillas_bloqueadas=set()
    

        
        
    def reenviar_mail(self):
        funciones.ver_bandeja(self)
        while True:
            opcion = input("\n¿Desea reenviar alguno de estos emails? (si/no): ").lower()
            if opcion == 'no':
                break
            elif opcion == 'si':
                try:
                    opcion = int(input("\nIngrese el número del email a reenviar (0 para volver): "))
                    if opcion == 0:
                        return
                        
                    if opcion > 0 and opcion <= len(self.bandeja):
                        email_a_reenviar = self.bandeja[opcion - 1]
                        destinatario = input("Ingrese email del nuevo destinatario: ")
                        
                        nuevo_email = Email(
                            self.mail,
                            destinatario,
                            f"FWD: {email_a_reenviar.asunto}",
                            f"---------- Email reenviado ----------\n{email_a_reenviar.cuerpo}"
                        )
                        
                        if self.celular.central_gmail.enviar_mail(nuevo_email):
                            print("Email reenviado exitosamente")
                    else:
                        print("Número de email inválido")
                except ValueError:
                    print("Por favor ingrese un número válido")
                    break
            else:
                print("Por favor, responda 'si' o 'no'")
        
            

    
    def enviar_mail(self):
        if not self.celular.datos_moviles:
            print("Error: Necesita activar los datos móviles para enviar emails")
            return
            
        destinatario = input("Ingrese email del destinatario: ")
        asunto = input("Ingrese asunto: ")
        cuerpo = input("Escriba su mensaje: ")
        
        nuevo_email = Email(
            self.mail,
            destinatario,
            asunto,
            cuerpo
        )
        
        self.celular.central_gmail.enviar_mail(nuevo_email)

        
            
    def bloquear_casillas(self):
        while True:
            casilla=input("ingrese la casilla que desea bloquear (No podra interactuar al estar bloqueada): ")
            try:
                if casilla in self.celular.central_gmail.usuarios_registrados:
                    self.casillas_bloqueadas.append(casilla) 
            except ValueError:
                print("Esa casilla es inexistente")
            finally:
                opcion=input("Desea volver a intentarlo? (si/no): ")
                if opcion.lower()=='no':
                    break
                elif opcion.lower() != 'si':
                    print("esa opcion es inexistente")
                    break 
    
    def menu(self):
        while True:
            opcion = input(f"""
EMAIL - {self.mail}
1. Ver todos los emails
2. Ver emails no leídos
3. Ver emails enviados
4. Enviar email
5. Bloquear casilla
6. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                funciones.ver_bandeja(self)
            elif opcion == "2":
                funciones.ver_bandeja(self, mostrar_no_leidos=True)
            elif opcion == "3":
                self.ver_bandeja_enviados()
            elif opcion == "4":
                self.enviar_mail()
            elif opcion == "5":
                self.bloquear_casillas()
            elif opcion == "6":
                break
            else:
                print("Opción inválida")


class App_Store(Aplicacion):
    def __init__(self, celular: Celular):
        super().__init__(celular)
        self.almacenamiento= 2 #ocupa 2gb
        celular.almacenamiento_disponible+=self.almacenamiento
        self.necesaria = True
        
    def descargar_app(self):
        if not self.celular.datos_moviles:
            print("Error: Necesita activar los datos móviles para descargar apps")
            return
            
        app = input("¿Qué app quiere descargar?: ")
        if app in self.celular.apps:
            print("Esta aplicación ya está instalada")
            return
            
        # Se crea un almacenamiento random  entre 0 y 2
        almacenamiento_de_nueva_app=random.uniform(0,2)
        #si pasa la verificacion este almacenamiento, se le pasa como atributo a la nueva app
        if self.celular.apps['configuracion'].validar_almacenamiento(almacenamiento_de_nueva_app):
            self.celular.apps[app] = Aplicacion(self.celular)
            self.celular.apps[app].almacenamiento=almacenamiento_de_nueva_app #se le pasa como atributo el almacenamiento ya verificado
            print(f"App '{app}' descargada exitosamente")
        

    def borrar_app(self):
        print("\nApps instaladas:")
        apps_borrables = []
        for nombre, app in self.celular.apps.items():
            estado = "(No se puede borrar)" if app.necesaria else ""
            print(f"- {nombre} {estado}")
            if not app.necesaria:
                apps_borrables.append(nombre)
                
        if not apps_borrables:
            print("No hay apps que se puedan borrar")
            return
            
        app = input("\n¿Qué app quiere borrar?: ")
        if app not in self.celular.apps:
            print("Esta aplicación no está instalada")
            return
            
        if self.celular.apps[app].necesaria:
            print("Esta aplicación no se puede borrar")
            return
            
        else:
            del self.celular.apps[app]
            self.celular.almacenamiento_disponible-= self.celular.apps[app].almacenamiento #se libera almacenamiento al borrar
        print(f"App '{app}' borrada exitosamente")
        
        
    
    def menu(self):
        while True:
            opcion = input("""
APP STORE
1. Descargar app
2. Borrar app
3. Ver apps instaladas
4. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                self.descargar_app()
            elif opcion == "2":
                self.borrar_app()
            elif opcion == "3":
                print("\nApps instaladas:", list(self.celular.apps.keys()))
            elif opcion == "4":
                break
            else:
                print("Opción inválida")
    

class Configuracion(Aplicacion):
    def __init__(self, celular: Celular):
        super().__init__(celular)
        self.almacenamiento=1.5 #ocupa gb
        celular.almacenamiento+=self.almacenamiento
        self.necesaria = True
        
    def cambiar_codigo(self):
        """Cambia el código de desbloqueo del celular"""
        
        # Si no hay código previo, simplemente pide el nuevo
        if self.celular.codigo is None:
            while True:
                try:
                    nuevo_codigo = int(input('Ingrese el nuevo código: '))
                    self.celular.codigo = nuevo_codigo
                    print("Código establecido exitosamente")
                    return
                except ValueError:
                    print("El código debe ser un número")
                
        # Si hay código previo, pide verificación
        if self.celular.codigo == int(input('Ingrese el código actual: ')):
            while True:
                try:
                    nuevo_codigo = int(input('Ingrese el nuevo código: '))
                    self.celular.codigo = nuevo_codigo
                    print("Código cambiado exitosamente")
                    return
                except ValueError:
                    print("El código debe ser un número")
        else:
            print("Código incorrecto")
        
    def activar_red_movil(self):
        #desactiva la red movil y manda la actualizacion a la central
        if self.celular.red_movil:
            print('La red movil ya esta activada')
        else:   
            if self.celular.num_telefonico in self.celular.central.dispositivos_registrados:
                self.celular.red_movil = True
                funciones.actualizar_bandeja(self.celular.apps['sms'])
                print("Red móvil activada")
            else:
                print('Tu celular no esta registrado en la central. No podes activar la red movil')
    
    def desactivar_red_movil(self):
        self.celular.apps['telefono'].terminar_llamada()
        self.celular.red_movil = False
        print("Red móvil desactivada")
        
        
    def toggle_disponibilidad(self):
        self.celular.disponible = not self.celular.disponible
        estado = "disponible" if self.celular.disponible else "no disponible"
        print(f"El celular ahora está {estado} para recibir llamadas")

    def toggle_datos_moviles(self):
        if not self.celular.red_movil:
            print("Error: Primero debe activar la red móvil")
            return
            
        self.celular.datos_moviles = not self.celular.datos_moviles
        estado = "activados" if self.celular.datos_moviles else "desactivados"
        #se actualiza la bandeja del mail cuando se prenden los datos
        if self.celular.datos_moviles:
            funciones.actualizar_bandeja(self.celular.apps['email'])
        print(f"Datos móviles {estado}")
        
    def validar_almacenamiento(self, almacenamiento_de_app: float):
        #se puede agregar esta app
        if self.celular.almacenamiento_disponible + almacenamiento_de_app<=self.celular.almacenamiento:
            self.celular.almacenamiento_disponible+=almacenamiento_de_app
            return True
        #ocupa mas espacio del disponible
        if self.celular.almacenamiento_disponible + almacenamiento_de_app>self.celular.almacenamiento: 
            print("No se puede descargar esta aplicacion debido a que ocupa mas del espacio que tiene disponible")
            return False

    def menu(self):
        while True:
            opcion = input("""
CONFIGURACIÓN
1. Cambiar código de desbloqueo
2. Activar red móvil
3. Desactivar red móvil
4. Cambiar disponibilidad para llamadas
5. Activar/Desactivar datos móviles
6. Volver

Ingrese una opción: """)
            
            if opcion == "1":
                self.cambiar_codigo()
            elif opcion == "2":
                self.activar_red_movil()
            elif opcion == "3":
                self.desactivar_red_movil()
            elif opcion == "4":
                self.toggle_disponibilidad()
            elif opcion == "5":
                self.toggle_datos_moviles()
            elif opcion == "6":
                break
            else:
                print("Opción inválida")
