"""Módulo que executa o script de automação."""

import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from extracao_mids import extracao_lista_mids
from validador import CadastroPixSandboxValidador, ServidorComErro


class ErroArquivoEnv(Exception):
    """Erro lançado quando há uma variável de ambiente faltando."""


class CadastroPixSandboxAutomador:
    """Representa o Automador via Selenium."""

    def __init__(self):
        """Inicializa o webdriver junto com o validador."""
        self.driver = webdriver.Edge()
        self.validador = CadastroPixSandboxValidador()

    def fazer_login(self):
        """Realiza a autenticação."""
        braspag_url = self.validador.validar_url_main()
        self.driver.get(braspag_url)
        assert 'Login | BraspagAuth' in self.driver.title
        time.sleep(3)
        usuario = self.driver.find_element(By.XPATH, '//input[@name="Param1"]')
        senha = self.driver.find_element(By.XPATH, '//input[@name="Param2"]')
        usuario.clear()
        senha.clear()
        self.validador.validar_credenciais_login()
        usuario.send_keys(self.validador.braspag_login)
        senha.send_keys(self.validador.braspag_senha)
        botao_entrar = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
        botao_entrar.click()
        time.sleep(3)

    def rotina_erro_500(self, finalizado: bool = False, tentativas: int = 0):
        """Rotina a ser executada se der algum erro 500 durante a navegação."""
        while not finalizado:
            if self.validador.erro_500_existe(self.driver):
                if tentativas >= 5:
                    raise ServidorComErro('O servidor não está respondendo ..')
                self.validador.acao_erro_500(self.driver)
                tentativas += 1
            finalizado = True

    def acessar_mid(self, mid: str):
        """Acessa o MID e retorna se foi encontrado na busca."""
        resultado = ''
        botao_cielo = self.driver.find_element(By.XPATH, '//a[@id="cielo"]')
        botao_cielo.click()
        time.sleep(0.3)
        link_pesquisar_estabelecimentos = self.driver.find_element(
            By.XPATH, '//a[@href="/EcommerceCielo/List"]'
        )
        link_pesquisar_estabelecimentos.click()
        time.sleep(3)
        self.rotina_erro_500()
        campo_mid = self.driver.find_element(By.XPATH, '//input[@name="MerchantId"]')
        campo_mid.clear()
        campo_mid.send_keys(mid)
        campo_data_inicial = self.driver.find_element(By.XPATH, '//input[@name="StartDate"]')
        campo_data_inicial.clear()
        botao_buscar = self.driver.find_element(
            By.XPATH,
            '//button[@id="buttonSearch"][@type="submit"]'
        )
        botao_buscar.click()
        time.sleep(3)
        self.rotina_erro_500()
        if self.validador.mid_nao_encontrado(self.driver):
            resultado = 'MID nao encontrado'
            return resultado
        botao_abrir_mid = self.driver.find_element(By.XPATH, '//a[@title="Ver Detalhes"]')
        botao_abrir_mid.click()
        time.sleep(3)
        self.rotina_erro_500()
        return resultado

    def cadastrar_pix(self):
        """Depois de acessar o MID, cadastra o PIX e retorna o status da solicitação."""
        resultado = ''
        botao_habilitar = self.driver.find_element(By.XPATH, '//a[@id="buttonEditCieloPix"]')
        if not botao_habilitar.text.lower() in {'habilitar', ' habilitar'}:
            resultado = 'PIX ja habilitado'
            return resultado
        botao_habilitar.click()
        time.sleep(3)
        self.rotina_erro_500()
        senha = self.driver.find_element(By.XPATH, '//input[@name="Password"]')
        senha.clear()
        senha.send_keys(self.validador.braspag_senha)
        time.sleep(0.3)
        botao_confirmar = self.driver.find_element(By.XPATH, '//a[@id="btnConfirm"]')
        botao_confirmar.click()
        time.sleep(3)
        confirmacao = self.driver.find_element(By.XPATH, '//div[@id="messageContent"]')
        if confirmacao.text.lower() in {'operação realizada com sucesso.', ' operação realizada com sucesso.'}:
            resultado = 'PIX habilitado com sucesso'
            return resultado
        resultado = 'Ocorreu um erro ao habilitar'
        return resultado

    def fazer_logout(self):
        """Depois de cadastrar o PIX, faz logout e finaliza."""
        braspag_url = self.validador.validar_url_main()
        self.driver.get(braspag_url)
        botao_usuario = self.driver.find_element(By.XPATH, '//a[@id="userName"]')
        botao_usuario.click()
        time.sleep(0.5)
        botao_logout = self.driver.find_element(By.XPATH, '//a[@id="logout"]')
        botao_logout.click()
        time.sleep(1)


def main():
    """Executa a rotina principal."""
    print('--------------------------------------------')
    print('\n.. Iniciando Automador - PIX Sandbox ..')
    print('\n--------------------------------------------')
    lista_mids = extracao_lista_mids()
    if not lista_mids:
        raise ErroArquivoEnv('Lista de MIDs esta vazia')
    resultados: dict[str, str] = {}
    for mid in lista_mids:
        automador = CadastroPixSandboxAutomador()
        automador.fazer_login()
        resultado_acesso = automador.acessar_mid(mid)
        if resultado_acesso == 'MID nao encontrado':
            resultados[mid] = 'MID nao encontrado'
            continue
        resultado_cadastro = automador.cadastrar_pix()
        resultados[mid] = resultado_cadastro
        automador.fazer_logout()
    retorno_json = json.dumps(resultados, indent=4)
    with open('resultado.json', 'w', encoding='utf-8') as arq:
        arq.write(retorno_json)
    print('--------------------------------------------')
    print('\n.. Fim da execução ..')
    print('\n--------------------------------------------')


if __name__ == '__main__':
    main()
