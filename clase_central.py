#from main import Celular

class Comunicacion:
    def __init__(self, emisor: 'Celular', receptor: 'Celular'):
        self.emisor = emisor
        self.receptor = receptor
    
    def _obtener_identificador_emisor(self):
        if self.emisor.nombre in self.receptor.apps['contactos'].lista_de_contactos:
            return self.emisor.nombre
        return self.emisor.num_telefonico

class SMS(Comunicacion):
    def __init__(self, emisor: 'Celular', receptor: 'Celular', contenido: str):
        super().__init__(emisor, receptor)
        self.contenido = contenido
        self.tipo = 'sms'
    
    def __str__(self, vista_emisor=False):
        if vista_emisor:
            return f'Mensaje enviado a: {self.receptor.num_telefonico}\n Mensaje: {self.contenido}'
        return f'Mensaje de: {self._obtener_identificador_emisor()}\n Mensaje: {self.contenido}'

class Llamada(Comunicacion):
    def __init__(self, emisor: 'Celular', receptor: 'Celular'):
        super().__init__(emisor, receptor)
        self.tipo = 'llamada'
        self.llamada_aceptada = False
        self.llamada_en_transcurso = False
    
    def __str__(self, vista_emisor=False):
        estado = 'aceptada' if self.llamada_aceptada else 'perdida'
        if vista_emisor:
            return f'Llamada {estado} a {self.receptor.num_telefonico}'
        return f'Llamada {estado} de {self._obtener_identificador_emisor()}'
    

class Central:

    def __init__(self):
        self.dispositivos_registrados = {}
        self.registro_comunicaciones = [] #revisar tipo de dato

    # Genera un informe legible de las comunicaciones
    def generar_informe(self):
        try:
            with open('informe_comunicaciones.txt', 'w') as archivo:
                for comunicacion in self.registro_comunicaciones:
                    if isinstance(comunicacion, SMS):
                        archivo.write(f"SMS de {comunicacion.emisor.nombre} - {comunicacion.emisor.num_telefonico} a {comunicacion.receptor.nombre} - {comunicacion.receptor.num_telefonico}\n")
                    elif isinstance(comunicacion, Llamada):
                        estado = "aceptada" if comunicacion.llamada_aceptada else "rechazada"
                        archivo.write(f"Llamada {estado} de {comunicacion.emisor.num_telefonico} a {comunicacion.receptor.num_telefonico}\n")
        except Exception as e:
            print(f"Error al generar el informe: {e}")

    def alta_dispositivo(self, celular: 'Celular'):
        self.dispositivos_registrados[celular.num_telefonico] = celular

    def validar_estado_celular(self, celular: 'Celular', es_emisor, es_llamada=False):
        # Si el dispositivo celular no esta registrado en la red se avisa que esta fuera de servicio y devuelve False
        if not celular.red_movil:
            if es_emisor:
                print('Tu celular esta fuera de servicio') 
            return False
        
        # Si se trata de una llamada y no esta disponible el celular se avisa y devuelve False
        if es_llamada and not celular.disponible:
            print(f'El numero {celular.num_telefonico} no se encuentra disponible.')
            return False
        
        return True

    def comunicacion_sms(self, celular_emisor: 'Celular', receptor: str, mensaje: str):
        if receptor not in self.dispositivos_registrados:
            print(f'El número {receptor} no se encuentra registrado en la red.')
        else:
            celular_receptor = self.dispositivos_registrados[receptor]
        
            # Si el emisor no esta en la central, no se envia el mensaje
            if self.validar_estado_celular(celular_emisor, True):
                # Creamos la comunicación antes de validar el estado del receptor
                comunicacion = SMS(celular_emisor, celular_receptor, mensaje)
                
                # Si el receptor se puede comunicar, el receptor recibe el mensaje y se crea el registro
                if self.validar_estado_celular(celular_receptor, False):
                    celular_receptor.apps['sms'].recibir_mensaje(comunicacion)
                    self.registro_comunicaciones.append(comunicacion)
                    print("\nMensaje enviado exitosamente")
                else:
                    # Si el receptor no está disponible, guardamos el mensaje en espera
                    celular_receptor.apps['sms'].mensajes_en_espera.append(comunicacion)
                    print(f"\nEl número {receptor} está fuera de servicio.")
                    print("Mensaje enviado. El destinatario lo recibirá cuando active su red móvil")

    def comunicacion_telefonica(self, celular_emisor: 'Celular', receptor: str):

        if receptor not in self.dispositivos_registrados:
            print(f'\nEl número {receptor} no se encuentra registrado en la red.')
            
        else:
            celular_receptor = self.dispositivos_registrados[receptor]

            # Si el receptor se puede comunicar se crea la comunicacion 
            if self.validar_estado_celular(celular_emisor, True, True):
                if self.validar_estado_celular(celular_receptor, False, True):
                    
                    comunicacion = Llamada(celular_emisor, celular_receptor)
                    celular_receptor.apps['telefono'].historial_llamadas.append(comunicacion)
                    celular_emisor.apps['telefono'].historial_llamadas.append(comunicacion)

                    # Si se acepta la llamada, se le cambia el atributo llamada_aceptada de la comunicacion
                    if celular_receptor.apps['telefono'].recibir_llamada(comunicacion):
                        comunicacion.llamada_aceptada = True
                        print(f'\nEstas en llamada con {receptor}')
                        celular_emisor.disponible = False
                        celular_emisor.llamada_actual = comunicacion
                        comunicacion.llamada_en_transcurso = True


                    # Si rechaza la llamada el atributo llamada_aceptada queda como False
                    else:

                        print('\nLlamada rechazada.')

                    # Se agrega la comunicacion al registro
                    self.registro_comunicaciones.append(comunicacion)

    def terminar_comunicacion_telefonica(self, comunicacion: Llamada):
        comunicacion.llamada_en_transcurso = False
        comunicacion.emisor.disponible = True
        comunicacion.receptor.disponible = True
        comunicacion.emisor.llamada_actual = None
        comunicacion.receptor.llamada_actual = None
        
    def ver_dispositivos(self):
        # Verifica si hay dispositivos registrados
        if not self.dispositivos_registrados:
            print("No hay dispositivos registrados")
            return False
            
        # Muestra la lista enumerada de dispositivos con su información
        print("\nDispositivos registrados:")
        for i, (numero, celular) in enumerate(self.dispositivos_registrados.items(), 1):
            estado_red = "Activada" if celular.red_movil else "Desactivada"
            print(f"{i}. Número: {numero} - Nombre: {celular.nombre} - Red móvil: {estado_red}")
        return True

    def dar_baja_dispositivo(self):
        # Si no hay dispositivos, termina la función
        if not self.ver_dispositivos():
            return
            
        # Solicita al usuario seleccionar un dispositivo para dar de baja
        seleccion = int(input("\nSeleccione el número del dispositivo a dar de baja (0 para cancelar): "))
        if seleccion == 0:
            return
            
        # Verifica que la selección sea válida
        if 1 <= seleccion <= len(self.dispositivos_registrados):
            # Obtiene el número de teléfono correspondiente a la selección
            dispositivo = list(self.dispositivos_registrados.values())[seleccion-1]
            # Da de baja el dispositivo usando el método existente
            dispositivo.red_movil = False
            del self.dispositivos_registrados[dispositivo.num_telefonico]

            print(f"Dispositivo de {dispositivo.nombre} con numero {dispositivo.num_telefonico} dado de baja exitosamente")
        else:
            print("Selección inválida")

    def menu_admin(self):
        # Menú principal que se ejecuta en un loop hasta que el usuario elija salir
        while True:
            opcion = input("""
            MENU ADMINISTRADOR
            1. Ver dispositivos registrados
            2. Generar informe de comunicaciones
            3. Dar de baja dispositivo
            4. Volver
            Ingrese una opción: """)

            # Procesa la opción seleccionada
            if opcion == "1":
                self.ver_dispositivos()
            elif opcion == "2":
                self.generar_informe()
            elif opcion == "3":
                self.dar_baja_dispositivo()
            elif opcion == "4":
                break
            else:
                print("Opción inválida")