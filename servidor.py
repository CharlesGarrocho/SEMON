# coding: utf-8
# @author: Charles Tim Batista Garrocho
# @contact: ctgarrocho@gmail.com
# @copyright: (C) 2012-2012 Python Software Open Source

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from detector import DetectorMovimentos
import cv2.cv as cv
from os import remove
import settings

DETECTOR = DetectorMovimentos()

def statusMonitoramento(conexao):
    """
    Envia ao cliente o estado atual do monitoramento.
    """
    conexao.send(settings.OK_200)
    if DETECTOR.EXECUTANDO:
        conexao.send(settings.EXECUTANDO)
    else:
        conexao.send(settings.PAUSADO)

def iniciar(conexao = None):
    """
    Inicia o monitoramento. Vai processando as imagens e verificando
    se ocorre diferenças nas imagens, caso ocorra, um e-mail é enviado
    ao administrador da sala de servidores.
    """
    
    if conexao != None:
        conexao.send(settings.OK_200)
    DETECTOR.EXECUTANDO = True
    
    while DETECTOR.EXECUTANDO:
        imagem = DETECTOR.obterImagemCam()
        DETECTOR.processaImagem(imagem)
        
        if DETECTOR.verificaMovimento():
            print 'tem movimento'

            # Exibe a imagem na janela webCam e salva a imagem no diretorio corrente com nome da data e horario atual.
            #DETECTOR.ShowImage('webCam', self.imagem_atual)
            # cv.SaveImage(self.obterHoraAtual(), imagem)
            
def obterImagemAtual(conexao):
    """
    Envia uma imagem atual do monitoramento para o cliente.
    """
    endereco = DETECTOR.obterHoraAtual()
    cv.SaveImage(endereco, DETECTOR.imagem_atual)
        
    imagem = open(endereco)
    conexao.send(settings.OK_200)
    
    while True:
        dados = imagem.read(512)
        if not dados:
            break
        conexao.send(dados)
    
    imagem.close()
    remove(endereco)
    
def trataCliente(conexao, endereco):
    """
    Trata as novas requisições dos clientes.
    """
    requisicao = conexao.recv(1)

    # Requisição de verificar estado do monitoramento.
    if requisicao == settings.STATUS:
        statusMonitoramento(conexao)

    # Requisição de iniciar monitoramento.
    elif requisicao == settings.INICIAR:
        iniciar(conexao)

    # Requisição de pausar monitoramento.
    elif requisicao == settings.PAUSAR:
        conexao.send(settings.OK_200)
        DETECTOR.EXECUTANDO = False

    # Requisição de obter uma imagem atual do monitoramento.
    elif requisicao == settings.IMAGEM:
        obterImagemAtual(conexao)

    # Requisição não autorizada.
    else:
        conexao.send(settings.NAO_AUTORIZADO_401)

    # Após a requisição ser realizada, a conexão é fechada. 
    conexao.close()

def servidor():
    """
    Abre um novo soquete servidor para tratar as novas conexões do cliente.
    """
    soquete = socket(AF_INET, SOCK_STREAM)
    soquete.bind((settings.HOST, settings.PORTA))
    soquete.listen(1)

    # Fica aqui aguardando novas conexões.
    while True:
        # Para cada nova conexão é criado um novo processo para tratar as requisições.
        Thread(target=trataCliente, args=(soquete.accept())).start()

if __name__== '__main__':
    Thread(target=servidor).start() 
