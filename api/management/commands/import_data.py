import os
import json
from django.core.management.base import BaseCommand
from api.models import UserProfile, Address, AcademicData

class Command(BaseCommand):
    help = 'Importa dados de um arquivo JSON e salva no banco de dados'

    def handle(self, *args, **kwargs):
        json_file_path = 'form_data.json'  # Substitua pelo caminho correto do arquivo JSON

        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f'Arquivo {json_file_path} não encontrado!'))
            return

        with open(json_file_path, 'r', encoding='utf-8') as file:
            data_list = json.load(file)

        for data in data_list:
            try:
                # Cria um novo UserProfile, ignorando duplicatas
                user_profile = UserProfile.objects.create(
                    id=data['id'],
                    nome_completo=data.get('nome_completo'),
                    cpf=data['cpf'],
                    rg=data.get('rg'),
                    data_nasc=data.get('data_nasc'),
                    genero=data.get('genero'),
                    pcd=data.get('pcd'),
                    preferred_name=data.get('preferred_name'),
                    has_preferred_name=data.get('has_preferred_name'),
                    cel=data.get('cel'),
                    cel_responsavel=data.get('cel_responsavel'),
                    email=data.get('email'),
                    mother_name=data.get('mother_name'),
                    estado_civil=data.get('estado_civil'),
                    raca=data.get('raca'),
                    renda_familiar=data.get('renda_familiar'),
                    cadastro_completo=data.get('cadastro_completo'),
                )

                # Cria o Address correspondente
                Address.objects.create(
                    user_profile=user_profile,
                    cep=data.get('cep'),
                    rua=data.get('rua'),
                    bairro=data.get('bairro'),
                    numero=data.get('numero'),
                    complemento=data.get('complemento'),
                    city_id=data.get('city_id'),
                    city_name=data.get('city_name'),
                )

                # Cria o AcademicData correspondente
                AcademicData.objects.create(
                    user_profile=user_profile,
                    apply_method=data.get('apply_method'),
                    apply_method_grade=data.get('apply_method_grade'),
                    test_id=data.get('test_id'),
                    school_year=data.get('school_year'),
                    score=data.get('score'),
                    absent=data.get('absent'),
                    enrolled=data.get('enrolled'),
                    disqualified=data.get('disqualified'),
                    practice_test_id=data.get('practice_test_id'),
                    school_award=data.get('school_award'),
                )

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Erro ao inserir registro com CPF {data["cpf"]}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Importação concluída!'))
