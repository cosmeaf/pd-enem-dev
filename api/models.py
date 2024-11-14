import datetime
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from django.db import models
import uuid


class UserProfile(models.Model):
    REGISTRATION_STATUS_CHOICES = [
        ('aprovado', 'Aprovado'),
        ('em_andamento', 'Em Andamento'),
        ('matriculado', 'Matriculado'),
        ('reprovado', 'Reprovado'),
        ('espera', 'Espera'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome_completo = models.CharField(max_length=255, null=True, blank=True)
    cpf = models.CharField(max_length=11, unique=True, null=True, blank=True)
    rg = models.CharField(max_length=20, null=True, blank=True)
    data_nasc = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=10, null=True, blank=True)
    pcd = models.CharField(max_length=50, null=True, blank=True)
    preferred_name = models.CharField(max_length=255, null=True, blank=True)
    has_preferred_name = models.BooleanField(null=True, blank=True)
    cel = models.CharField(max_length=15, null=True, blank=True)
    cel_responsavel = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    mother_name = models.CharField(max_length=255, null=True, blank=True)
    estado_civil = models.CharField(max_length=50, null=True, blank=True)
    raca = models.CharField(max_length=10, null=True, blank=True)
    renda_familiar = models.CharField(max_length=50, null=True, blank=True)
    cadastro_completo = models.BooleanField(null=True, blank=True)
    registration_status = models.CharField(
        max_length=20,
        choices=REGISTRATION_STATUS_CHOICES,
        default='espera'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class Address(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='address', null=True, blank=True)
    cep = models.CharField(max_length=10, null=True, blank=True)
    rua = models.CharField(max_length=255, null=True, blank=True)
    bairro = models.CharField(max_length=255, null=True, blank=True)
    numero = models.CharField(max_length=10, null=True, blank=True)
    complemento = models.CharField(max_length=255, null=True, blank=True)
    city_id = models.UUIDField(null=True, blank=True)
    city_name = models.CharField(max_length=255, null=True, blank=True)


class AcademicData(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='academic_data', null=True, blank=True)
    apply_method = models.CharField(max_length=50, null=True, blank=True)
    apply_method_grade = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    test_id = models.UUIDField(null=True, blank=True)
    school_year = models.CharField(max_length=10, null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    absent = models.BooleanField(null=True, blank=True)
    enrolled = models.BooleanField(null=True, blank=True)
    disqualified = models.BooleanField(null=True, blank=True)
    practice_test_id = models.UUIDField(null=True, blank=True)
    school_award = models.CharField(max_length=255, null=True, blank=True)

    # Provas e PDFs extras
    nota_matematica = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    nota_redacao = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    nota_geral = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    media_ensino_medio = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    pdf_url = models.CharField(max_length=255, blank=True, null=True)
    contract_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Garante apenas manipular datas de valores diretos ruins 
        if not isinstance(self.created_at, (datetime.datetime, type(None))):
            self.created_at = None
        if not isinstance(self.updated_at, (datetime.datetime, type(None))):
            self.updated_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Provas e Mérito de {self.user_profile.nome_completo if self.user_profile else "Desconhecido"}'
