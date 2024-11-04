#from main import Celular

class Comunicacion:
    def __init__(self, tipo: str, emisor: 'Celular', receptor: 'Celular', contenido=None):
        self.tipo = tipo
        self.emisor = emisor
        self.receptor = receptor
        self.contenido = contenido
        if self.tipo == 'llamada':
            self.llamada_aceptada=False
            self.llamada_en_transcurso = False
        
    def __str__(self):
        if self.tipo == 'sms':
            if self.emisor.nombre in self.receptor.apps['contactos'].lista_de_contactos:
                return f'Mensaje de: {self.emisor.nombre}\n Mensaje: {self.contenido}'
            else:
                return f'Mensaje de: {self.emisor.num_telefonico}\n Mensaje: {self.contenido}'
        elif self.tipo == 'llamada':
            # Si la llamada fue aceptada
            if self.llamada_aceptada:
                # Si el emisor está en los contactos del receptor, mostramos el nombre
                if self.emisor.nombre in self.receptor.apps['contactos'].lista_de_contactos:
                    return f'Llamada aceptada de {self.emisor.nombre}'
                # Si no está en contactos, mostramos el número
                else:
                    return f'Llamada aceptada de {self.emisor.num_telefonico}'
            # Si la llamada no fue aceptada (llamada perdida)
            else:
                # Si el emisor está en los contactos del receptor, mostramos el nombre
                if self.emisor.nombre in self.receptor.apps['contactos'].lista_de_contactos:
                    return f'Llamada perdida de {self.emisor.nombre}'
                # Si no está en contactos, mostramos el número
                else:
                    return f'Llamada perdida de {self.emisor.num_telefonico}'
             
        

class Central:

    def __init__(self):
        self.dispositivos_registrados = {}
        self.registro_comunicaciones = [] #revisar tipo de dato

    # Genera un informe legible de las comunicaciones
    def generar_informe(self):
        try:
            with open('informe_comunicaciones.txt', 'w') as archivo:
                for comunicacion in self.registro_comunicaciones:
                    if comunicacion.tipo == 'sms':
                        archivo.write(f"SMS de {comunicacion.emisor.num_telefonico} a {comunicacion.receptor}\n")
                    else:
                        estado = "aceptada" if comunicacion.llamada_aceptada else "rechazada"
                        archivo.write(f"Llamada {estado} de {comunicacion.emisor.num_telefonico} a {comunicacion.receptor.num_telefonico}\n")
        except Exception as e:
            print(f"Error al generar el informe: {e}")

    def alta_dispositivo(self, celular: 'Celular'):
        self.dispositivos_registrados[celular.num_telefonico] = celular

    def baja_dispositivo(self, celular: 'Celular'):
        try:
            celular.red_movil = False
            del self.dispositivos_registrados[celular.num_telefonico]
        except KeyError:
            print(f'El telefono con numero {celular.num_telefonico} no se encuentra en la red.')
    
    def validar_estado_celular(self, celular: 'Celular', es_emisor, es_llamada=False):

        # la validacion para la emision del mensaje se realiza desde el ceular emisor mismo
        
        # Si el dispositivo celular no esta registrado en la red se avisa que esta fuera de servicio y devuelve False
        if not celular.red_movil:
            if es_emisor:
                print('Tu celular esta fuera de servicio') 
            else:
                print(f'El numero {celular.num_telefonico} esta fuera de servicio.')
            return False
        
        # Si se trata de una llamada y no esta disponible el celular se avisa y devuelve False
        if es_llamada and not celular.disponible:
            print(f'El numero {celular.num_telefonico} no se encuentra disponible.')
            return False
        
        # Devuelve True si se puede realizar la comunicacion
        
        return True

    def comunicacion_sms(self, celular_emisor: 'Celular', receptor: str, mensaje: str):

        if receptor not in self.dispositivos_registrados:
            print(f'El número {receptor} no se encuentra registrado en la red.')
            
        else:
            celular_receptor = self.dispositivos_registrados[receptor]
        
            # Si el emisor no esta en la central, no se envia el mensaje
            if self.validar_estado_celular(celular_emisor, True):
                # Si el receptor se puede comunicar, el receptor recibe el mensaje y se crea el registro
                comunicacion = Comunicacion('sms', celular_emisor, celular_receptor, mensaje)
                if self.validar_estado_celular(celular_receptor, False):
                    
                    celular_receptor.apps['sms'].recibir_mensaje(comunicacion)
                    self.registro_comunicaciones.append(comunicacion)
                
                else:
                    celular_receptor.apps['sms'].mensajes_en_espera.append(comunicacion)

                
    def comunicacion_telefonica(self, celular_emisor: 'Celular', receptor: str):

        if receptor not in self.dispositivos_registrados:
            print(f'El número {receptor} no se encuentra registrado en la red.')
            
        else:
            celular_receptor = self.dispositivos_registrados[receptor]

            # Si el receptor se puede comunicar se crea la comunicacion 
            if self.validar_estado_celular(celular_emisor):
                if self.validar_estado_celular(celular_receptor, True):
                    
                    comunicacion = Comunicacion('llamada', celular_emisor, receptor)
                    celular_receptor.apps['telefono'].historial_llamadas.append(comunicacion)
                    celular_emisor.apps['telefono'].historial_llamadas.append(comunicacion)

                    # Si se acepta la llamada, se le cambia el atributo llamada_aceptada de la comunicacion
                    if celular_receptor.apps['telefono'].recibir_llamada(comunicacion):
                        comunicacion.llamada_aceptada = True
                        print(f'Estas en llamada con {receptor}')
                        celular_emisor.disponible = False
                        celular_emisor.llamada_actual = comunicacion
                        comunicacion.llamada_en_transcurso = True


                    # Si rechaza la llamada el atributo llamada_aceptada queda como False
                    else:

                        print('Llamada rechazada.')

                # Se agrega la comunicacion al registro
                self.registro_comunicaciones.append(comunicacion)

    def terminar_comunicacion_telefonica(self, comunicacion: Comunicacion):
        comunicacion.llamada_en_transcurso = False
        comunicacion.emisor.disponible = True
        comunicacion.receptor.disponible = True
        comunicacion.emisor.llamada_actual = None
        comunicacion.receptor.llamada_actual = None
        
