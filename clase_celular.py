from clase_central import Central, Comunicacion
from collections import deque
from listaenlazada import ListaEnlazada, Nodo
from clase_email import Email


class Celular:
    
    central = Central()
    celulares_registrados = []

    def __init__(self, identificacion, nombre, modelo, sistema_operativo, version, RAM, almacenamiento, num_telefonico) :
        
        #atributos bases
        #falta agregar validadores
        self.identificacion=identificacion 
        self.nombre=nombre
        self.modelo=modelo
        self.sistema_operativo=sistema_operativo
        self.version=version
        self.RAM=RAM
        self.almacenamiento=almacenamiento
        self.num_telefonico=num_telefonico
        self.datos_moviles=True

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
            print("El celular se ha prendido")

        else:
            #ACA deberia DESCONECTAR CON LA CENTRAL
            self.red_movil = False
            self.desbloqueado = False
            if self.llamada_actual != None:
                
                self.apps['telefono'].terminar_llamada() # Se termina la llamada en curso en el caso de existir
            print("Has apagado el celular")

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
                opcion = input(f"""
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
            print("Aplicación no encontrada")


    #agregar contrasenia    
    def bloq_desbloq(self):
        if self.desbloqueado:
            # Si está desbloqueado, simplemente lo bloqueamos
            self.desbloqueado = False
            print("Has bloqueado el celular")
            return
        
        # Si está bloqueado, verificamos si tiene código
        if self.codigo is None:
            self.desbloqueado = True
            print("El celular se ha desbloqueado")
            return
        
        # Si tiene código, pedimos que lo ingrese
        intentos = 3
        while intentos > 0:
            try:
                codigo_ingresado = int(input('Ingrese el código de desbloqueo: '))
                if codigo_ingresado == self.codigo:
                    self.desbloqueado = True
                    print("El celular se ha desbloqueado")
                    return
                else:
                    intentos -= 1
                    if intentos > 0:
                        print(f"Código incorrecto. Te quedan {intentos} intentos")
                    else:
                        print("Demasiados intentos fallidos. Vuelva a intentarlo. ")
            except ValueError:
                print("El código debe ser un número")
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
        self.necesaria = False


class Contactos(Aplicacion):

    def __init__(self, celular: Celular):
        super().__init__(celular)
        self.lista_de_contactos={}
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
        self.bandeja_sms= ListaEnlazada() #lista enlazada 
        self.contactos=contactos
        self.mensajes_en_espera = deque() # Mensajes que te llegaron cuando no tenias la red movil activa
        self.necesaria = True
        
    def enviar_mensaje(self):
        # Primero mostramos los contactos disponibles
        self.contactos.ver_contactos()
        
        # Pedimos el destinatario (puede ser un número directo o nombre de contacto)
        receptor = input("\nIngrese un numero o un nombre de contacto: ")
        
        # Si el receptor está en las claves (nombres) de contactos, obtenemos su número
        if receptor in self.contactos.lista_de_contactos:  # Cambió esta línea
            receptor = self.contactos.lista_de_contactos[receptor]  # Cambió esta línea
        else:
            # Si no es un contacto, verificamos que sea un número válido
            if not receptor.isdigit() or len(receptor) != 8:
                print("Número inválido. Debe contener 8 dígitos.")
                return
            
        mensaje = input("Escriba su mensaje: ")
        
        # La central maneja la comunicación
        self.celular.central.comunicacion_sms(self.celular, receptor, mensaje)
        
    def recibir_mensaje(self, mensaje: Comunicacion):
        self.bandeja_sms.agregarInicio(Nodo(mensaje))
        
    def actualizar_bandeja(self):
        if self.celular.red_movil:
            print(f'Tenes {len(self.mensajes_en_espera)} mensajes nuevos. ')
            while self.mensajes_en_espera:
                self.bandeja_sms.agregarInicio(Nodo(self.mensajes_en_espera.popleft()))
        else:
            print('No se pueden actualizar los mensajes. Activar la red movil. ')

    def ver_bandeja_sms(self):
        print(self.bandeja_sms)
    
    def eliminar_mensajes(self):
        """Permite al usuario eliminar mensajes específicos"""
        if self.bandeja_sms.esVacia():
            print("No hay mensajes para eliminar")
            return
            
        print("\nMensajes en la bandeja:")
        actual = self.bandeja_sms.inicio
        indice = 1
        while actual:
            print(f"{indice}. {actual.dato}")
            actual = actual.siguiente
            indice += 1
            
        try:
            seleccion = int(input("\nIngrese el número del mensaje a eliminar (0 para cancelar): "))
            if seleccion == 0:
                return
                
            if 1 <= seleccion <= self.bandeja_sms.tamanio():  # Necesitamos agregar este método
                # Eliminamos el mensaje seleccionado
                self.bandeja_sms.eliminarPosicion(seleccion - 1)  # Y este método
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
                self.ver_bandeja_sms()
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
        self.historial_llamadas=deque() #Pila para ver cual llega primero
        self.contactos=contactos
        self.necesaria = True
    
    def llamar(self):

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
        

        self.celular.central.comunicacion_telefonica(self, receptor)
    
    def recibir_llamada(self, comunicacion: Comunicacion):

        # Si el celular no esta en llamada se le pide aceptar o rechazar la llamada
        
        if self.celular.disponible:
            # Buscamos si el número que llama está en los contactos
            nombre_contacto = None
            for nombre, numero in self.celular.contactos.lista_de_contactos.items():
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
            print(llamada)

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
        self.mail = f"{celular.nombre.lower().replace(' ', '')}@gmail.com"
        self.bandeja_email = deque()  # pila para los emails
        self.necesaria = True
    


    def ver_bandeja_mails(self, mostrar_no_leidos=False):
        if not self.bandeja_email:
            print("No hay emails en la bandeja")
            return
            
        print("\nBandeja de entrada:")
        for email in self.bandeja_email:
            if not mostrar_no_leidos or not email.leido:
                print(email)
                email.leido = True
    
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

        print("Email enviado exitosamente")
    
    def recibir_mail(self, email):
        """Método llamado cuando llega un nuevo email"""
        if self.celular.datos_moviles:
            self.bandeja_email.appendleft(email)  # Los más recientes aparecen primero
    
    def menu(self):
        while True:
            opcion = input(f"""
            EMAIL - {self.mail}
            1. Ver todos los emails
            2. Ver emails no leídos
            3. Enviar email
            4. Volver
            Ingrese una opción: """)
            
            if opcion == "1":
                self.ver_bandeja_mails()
            elif opcion == "2":
                self.ver_bandeja_mails(mostrar_no_leidos=True)
            elif opcion == "3":
                self.enviar_mail()
            elif opcion == "4":
                break
            else:
                print("Opción inválida")


class App_Store(Aplicacion):
    def __init__(self, celular: Celular):
        super().__init__(celular)
        
    def descargar_app(self):
        if not self.celular.datos_moviles:
            print("Error: Necesita activar los datos móviles para descargar apps")
            return
            
        app = input("¿Qué app quiere descargar?: ")
        if app in self.celular.apps:
            print("Esta aplicación ya está instalada")
            return
            
        # Aquí se podrían agregar validaciones de apps disponibles
        self.celular.apps[app] = Aplicacion(self.celular)
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
            
        del self.celular.apps[app]
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
                self.celular.apps['sms'].actualizar_bandeja()
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
        print(f"Datos móviles {estado}")

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
