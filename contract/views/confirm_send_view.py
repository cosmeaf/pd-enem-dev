from django.shortcuts import redirect, render
from decouple import config
from contract.views.messages_view import render_message
from api.models import AcademicData, UserProfile
from django.core.exceptions import ValidationError
import requests
import logging
from decimal import Decimal, InvalidOperation

# Configuração de logs
logger = logging.getLogger('django')

API_BASE_URL = config('API_BASE_URL')
API_KEY = config('API_KEY')

def convert_to_decimal(value):
    try:
        if isinstance(value, str):
            return Decimal(value.replace(',', '.'))
        return Decimal(value)
    except InvalidOperation as e:
        logger.error(f"Erro na conversão de valor decimal: {value} - {e}")
        raise ValidationError(f"'{value}' não é um número decimal válido.")

def confirm_send_view(request):
    if request.method == 'POST':
        try:
            nome = request.session.get('nome')
            cpf = request.session.get('cpf_extraido')
            cel = request.session.get('cel')
            cel_responsavel = request.session.get('cel_responsavel')
            email = request.session.get('email')
            nota_matematica = request.session.get('nota_matematica')
            nota_redacao = request.session.get('nota_redacao')
            nota_geral = request.session.get('nota_geral')
            apply_method = request.session.get('apply_method')
            id_value = request.session.get('user_id')

            if not all([nome, cpf, nota_matematica, nota_redacao, nota_geral, apply_method, id_value]):
                logger.error("Dados ausentes na sessão.")
                return render_message(request, 'error', title='Erro', message='Dados incompletos.')

            # Verificar ou criar UserProfile
            user_profile, created = UserProfile.objects.get_or_create(
                cpf=cpf,
                defaults={
                    'nome_completo': nome,
                    'cel': cel,
                    'cel_responsavel': cel_responsavel,
                    'email': email
                }
            )

            if not created and AcademicData.objects.filter(user_profile=user_profile).exists():
                return render_message(request, 'error', title='CPF Duplicado', message='Dados já cadastrados no sistema.')

            nota_matematica_decimal = convert_to_decimal(nota_matematica)
            nota_redacao_decimal = convert_to_decimal(nota_redacao)
            nota_geral_decimal = convert_to_decimal(nota_geral)

            academic_data = AcademicData.objects.create(
                user_profile=user_profile,
                apply_method=apply_method,
                nota_matematica=nota_matematica_decimal,
                nota_redacao=nota_redacao_decimal,
                nota_geral=nota_geral_decimal
            )

            url_method = f'{API_BASE_URL}/form/{id_value}/applyMethod'
            headers = {'api-key': API_KEY}
            body = {
                "applyMethod": apply_method,
                "applyMethodGrade": float(nota_geral_decimal),
            }

            response_method = requests.patch(url_method, headers=headers, json=body)
            response_method.raise_for_status()

            request.session.flush()
            return render_message(request, 'success', title='Sucesso', message='Dados enviados com sucesso.')

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar os dados: {e}")
            return render_message(request, 'error', title='Erro', message='Erro ao enviar dados para a API.')

        except ValidationError as e:
            logger.error(f"Erro de validação: {e}")
            return render_message(request, 'error', title='Erro', message='Erro ao validar os dados informados.')

    return redirect('enem_result_view')
