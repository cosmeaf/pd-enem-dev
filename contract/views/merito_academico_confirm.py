from datetime import datetime
import os
import subprocess
import requests
from django.shortcuts import render, redirect
from contract.utility.docx_utility import manipular_docx
from decouple import config
from contract.views.messages_view import render_message
from api.models import AcademicData, UserProfile

API_BASE_URL = config('API_BASE_URL')
API_KEY = config('API_KEY')

def merito_academico_confirm(request):
    if request.method == 'POST':
        confirmacao = request.POST.get('confirmacao')

        if confirmacao == 'sim':
            # Coletar os dados da sessão
            nome_aluno = request.session.get('nome_aluno')
            nome_diretor = request.session.get('nome_diretor')
            nome_escola = request.session.get('nome_escola')
            endereco_escola = request.session.get('endereco_escola')
            data = request.session.get('data')
            media_ensino_medio = request.session.get('media_ensino_medio')
            cpf = request.session.get('cpf')

            # Verificar duplicidade de CPF no UserProfile
            user_profile = UserProfile.objects.filter(cpf=cpf).first()
            if not user_profile:
                user_profile = UserProfile.objects.create(
                    nome_completo=nome_aluno,
                    cpf=cpf,
                    cel=request.session.get('cel'),
                    cel_responsavel=request.session.get('cel_responsavel'),
                    email=request.session.get('email')
                )

            # Manipular o DOCX e gerar o arquivo PDF
            try:
                pdf_path = manipular_docx(nome_aluno, nome_diretor, nome_escola, endereco_escola, data, media_ensino_medio)
                pdf_url = f'/media/documents/{os.path.basename(pdf_path)}'
            except FileNotFoundError as e:
                return render_message(request, 'error', title='Arquivo Não Encontrado', message=str(e))
            except subprocess.CalledProcessError:
                return render_message(request, 'error', title='Erro na Conversão', message='Erro ao converter o documento para PDF.')

            # Verificar se já existe AcademicData para este UserProfile
            academic_data, created = AcademicData.objects.update_or_create(
                user_profile=user_profile,
                defaults={
                    'apply_method': "MeritoAcademico",
                    'apply_method_grade': media_ensino_medio,
                    'media_ensino_medio': media_ensino_medio,
                    'pdf_url': pdf_url,
                    'nota_matematica': None,
                    'nota_redacao': None,
                    'nota_geral': None,
                    'contract_date': data
                }
            )

            # Obter o user_id salvo na sessão
            user_id = request.session.get('user_id')

            # Enviar os dados via API
            url_method = f'{API_BASE_URL}/form/{user_id}/applyMethod'
            headers = {'api-key': API_KEY}
            body = {
                "applyMethod": "MeritoAcademico",
                "applyMethodGrade": media_ensino_medio,
            }

            try:
                response_method = requests.patch(url_method, headers=headers, json=body)
                response_method.raise_for_status()
                return render(request, 'merito_academico_view_doc.html', {
                    'pdf_url': pdf_url,
                    'nome_aluno': nome_aluno
                })
            except requests.exceptions.RequestException as e:
                return render_message(request, 'error', title='Erro na API', message=f"Erro ao enviar dados: {str(e)}")

        else:
            return redirect('merito_academico_input')

    # Carregar os dados da sessão para exibir na tela
    context = {
        'nome_aluno': request.session.get('nome_aluno'),
        'nome_diretor': request.session.get('nome_diretor'),
        'nome_escola': request.session.get('nome_escola'),
        'endereco_escola': request.session.get('endereco_escola'),
        'data': request.session.get('data'),
        'media_ensino_medio': request.session.get('media_ensino_medio'),
    }
    return render(request, 'merito_academico_confirm.html', context)
