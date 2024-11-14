from django.core.management.base import BaseCommand
from django.db import connections
import json
from uuid import UUID
from datetime import date, datetime

class Command(BaseCommand):
    help = 'Lista dados diretamente do PostgreSQL e salva em um arquivo JSON'

    def handle(self, *args, **kwargs):
        query = '''
            SELECT id, city_id, nome_completo, cpf, data_nasc, genero, pcd, cep, rua, bairro, numero, complemento, 
                   cel, operadora, email, profissao, estado_civil, religiao, escola_publica, raca, escolaridade, 
                   nome_faculdade, cota, tipo_pcd, exam_hour_id, exam_date_id, exam_id, cadastro_completo, 
                   created_at, updated_at, uso_de_dados, cel_responsavel, periodo_faculdade, renda_familiar, 
                   score, absent, test_id, practice_test_id, enrolled, disqualified, n_of_children, 
                   youngest_nasc_date, parent, school_award, email_pd, note_patrimony, documents_validated, 
                   school_year, has_preferred_name, preferred_name, previous_knowledge, city_name, mother_name, 
                   home_internet_access, rg, apply_method, apply_method_grade, indication
            FROM public.form;
        '''

        with connections['remote'].cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()

        # Função para serializar objetos não padrão
        def custom_serializer(obj):
            if isinstance(obj, UUID):
                return str(obj)
            elif isinstance(obj, (date, datetime)):
                return obj.isoformat()  # Converte para string no formato ISO 8601
            return obj

        # Converte resultados em um formato serializável
        data = [
            {col: custom_serializer(val) for col, val in zip(columns, row)}
            for row in results
        ]

        # Salva os dados em um arquivo JSON
        with open('form_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS('Dados salvos em form_data.json com sucesso!'))
