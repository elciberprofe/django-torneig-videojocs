from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from random import choice, shuffle
from datetime import timedelta

from competicions.models import Torneig, Equip, Jugador, Partida, Videojoc

faker = Faker(["es_CA", "es_ES"])

class Command(BaseCommand):
    help = 'Crea un torneig de 16 equips i simula totes les fases fins la final'

    def add_arguments(self, parser):
        parser.add_argument('nom_torneig', type=str, help='Nom del torneig')
        parser.add_argument('nom_videojoc', type=str, help='Nom del videojoc')

    def handle(self, *args, **options):
        nom_torneig = options['nom_torneig']
        nom_videojoc = options['nom_videojoc']

        if Torneig.objects.filter(nom=nom_torneig).exists():
            self.stdout.write(self.style.WARNING(f"El torneig '{nom_torneig}' ja existeix."))
            return

        videojoc, _ = Videojoc.objects.get_or_create(nom=nom_videojoc)
        torneig = Torneig.objects.create(
            nom=nom_torneig, 
            videojoc=videojoc, 
            data_inici=timezone.now(),
            data_final=timezone.now() + timedelta(days=1)
            )
        torneig.save()
        self.stdout.write(self.style.SUCCESS(f"Creat el torneig: {nom_torneig}"))

        # Crear 16 equips amb jugadors
        equips = []
        for _ in range(16):
            ciutat = faker.city()
            nom_equip = f"{choice(['Team', 'Clan', 'Esports', 'Gaming'])} {ciutat}"
            equip = Equip.objects.create(
                nom=nom_equip, 
                ciutat=ciutat,
                videojoc=videojoc
                )
            equip.save()
            torneig.equips.add(equip)
            equips.append(equip)

            posicions = ["atacant", "defensor", "mixt"]
            for j in range(5):
                Jugador.objects.create(
                    nom=faker.name(),
                    nickname=faker.user_name(),
                    posicio=choice(posicions),
                    dorsal=j+1,
                    data_naixement=timezone.now() - timedelta(days=365*faker.random_int(18, 30)),
                    equip=equip
                )

        self.stdout.write(self.style.SUCCESS("Creats 16 equips amb jugadors."))

        # Simular fases
        fases = ['Octaus', 'Quarts', 'Semifinals', 'Final']
        puntuacions_possibles = [1, 3, 5, 10]
        ronda = 0

        while len(equips) > 1:
            fase = fases[ronda]
            self.stdout.write(self.style.NOTICE(f"\nSimulant fase: {fase} ({len(equips)} equips)"))

            shuffle(equips)
            guanyadors = []

            for i in range(0, len(equips), 2):
                equip1 = equips[i]
                equip2 = equips[i+1]

                punts1 = choice(puntuacions_possibles)
                punts2 = choice(puntuacions_possibles)

                # evitar empat
                while punts1 == punts2:
                    punts1 = choice(puntuacions_possibles)
                    punts2 = choice(puntuacions_possibles)

                # decidir guanyador
                if punts1 > punts2:
                    guanyador = equip1
                else:
                    guanyador = equip2

                # suma 1 punt extra al guanyador per passar de ronda
                extra = 1
                if guanyador == equip1:
                    punts1 += extra
                else:
                    punts2 += extra

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

        self.stdout.write(self.style.SUCCESS(f"\n🏆 Torneig completat! Guanyador: {equips[0].nom}"))