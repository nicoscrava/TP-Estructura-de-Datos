from datetime import datetime

class Email:
    """
    Clase que representa un correo electrónico.

    Attributes:
        emisor (str): Dirección de email del remitente
        destinatario (str): Dirección de email del destinatario 
        asunto (str): Asunto del correo
        cuerpo (str): Contenido del mensaje
        fecha (datetime): Fecha y hora de creación del email
        leido (bool): Indica si el email fue leído por el destinatario
    """
    def __init__(self, emisor, destinatario, asunto, cuerpo):
        self.emisor = emisor
        self.destinatario = destinatario
        self.asunto = asunto
        self.cuerpo = cuerpo
        self.fecha = datetime.now()
        self.leido = False
        
    def __str__(self, vista_emisor=False):
        if not vista_emisor:
            estado = "No leído" if not self.leido else "Leído"
            return f"[{estado}] De: {self.emisor} - Asunto: {self.asunto} - Fecha: {self.fecha}"
        else:
            return f"Para: {self.destinatario} - Asunto: {self.asunto} - Fecha: {self.fecha}"
    

class CentralGmail:
    """
    Clase que representa la central de correo electrónico Gmail.
    
    Gestiona el envío y recepción de emails entre usuarios registrados.
    
    Attributes:
        usuarios_registrados (dict): Diccionario que mapea direcciones de email a objetos Celular
        registro_mails (list): Lista que almacena el historial de emails enviados
    """
    def __init__(self):
        self.usuarios_registrados = {}
        self.registro_mails = [] 
        
    def validar_usuarios(self, emisor: str, receptor: str):
        """
        Valida que el emisor y receptor sean usuarios registrados y que el emisor no esté bloqueado.
        
        Args:
            emisor (str): Dirección de email del remitente
            receptor (str): Dirección de email del destinatario
            
        Returns:
            bool: True si la validación es exitosa, False en caso contrario
        """
        if emisor not in self.usuarios_registrados:
            print(f"La direccion de mail {emisor} no se encuentra registrada.")
            return False
        if receptor not in self.usuarios_registrados:
            print(f"La direccion de mail {receptor} no se encuentra registrada.")
            return False  
        
        elif emisor in self.usuarios_registrados[receptor].apps["email"].casillas_bloqueadas:
            print("La casilla a la que le intentas enviar un email te ha bloqueado.")
            return False
            
        return True

    def enviar_mail(self, mail: Email):
        """
        Envía un email entre usuarios registrados.
        
        Args:
            mail (Email): Objeto Email con los datos del correo a enviar
            
        Returns:
            bool: True si el envío fue exitoso, False en caso contrario
            
        El email se agrega a la bandeja de entrada del receptor si tiene datos móviles,
        sino se agrega a la cola de espera. También se agrega a la bandeja de enviados
        del emisor y al registro histórico de la central.
        """
        if self.validar_usuarios(mail.emisor, mail.destinatario):
            receptor = self.usuarios_registrados[mail.destinatario]
            emisor = self.usuarios_registrados[mail.emisor]
            
            if receptor.datos_moviles:
                receptor.apps["email"].recibir_mensaje(mail)
            else:
                receptor.apps["email"].en_espera.append(mail)
            
            emisor.apps["email"].bandeja_enviados.append(mail)
            self.registro_mails.append(mail)
            return True
        return False
