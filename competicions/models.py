from django.db import models

from django.core.exceptions import ValidationError

class Videojoc(models.Model):
    nom = models.CharField(max_length=100)
    descripcio = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='videojocs_logos/', blank=True, null=True)

    def __str__(self):
        return self.nom


class Torneig(models.Model):
    nom = models.CharField(max_length=100)
    videojoc = models.ForeignKey(Videojoc, on_delete=models.CASCADE)
    data_inici = models.DateField()
    data_final = models.DateField(blank=True, null=True)
    descripcio = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='tornejos_logos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nom} ({self.videojoc.nom})"


class Equip(models.Model):
    nom = models.CharField(max_length=100)
    ciutat = models.CharField(max_length=100, blank=True, null=True)
    videojoc = models.ForeignKey(Videojoc, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='equips_logos/', blank=True, null=True)

    def __str__(self):
        return self.nom


class Jugador(models.Model):
    nom = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50)
    equip = models.ForeignKey(Equip, on_delete=models.SET_NULL, blank=True, null=True)
    data_naixement = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.nickname} ({self.equip.nom if self.equip else 'Sense equip'})"
    

class Partida(models.Model):
    torneig = models.ForeignKey('Torneig', on_delete=models.CASCADE, related_name='partides')
    data_hora = models.DateTimeField()
    equip1 = models.ForeignKey('Equip', on_delete=models.CASCADE, related_name='partides_com_equip1')
    equip2 = models.ForeignKey('Equip', on_delete=models.CASCADE, related_name='partides_com_equip2')
    puntuacio_equip1 = models.IntegerField()
    puntuacio_equip2 = models.IntegerField()

    def __str__(self):
        return f"{self.equip1.nom} vs {self.equip2.nom} - {self.torneig.nom} ({self.data_hora.strftime('%d/%m/%Y %H:%M')})"

    @property
    def resultat(self):
        if self.puntuacio_equip1 > self.puntuacio_equip2:
            return 'equip1'
        elif self.puntuacio_equip2 > self.puntuacio_equip1:
            return 'equip2'
        else:
            return 'empat'

    def clean(self):
        # Validar que els equips no siguin iguals
        if self.equip1 == self.equip2:
            raise ValidationError("Els equips d'una partida no poden ser el mateix.")
