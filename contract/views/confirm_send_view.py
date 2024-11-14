import requests
from django.shortcuts import redirect, render
from decouple import config
from contract.views.messages_view import render_message
from api.models import AcademicData, UserProfile
from django.core.exceptions import ValidationError
import logging
from decimal import Decimal, InvalidOperation

# Configuração de logs
logger = logging.getLogger('django')

# Carregar URL base da API e chave de API do arquivo .env
API_BASE_URL = config('API_BASE_URL')
API_KEY = config('API_KEY')

# Função auxiliar para converter strings decimais com vírgula em valores decimais válidos
def convert_to_decimal(value):
    try:
        if isinstance(value, str):
            return Decimal(value.replace(',', '.'))
        return Decimal(value)
    except InvalidOperation as e:
        logger.error(f"Erro na conversão de valor decimal: {value} - {e}")
        raise ValidationError(f"'{value}' não é um número decimal válido.")

# View para enviar os dados para a API usando PATCH
def confirm_send_view(request):
    if request.method == 'POST':
        try:
            # Obter os dados da sessão
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

            # Verificar se todos os dados estão presentes
            if not all([nome, cpf, nota_matematica, nota_redacao, nota_geral, apply_method, id_value]):
                logger.error("Dados ausentes na sessão.")
                return render_message(request, 'error', title='Erro', message='Dados incompletos.')

            # Verificar duplicidade de CPF no UserProfile associado
            user_profile = UserProfile.objects.filter(cpf=cpf).first()
            if not user_profile:
                return render_message(request, 'error', title='Erro', message='Usuário não encontrado.')

            if AcademicData.objects.filter(user_profile=user_profile).exists():
                return render_message(request, 'error', title='CPF Duplicado', message='Dados já cadastrados no sistema.')

            # Converter notas para valores decimais
            nota_matematica_decimal = convert_to_decimal(nota_matematica)
            nota_redacao_decimal = convert_to_decimal(nota_redacao)
            nota_geral_decimal = convert_to_decimal(nota_geral)

            # Salvar os dados na model AcademicData
            academic_data = AcademicData.objects.create(
                user_profile=user_profile,
                apply_method=apply_method,
                nota_matematica=nota_matematica_decimal,
                nota_redacao=nota_redacao_decimal,
                nota_geral=nota_geral_decimal
            )

            # URL do endpoint dinâmico usando a variável API_BASE_URL
            url_method = f'{API_BASE_URL}/form/{id_value}/applyMethod'
            headers = {'api-key': API_KEY}
            body = {
                "applyMethod": apply_method,
                "applyMethodGrade": float(nota_geral_decimal),  # Converte Decimal para float
            }

            # Enviar os dados para a API com o método PATCH
            response_method = requests.patch(url_method, headers=headers, json=body)
            response_method.raise_for_status()

            # Limpar a sessão em caso de sucesso
            request.session.flush()

            # Redirecionar para a mensagem de sucesso
            return render_message(request, 'success', title='Sucesso', message='Dados enviados com sucesso.')

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar os dados: {e}")
            # Redirecionar para a mensagem de erro
            return render_message(request, 'error', title='Erro', message='Erro ao enviar dados para a API.')

        except ValidationError as e:
            logger.error(f"Erro de validação: {e}")
            return render_message(request, 'error', title='Erro', message='Erro ao validar os dados informados.')

    # Se o método da requisição não for POST, redirecionar para a página de resultados
    return redirect('enem_result_view')
