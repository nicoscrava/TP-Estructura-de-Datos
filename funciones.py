# funciones que comparten SMS Y EMAIL
from clase_listaenlazada import *

def actualizar_bandeja(app):
    cantidad_mensajes = len(app.en_espera)
    if cantidad_mensajes > 0:
        print(f'\nTenes {cantidad_mensajes} mensaje/s nuevos')
        while app.en_espera:
            mensaje = app.en_espera.popleft()
            print(mensaje)  # Mostramos el mensaje cuando se recibe
            app.bandeja.agregarInicio(Nodo(mensaje))
    else:
        print('\nNo hay mensajes nuevos.')
        
def recibir_mensaje(app, mensaje):
    app.bandeja.agregarInicio(Nodo(mensaje))
    
def ver_bandeja(app):
    if app.bandeja.esVacia():
        print("No hay mensajes en la bandeja")
        return
            
    print("\nBandeja de mensajes:")
    actual = app.bandeja.inicio
    while actual:
        # Pasamos True si el emisor del mensaje es este celular
        vista_emisor = actual.dato.emisor == app.celular
        print(actual.dato.__str__(vista_emisor))
        actual = actual.siguiente