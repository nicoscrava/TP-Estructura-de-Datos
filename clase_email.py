from datetime import datetime
class Email:
    def __init__(self, emisor, destinatario, asunto, cuerpo):
        self.emisor = emisor
        self.destinatario = destinatario
        self.asunto = asunto
        self.cuerpo = cuerpo
        self.fecha = datetime.now()
        self.leido = False
        
    def __str__(self):
        estado = "No leído" if not self.leido else "Leído"
        return f"[{estado}] De: {self.emisor} - Asunto: {self.asunto} - Fecha: {self.fecha}"