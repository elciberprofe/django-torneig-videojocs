from django.core.management.base import BaseCommand
from django.utils import timezone
from random import choice, shuffle

from competicions.models import Torneig, Partida

class Command(BaseCommand):
    help = 'Genera partides per a un torneig existent amb equips assignats'

    def add_arguments(self, parser):
        parser.add_argument('nom_torneig', type=str, help='Nom del torneig')

    def handle(self, *args, **options):
        nom_torneig = options['nom_torneig']

        try:
            torneig = Torneig.objects.get(nom=nom_torneig)
        except Torneig.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No s'ha trobat el torneig '{nom_torneig}'."))
            return

        equips = list(torneig.equips.all())

        if len(equips) < 2 or (len(equips) & (len(equips)-1)) != 0:
            self.stdout.write(self.style.ERROR("El nombre d'equips ha de ser una potència de 2 (2, 4, 8, 16...)."))
            return

        fases = ['Octaus', 'Quarts', 'Semifinals', 'Final']
        puntuacions_possibles = [1, 3, 5, 10]
        ronda = 0

        self.stdout.write(self.style.SUCCESS(f"Generant partides pel torneig: {torneig.nom}"))

        while len(equips) > 1 and ronda < len(fases):
            fase = fases[ronda]
            self.stdout.write(self.style.NOTICE(f"\nFase: {fase} ({len(equips)} equips)"))

            shuffle(equips)
            guanyadors = []

            for i in range(0, len(equips), 2):
                equip1 = equips[i]
                equip2 = equips[i+1]

                punts1 = choice(puntuacions_possibles)
                punts2 = choice(puntuacions_possibles)
                while punts1 == punts2:
                    punts2 = choice(puntuacions_possibles)

                if punts1 > punts2:
                    guanyador = equip1
                    punts1 += 1
                else:
                    guanyador = equip2
                    punts2 += 1

                Partida.objects.create(
                    torneig=torneig,
                    ronda=fase,
                    equip1=equip1,
                    equip2=equip2,
                    puntuacio_equip1=punts1,
                    puntuacio_equip2=punts2,
                    data_hora=timezone.now()
                )

                guanyadors.append(guanyador)
                self.stdout.write(f"{equip1.nom} ({punts1}) vs {equip2.nom} ({punts2}) → Guanya: {guanyador.nom}")

            equips = guanyadors
            ronda += 1

        if equips:
            self.stdout.write(self.style.SUCCESS(f"\n🏆 Guanyador del torneig: {equips[0].nom}"))