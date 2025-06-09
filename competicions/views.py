from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Sum, Count
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from .models import *


#Mostra un llistat amb tots els tornejos creats
def llistat_tornejos(request):
    tornejos = Torneig.objects.all().order_by('-data_inici')
    return render(request, "llistat_tornejos.html", {
        "tornejos": tornejos
    })

#Vista per taula del torneig
@login_required
def quadre_torneig(request, torneig_id):
    torneig = Torneig.objects.get(id=torneig_id)
    partides = Partida.objects.filter(torneig=torneig).order_by('data_hora')

    # Organitzem les partides per ronda
    rondes = {'Octaus': [], 'Quarts': [], 'Semifinals': [], 'Final': []}
    for partida in partides:
        if partida.ronda in rondes:
            rondes[partida.ronda].append(partida)

    return render(request, 'quadre_torneig.html', {
        'torneig': torneig,
        'rondes': rondes,
    })

#Mostra el detall d'un torneig (template format: octaus --> quarts --> semis i final)
#Puntuen per guanyar la ronda 1 punt, 3 punts, 5 punts i 10 punts.
#Suma 1 punt el perdedor mes enllà d'octaus
@login_required
def detall_torneig(request, torneig_id):
    torneig = get_object_or_404(Torneig, pk=torneig_id)
    
    partides = Partida.objects.filter(torneig=torneig)

    eliminatoria = {
        "OCTAUS": partides.filter(ronda="OCTAUS"),
        "QUARTS": partides.filter(ronda="QUARTS"),
        "SEMIS": partides.filter(ronda="SEMIS"),
        "FINAL": partides.filter(ronda="FINAL"),
    }

    equips1 = Equip.objects.filter(partides_com_equip1__torneig=torneig)
    equips2 = Equip.objects.filter(partides_com_equip2__torneig=torneig)
    equips = list(set(list(equips1) + list(equips2)))

    puntuacio = {}

    for equip in equips:
        puntuacio[equip.nom] = 0
        partides = Partida.objects.filter(
            torneig=torneig
        ).filter(models.Q(equip1=equip) | models.Q(equip2=equip))

        for partida in partides:
            ronda = partida.ronda
            guanyador = partida.equip1 if partida.resultat == 'equip1' else partida.equip2
            perdedor = partida.equip2 if partida.resultat == 'equip1' else partida.equip1

            if equip == guanyador:
                if ronda == 'Octaus':
                    puntuacio[equip.nom] += 1
                elif ronda == 'Quarts':
                    puntuacio[equip.nom] += 3
                elif ronda == 'Semis':
                    puntuacio[equip.nom] += 5
                elif ronda == 'Final':
                    puntuacio[equip.nom] += 10
            elif equip == perdedor and ronda != 'Octaus':
                puntuacio[equip.nom] += 1

    # Obtenir una llista de tuples (equip, punts) ordenada de major a menor segons punts
    classificacio = sorted(
    puntuacio.items(),
    key=lambda parella: parella[1],
    reverse=True
    )

    return render(request, "detall_torneig.html", {
        "torneig": torneig,
        "eliminatoria": eliminatoria,
        "classificacio": classificacio
    })


#Funció de la Vista per classificació GENERAL
def calcular_punts_torneig(torneig):
    # Similar a la lògica de detall_torneig per calcular punts per equip en un torneig
    partides = Partida.objects.filter(torneig=torneig)
    
    equips1 = Equip.objects.filter(partides_com_equip1__torneig=torneig)
    equips2 = Equip.objects.filter(partides_com_equip2__torneig=torneig)
    equips = list(set(list(equips1) + list(equips2)))

    puntuacio = defaultdict(int)

    for equip in equips:
        partides_equip = partides.filter(models.Q(equip1=equip) | models.Q(equip2=equip))

        for partida in partides_equip:
            ronda = partida.ronda
            guanyador = partida.equip1 if partida.resultat == 'equip1' else partida.equip2
            perdedor = partida.equip2 if partida.resultat == 'equip1' else partida.equip1
            
            if equip == guanyador:
                if ronda == 'Octaus':
                    puntuacio[equip.nom] += 1
                elif ronda == 'Quarts':
                    puntuacio[equip.nom] += 3
                elif ronda == 'Semis':
                    puntuacio[equip.nom] += 5
                elif ronda == 'Final':
                    puntuacio[equip.nom] += 10
            elif equip == perdedor and ronda != 'Octaus':
                puntuacio[equip.nom] += 1

    return puntuacio

#Vista classificació general
@login_required
def classificacio_tornejos(request):
    tornejos = Torneig.objects.all()

    puntuacio_global = defaultdict(int)

    for torneig in tornejos:
        punts_torneig = calcular_punts_torneig(torneig)
        for equip, punts in punts_torneig.items():
            puntuacio_global[equip] += punts

    # Ordenar per punts descendent
    classificacio = sorted(puntuacio_global.items(), key=lambda x: x[1], reverse=True)

    return render(request, 'classificacio_tornejos.html', {
        'classificacio': classificacio,
    })