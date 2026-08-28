from django.db import models

class Usuario(models.Model):
    nome = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.nome or "Usuário sem nome"

class Peca(models.Model):
    categoria = models.CharField(max_length=100, null=True, blank=True)
    cor = models.CharField(max_length=50, null=True, blank=True)
    estilo = models.CharField(max_length=50, null=True, blank=True)
    clima = models.CharField(max_length=50, null=True, blank=True)
    imagem = models.ImageField(upload_to='pecas/', null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.categoria} - {self.cor}"

class Look(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    nome_look = models.CharField(max_length=100, null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)
    pecas = models.ManyToManyField(Peca)

    def __str__(self):
        return self.nome_look or "Look"