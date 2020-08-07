"""
    Trabalho Final de Processamento Digital de Imagens
                                   Wender Castro, 2020

    Detalhamento:
      https://docs.google.com/document/d/1QL1Tn7RHkRW6BZIUdIyoiMCRr7J0rYUOIr6rtftIBYE/edit

    Menu Arquivo
    - Abrir
    - Salvar como… (opção de escolher o nome do arquivo)
    - Fechar
    Menu Transformações
    - Negativo
    - Correção gamma... (valor)
    - Transformação logarítmica
    - Filtro Sharpen
    - Filtro mediana (Box blur)
    - Filtro Gaussiano (3x3, 5x5, 7x7)
    - Detecção de bordas com Filtro de Sobel... (valor threshold)
    - Detecção de bordas com filtros da lista 4 exercício 01 (ou lista 7 exercícios 2B) (dê nomes para cada um dos três filtros)
    - Colorida para escala de cinza
    - Colorida para preto e branco... (valor threshold)
    - Separação de camadas R, G e B. (uma de cada vez, uma opção para cada)
    - Erosão (conferir se imagem é binária)
    - Dilatação (conferir se imagem é binária)
    - Abertura (conferir se imagem é binária)
    - Fechamento (conferir se imagem é binária)
      - Obs.: Para erosão, dilatação, abertura e fechamento, você pode definir um elemento estruturante padrão, ou dar algumas opções prontas para o usuário escolher, ou deixar o usuário criar um elemento estruturante no próprio aplicativo (se você fizer isso, terá meu respeito eternamente)).
    - Detecção de bordas em imagens binárias (lista 10)
    Menu Sobre:
    - Sobre o aplicativo…
      - Exibir uma caixa de diálogo com as seguintes informações:
      - Seu nome completo.
      - Nome da sua cidade.
      - Data que você terminou o aplicativo.
      - Se possível o link para o vídeo da sua apresentação.
    - Sobre a imagem…
      - Exibir uma caixa de diálogo com as seguintes informações sobre a imagem:
      - Nome do arquivo
      - Tipo do arquivo
      - Comentário
      - Largura
      - Altura
"""

import sys
import time
import subprocess

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication, QGridLayout, QWidget, QMessageBox, QProgressBar
from PyQt5.QtCore import QSize

from imagens import Imagem
from processamentos import Processamento, Processamentos


SOBRE_NOME_AUTOR = "Wender Silva de Castro"
SOBRE_CIDADE = "Ituiutaba - MG"
SOBRE_DATA = "02/08/2020"
SOBRE_LINK_VIDEO = "[url]"


class MyWindow(QMainWindow):
    # Constantes
    LARGURA = 640
    ALTURA = 480
    CAMINHO_TEMP = '.temp'

    def __init__(self):
        super(MyWindow, self).__init__()

        # Definir propriedades
        self.layout = None
        self.barra_progresso = None
        self.barra_status = None
        self.imagem_1 = None
        self.imagem_2 = None
        self.texto_progresso = None

        self.menu_salvar_arquivo = None
        self.menu_sobre_imagem = None
        self.menu_resetar_imagem = None
        self.menus_processamentos = []

        self.processamentos = Processamentos()
        self.imagem_original = None
        self.imagem_alterada = None

        # Montar interface
        self.setup_main_window()
        self.init_ui()
        self.atualizar_menus()

    def setup_main_window(self):
        # Definir formato
        self.setMinimumSize(QSize(MyWindow.LARGURA, MyWindow.ALTURA))
        self.setWindowTitle("Processamento Digital de Imagens - IFTM")

        # Definir layout
        widget = QWidget(self)
        self.setCentralWidget(widget)
        self.layout = QGridLayout()
        widget.setLayout(self.layout)

    def init_ui(self):
        # Criar a barra de menu
        barra_menu = self.menuBar()

        # Criar o menu arquivo
        menu_arquivo = barra_menu.addMenu("&Arquivo")

        opcao_abrir = menu_arquivo.addAction("A&brir")
        opcao_abrir.triggered.connect(self.open_file)
        opcao_abrir.setShortcut("Ctrl+A")

        self.menu_salvar_arquivo = menu_arquivo.addAction("S&alvar como")
        self.menu_salvar_arquivo.triggered.connect(self.save_file)
        self.menu_salvar_arquivo.setShortcut("Ctrl+S")

        menu_arquivo.addSeparator()

        opcao_fechar = menu_arquivo.addAction("F&echar")
        opcao_fechar.triggered.connect(self.close)
        opcao_fechar.setShortcut("Ctrl+X")

        # Criar o menu transformacoes
        menu_transformacoes = barra_menu.addMenu("&Transformações")
        self.menu_resetar_imagem = menu_transformacoes.addAction("Resetar Imagem")
        self.menu_resetar_imagem.triggered.connect(self.resetar_imagem)

        menu_transformacoes.addSeparator()

        for processamento in self.processamentos.get_todos():
            if processamento.get_default_params() is not None:
                menu = menu_transformacoes.addMenu(processamento.get_nome())

                # Definir sub menus
                for (param_name, param_value) in processamento.get_default_params():
                    submenu = menu.addAction(param_name)

                    # Definir a acao em outro escopo para manter o valor da variavel processamento
                    submenu.triggered.connect(self._get_processamento_acao(processamento, param_value))
            else:
                menu = menu_transformacoes.addAction(processamento.get_nome())

                # Definir a acao em outro escopo para manter o valor da variavel processamento
                menu.triggered.connect(self._get_processamento_acao(processamento))

            # Adicionar tooltip, se presente
            if len(processamento.get_descricao()) > 0:
                menu.setToolTip(processamento.get_descricao())

            # Guardar na lista de acoes de processamentos
            menu.setEnabled(False)
            self.menus_processamentos.append((processamento, menu))

        # Criar o menu sobre
        menu_sobre = barra_menu.addMenu("&Sobre")
        opcao_sobre = menu_sobre.addAction("Sobre o Aplicativo")
        opcao_sobre.triggered.connect(self.exibir_sobre_aplicativo)

        self.menu_sobre_imagem = menu_sobre.addAction("Sobre a Imagem")
        self.menu_sobre_imagem.triggered.connect(self.exibir_sobre_imagem)

        # Criar barra de status
        self.barra_status = self.statusBar()
        self.barra_status.showMessage("Seja bem-vindo", 3000)

        # Criando a barra de progresso
        self.barra_progresso = QProgressBar(self)
        self.barra_progresso.setAlignment(QtCore.Qt.AlignCenter)
        self.barra_progresso.move(0, 100)

        # Criar os widgets (Label, Text, Image)

        # Criando um QLabel para texto
        texto = QLabel("Trabalho Final", self)
        texto.adjustSize()
        texto.setAlignment(QtCore.Qt.AlignCenter)

        # Criando um QLabel para informar que há uma barra de progresso
        self.texto_progresso = QLabel("Carregando...")

        # Criando uma imagem(QLabel)
        self.imagem_1 = QLabel(self)
        self.imagem_1.setAlignment(QtCore.Qt.AlignCenter)

        self.imagem_2 = QLabel(self)
        self.imagem_2.setAlignment(QtCore.Qt.AlignCenter)

        # Organizando os widgets dentro do GridLayout
        self.layout.addWidget(texto, 0, 0, 1, 4)
        self.layout.addWidget(self.imagem_1, 1, 0, 2, 2)
        self.layout.addWidget(self.imagem_2, 1, 2, 2, 2)
        self.layout.addWidget(self.texto_progresso, 2, 0)
        self.layout.addWidget(self.barra_progresso, 3, 0, 1, 4)

        # Definindo a largura das linhas
        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 0)
        self.layout.setRowStretch(3, 1)

    def exibir_sobre_aplicativo(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Sobre")
        msg.setText(SOBRE_NOME_AUTOR)
        msg.setInformativeText("Localização: %s\nData: %s\nLink Apresentação: %s" % (SOBRE_CIDADE, SOBRE_DATA, SOBRE_LINK_VIDEO))
        msg.exec_()  # exibir a caixa de mensagem/diálogo

    def exibir_sobre_imagem(self):
        imagem = self.imagem_original
        comentarios = ''
        if len(imagem.get_comentario()) > 0:
            comentarios = '\nComentario nos detalhes.'

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Sobre")
        msg.setText(imagem.get_caminho())
        msg.setInformativeText("Tipo: %s\nTamanho: %dx%d\nPrecisão: %d%s" % (imagem.get_tipo(), imagem.get_largura(), imagem.get_altura(), imagem.get_maxval(), comentarios))
        if len(comentarios) > 0:
            msg.setDetailedText(imagem.get_comentario())
        msg.exec_()  # exibir a caixa de mensagem/diálogo

    def exibir_erro(self, texto: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Abort)
        msg.setWindowTitle("Erro")
        msg.setText(texto)
        msg.exec_()  # exibir a caixa de mensagem/diálogo

    def open_file(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="Abrir Imagem",
                                                            directory=QtCore.QDir.currentPath(),
                                                            filter='Imagens(*.ppm; *.pgm; *.pbm)',
                                                            initialFilter='Imagens(*.ppm; *.pgm; *.pbm)')
        if file_name != '':
            print('Abrindo imagem...')
            self.texto_progresso.setText('Abrindo imagem...')

            self.barra_progresso.setValue(0)
            self.imagem_original = Imagem()
            sucesso = self.imagem_original.carregar(file_name)

            if not sucesso:
                self.exibir_erro(self.imagem_alterada.get_erro())
                self.barra_progresso.setValue(100)
                self.barra_status.showMessage("Não foi possível abrir a imagem.", 5000)
                print('Abrir imagem -> FALHA')
                return

            print('Abrir imagem -> 50%')

            self.barra_progresso.setValue(50)
            self.imagem_alterada = self.imagem_original.clonar()
            print('Abrir imagem -> 80%')

            self.barra_progresso.setValue(80)
            pixmap = QtGui.QPixmap(file_name)
            pixmap = pixmap.scaled(250, 250, QtCore.Qt.KeepAspectRatio)
            self.imagem_1.setPixmap(pixmap)
            self.imagem_2.setPixmap(pixmap)
            print('Abrir imagem -> 100%')

            self.barra_progresso.setValue(100)
            self.barra_status.showMessage("Imagem aberta com sucesso.", 5000)
            print('Abrir imagem -> COMPLETO')

        self.atualizar_menus()

    def save_file(self):
        imagem = self.imagem_alterada
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption="Salvar Imagem",
                                              directory=QtCore.QDir.currentPath(),
                                              filter='%s (%s)' % (imagem.get_tipo(), imagem.get_extensao()))
        if file_name != '':
            print('Salvando imagem...')
            self.texto_progresso.setText('Salvando imagem...')

            self.barra_progresso.setValue(0)
            sucesso = self.imagem_alterada.salvar(file_name)

            if not sucesso:
                self.exibir_erro(self.imagem_alterada.get_erro())
                self.barra_progresso.setValue(100)
                self.barra_status.showMessage("Não foi possível salvar a imagem.", 5000)
                print('Salvar imagem -> FALHA')
                return

            print('Salvar imagem -> 100%')

            self.barra_progresso.setValue(100)
            self.barra_status.showMessage("Imagem salva com sucesso.", 5000)
            print('Salvar imagem -> COMPLETO')


    def resetar_imagem(self):
        print('Resetando imagem...')
        self.texto_progresso.setText('Resetando imagem...')

        self.barra_progresso.setValue(0)
        self.imagem_alterada = self.imagem_original.clonar()
        print('Resetar imagem -> 80%')

        self.barra_progresso.setValue(80)
        pixmap = QtGui.QPixmap(self.imagem_alterada.get_caminho())
        pixmap = pixmap.scaled(250, 250, QtCore.Qt.KeepAspectRatio)
        self.imagem_2.setPixmap(pixmap)
        print('Resetar imagem -> 100%')

        self.barra_progresso.setValue(100)
        self.barra_status.showMessage("Imagem resetada.", 5000)
        self.atualizar_menus()
        print('Resetar imagem -> COMPLETO')

    def transform_me(self, processamento: Processamento, param_value: any):
        print('Processando:', processamento.get_nome(), '(', param_value, ')...')
        self.texto_progresso.setText('Processando imagem...')

        self.barra_progresso.setValue(0)
        self.imagem_alterada = processamento.processar(self.imagem_alterada, param_value)
        print('Processamento -> 40%')

        self.barra_progresso.setValue(40)
        self.imagem_alterada.salvar(MyWindow.CAMINHO_TEMP)
        time.sleep(.1)
        print('Processamento -> 80%')

        self.barra_progresso.setValue(80)
        pixmap = QtGui.QPixmap(self.imagem_alterada.get_caminho())
        pixmap = pixmap.scaled(250, 250, QtCore.Qt.KeepAspectRatio)
        self.imagem_2.setPixmap(pixmap)
        print('Processamento -> 100%')

        self.barra_progresso.setValue(100)
        self.barra_status.showMessage(processamento.get_nome() + " finalizado.", 5000)
        self.atualizar_menus()
        print('Processamento -> COMPLETO')

    def atualizar_menus(self):
        if self.imagem_alterada is None:
            tem_imagem = False
            imagem_binaria = False
            imagem_nao_binaria = False
        else:
            tem_imagem = True
            imagem_binaria = self.imagem_alterada.get_binario()
            imagem_nao_binaria = not imagem_binaria

        self.menu_salvar_arquivo.setEnabled(tem_imagem)
        self.menu_sobre_imagem.setEnabled(tem_imagem)
        self.menu_resetar_imagem.setEnabled(tem_imagem)

        for (processamento, menu) in self.menus_processamentos:
            ativo = (imagem_binaria and processamento.get_permitir_binarias()) or (imagem_nao_binaria and processamento.get_permitir_nao_binarias())
            menu.setEnabled(ativo)

    def _get_processamento_acao(self, processamento: Processamento, param_value: any = None):
        return lambda: self.transform_me(processamento, param_value)


def main():
    app = QApplication(sys.argv)
    app_icon = QtGui.QIcon("icon.jpg")
    app.setWindowIcon(app_icon)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
