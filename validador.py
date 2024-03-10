"""Módulo responsável por fazer as validações durante a navegação."""

import time

from dotenv import dotenv_values
from selenium.webdriver import Edge
from selenium.webdriver.common.by import By


class ErroArquivoEnv(Exception):
    """Erro lançado quando há uma variável de ambiente faltando."""


class ServidorComErro(Exception):
    """Erro lançado quando foi esgotado o máximo de tentativas (Erro 500)"""


class CadastroPixSandboxValidador:
    """Principal Validador do PIX em ambiente Sandbox."""

    def __init__(self):
        """Inicializa o validador com suas variáveis de ambiente."""
        self.arquivo_env = dotenv_values('.env')
        self.braspag_login = ''
        self.braspag_senha = ''

    def validar_url_main(self):
        """Retorna a URL da Braspag."""
        url_main = self.arquivo_env.get('URL_MAIN_ADMIN')
        if not url_main:
            raise ErroArquivoEnv('URL_MAIN_ADMIN obrigatória.')
        return url_main

    def validar_credenciais_login(self):
        """Define o Usuário e Senha da Braspag."""
        usuario = self.arquivo_env.get('BRASPAG_LOGIN')
        senha = self.arquivo_env.get('BRASPAG_PASS')
        if not usuario or not senha:
            raise ErroArquivoEnv('Credenciais são obrigatórias!')
        self.braspag_login = usuario
        self.braspag_senha = senha

    def erro_500_existe(self, driver: Edge):
        """Retorna se o servidor da Braspag respondeu com HTTP 500."""
        if driver.title.lower() in {'internal server error', '500', 'erro'}:
            return True
        return False

    def acao_erro_500(self, driver: Edge):
        """Atualiza a página para prosseguir."""
        time.sleep(5)
        driver.refresh()
        time.sleep(5)

    def mid_nao_encontrado(self, driver: Edge):
        """Retorna se não foi localizado o MID na Braspag."""
        resultado = driver.find_element(By.XPATH, '//div[@class="adm-title"]')
        if '0' in resultado.text:
            return True
        return False
