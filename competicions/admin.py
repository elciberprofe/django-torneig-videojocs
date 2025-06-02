from django.contrib import admin

from .models import Videojoc, Torneig, Equip, Jugador, Partida

admin.site.register(Videojoc)
admin.site.register(Torneig)
admin.site.register(Equip)
admin.site.register(Jugador)
admin.site.register(Partida)
