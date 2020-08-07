"""
    Trabalho Final de Processamento Digital de Imagens
                                   Wender Castro, 2020

    Contém os processamentos de imagem.
"""

import numpy as np
import math
import random
from imagens import Imagem, converter_ppm, converter_pgm, converter_pbm


def processar_unico(imagem: Imagem, indice: int, func, params=None):
    """
    :param func: function(pixel: int or int[], params?)
    """
    if not callable(func):
        raise Exception()

    p = imagem.get_pixels()[indice]
    if imagem.get_tipo() == 'P3':
        if params is not None:
            return [func(p[0], params), func(p[1], params), func(p[2], params)]
        else:
            return [func(p[0]), func(p[1]), func(p[2])]
    else:
        if params is not None:
            return func(p, params)
        else:
            return func(p)


def processar_independente(imagem: Imagem, func, params=None):
    """
    :param func: function(pixel: int or int[], params?)
    """
    if not callable(func):
        raise Exception()

    if imagem.get_tipo() == 'P3':
        if params is not None:
            return np.array([
                [func(p[0], params), func(p[1], params), func(p[2], params)] for p in imagem.get_pixels()
            ])
        else:
            return np.array([
                [func(p[0]), func(p[1]), func(p[2])] for p in imagem.get_pixels()
            ])
    else:
        if params is not None:
            return np.array([
                func(p, params) for p in imagem.get_pixels()
            ])
        else:
            return np.array([
                func(p) for p in imagem.get_pixels()
            ])


class Processamento:
    def get_nome(self) -> str:
        pass

    def get_descricao(self) -> str:
        pass

    def get_permitir_binarias(self) -> bool:
        pass

    def get_permitir_nao_binarias(self) -> bool:
        pass

    def get_default_params(self):
        return None

    def get_processamentos(self) -> 'Processamentos':
        if Processamentos.instance is None:
            Processamentos()
        return Processamentos.instance

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        pass

    def processar_clone(self, imagem: Imagem, params=None) -> Imagem:
        clone = imagem.clonar()
        self.processar(clone, params)
        return clone


class ProcessamentoNegativo(Processamento):
    def get_nome(self) -> str:
        return 'Negativo'

    def get_descricao(self) -> str:
        return 'Inverte a cor da imagem'

    def get_permitir_binarias(self) -> bool:
        return True

    def get_permitir_nao_binarias(self) -> bool:
        return True

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        maxval = imagem.get_maxval()
        imagem.set_pixels(processar_independente(imagem,
                                                 lambda p: maxval - p))
        return imagem


class ProcessamentoCorrecaoGama(Processamento):
    def get_nome(self) -> str:
        return 'Correcao Gama'

    def get_descricao(self) -> str:
        return 'Altera a gamma da imagem'

    def get_permitir_binarias(self) -> bool:
        return False

    def get_permitir_nao_binarias(self) -> bool:
        return True

    def get_default_params(self):
        return [
            ('0.10', 0.10),
            ('0.25', 0.25),
            ('0.33', 0.33),
            ('0.50', 0.50),
            ('0.66', 0.66),
            ('0.75', 0.75),
            ('0.90', 0.90),
            ('1.10', 1.10),
            ('1.25', 1.25),
            ('1.33', 1.33),
            ('1.50', 1.50),
            ('1.66', 1.66),
            ('1.75', 1.75),
            ('1.90', 1.90)
        ]

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        maxval = imagem.get_maxval()
        imagem.set_pixels(processar_independente(imagem,
                                                 lambda p: int(((p / maxval) ** params) * maxval)))
        return imagem


class ProcessamentoTransformacaoLogaritmica(Processamento):
    def get_nome(self) -> str:
        return 'Transformacao Logaritmica'

    def get_descricao(self) -> str:
        return 'Aplica a transformação logaritmica'

    def get_permitir_binarias(self) -> bool:
        return False

    def get_permitir_nao_binarias(self) -> bool:
        return True

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        maxval = imagem.get_maxval()
        imagem.set_pixels(processar_independente(imagem,
                                                 lambda p: int((math.log(1 + (p / maxval))) * maxval)))
        return imagem


class ProcessamentoFiltroBase(Processamento):
    def get_kernel(self, params=None):
        pass

    def get_permitir_binarias(self) -> bool:
        return False

    def get_permitir_nao_binarias(self) -> bool:
        return True

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        kernel = self.get_kernel(params)
        ks = int((len(kernel) - 1) / 2)

        largura = imagem.get_largura()
        altura = imagem.get_altura()
        novos_pixels = []

        if imagem.get_tipo() == 'P3':
            pixels = np.reshape(imagem.get_pixels(), (altura, largura, 3))
            for x in range(ks, altura - ks):
                for y in range(ks, largura - ks):
                    sum = [0, 0, 0]
                    for k in range(3):
                        for ki in range(len(kernel)):
                            for kj in range(len(kernel[1])):
                                sum[k] = sum[k] + (pixels[x - ks + ki][y - ks + kj][k] * kernel[ki][kj])
                        sum[k] = int(sum[k])
                    novos_pixels.append(np.array(sum))
        else:
            pixels = np.reshape(imagem.get_pixels(), (altura, largura))
            for x in range(ks, altura - ks):
                for y in range(ks, largura - ks):
                    sum = 0
                    for ki in range(len(kernel)):
                        for kj in range(len(kernel[1])):
                            sum = sum + (pixels[x - ks + ki][y - ks + kj] * kernel[ki][kj])
                    sum = int(sum)
                    novos_pixels.append(sum)

        imagem.set_pixels(np.array(novos_pixels))
        imagem.set_largura(largura - (2 * ks))
        imagem.set_altura(altura - (2 * ks))
        return imagem


class ProcessamentoFiltroSharpen(ProcessamentoFiltroBase):
    def get_nome(self) -> str:
        return 'Filtro Sharpen'

    def get_descricao(self) -> str:
        return ''

    def get_kernel(self, params=None):
        kernel = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]
        kernel = np.asarray(kernel)
        return kernel


class ProcessamentoFiltroMediana(ProcessamentoFiltroBase):
    def get_nome(self) -> str:
        return 'Filtro Mediana'

    def get_descricao(self) -> str:
        return ''

    def get_kernel(self, params=None):
        kernel = np.ones((3, 3))
        kernel = np.asarray(kernel)/9
        return kernel


class ProcessamentoFiltroGaussiana(ProcessamentoFiltroBase):
    def get_nome(self) -> str:
        return 'Filtro Gaussiana'

    def get_descricao(self) -> str:
        return ''

    def get_default_params(self):
        return [
            ('3x3', 3),
            ('5x5', 5),
            ('7x7', 7)
        ]

    def get_kernel(self, params=None):
        # 7x7
        if params == 7 or params == '7x7':
            kernel = [[0,  0,  1,   2,  1,  0, 0], [0,  3, 13, 22, 13,  3, 0], [1, 13, 59, 97, 59, 13, 1],
                      [2, 22, 97, 159, 97, 22, 2], [1, 13, 59, 97, 59, 13, 1], [0,  3, 13, 22, 13,  3, 0],
                      [0,  0,  1,   2,  1,  0, 0]]
            kernel = np.asarray(kernel)/1003
        # 5x5
        elif params == 5 or params == '5x5':
            kernel = [[1, 4, 7, 4, 1], [4, 16, 26, 16, 4], [7, 26, 41, 26, 7], [4, 16, 26, 16, 4], [1, 4, 7, 4, 1]]
            kernel = np.asarray(kernel)/273
        # 3x3
        else:
            kernel = [[1, 2, 1], [2, 4, 2], [1, 2, 1]]
            kernel = np.asarray(kernel)/16
        return kernel


class ProcessamentoFiltroSobel(Processamento):
    def get_nome(self) -> str:
        return 'Filtro Sobel'

    def get_descricao(self) -> str:
        return ''

    def get_permitir_binarias(self) -> bool:
        return False

    def get_permitir_nao_binarias(self) -> bool:
        return True

    def get_default_params(self):
        return [
            ('64', 64),
            ('128', 128),
            ('200', 200)
        ]

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        if params is None:
            params = 64

        kernelx = [[-1, 0, 1], [2, 0, -2], [1, 0, -1]]
        kernelx = np.asarray(kernelx)
        kernely = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]
        kernely = np.asarray(kernely)
        ks = int((len(kernelx)-1)/2)

        largura = imagem.get_largura()
        altura = imagem.get_altura()
        novos_pixels = []

        if imagem.get_tipo() == 'P3':
            pixels = np.reshape(imagem.get_pixels(), (altura, largura, 3))
            for x in range(ks, largura - ks):
                for y in range(ks, altura - ks):
                    sum = [0, 0, 0]
                    for k in range(3):
                        sumx = 0
                        sumy = 0
                        for ki in range(len(kernelx)):
                            for kj in range(len(kernelx[1])):
                                sumx = sumx + (pixels[x - ks + ki][y - ks + kj][k] * kernelx[ki][kj])
                                sumy = sumy + (pixels[x - ks + ki][y - ks + kj][k] * kernely[ki][kj])
                        sumxy = math.sqrt((sumx ** 2) + (sumy ** 2))
                        sum[k] = max(sumxy, params)
                        sum[k] = int(sum[k]) if sum[k] != params else 0
                    novos_pixels.append(sum)
        else:
            pixels = np.reshape(imagem.get_pixels(), (altura, largura))
            for x in range(ks, largura - ks):
                for y in range(ks, altura - ks):
                    sumx = 0
                    sumy = 0
                    for ki in range(len(kernelx)):
                        for kj in range(len(kernelx[1])):
                            sumx = sumx + (pixels[x - ks + ki][y - ks + kj] * kernelx[ki][kj])
                            sumy = sumy + (pixels[x - ks + ki][y - ks + kj] * kernely[ki][kj])
                    sumxy = math.sqrt((sumx ** 2) + (sumy ** 2))
                    sum = max(sumxy, params)
                    sum = int(sum) if sum != params else 0
                    novos_pixels.append(sum)

        imagem.set_pixels(np.array(novos_pixels))
        imagem.set_largura(largura - 2 * ks)
        imagem.set_altura(altura - 2 * ks)
        return imagem


class ProcessamentoFiltroDeteccaoBorda(ProcessamentoFiltroBase):
    def get_nome(self) -> str:
        return 'Filtro Edge Detection'

    def get_descricao(self) -> str:
        return ''

    def get_default_params(self):
        return [
            ('Filtro 1', 1),
            ('Filtro 2', 2),
            ('Filtro 3', 3)
        ]

    def get_kernel(self, params=None):
        if params == 3:
            kernel = [[1, 0, -1], [0, 0, 0], [-1, 0, 1]]
            kernel = np.asarray(kernel)
        elif params == 2:
            kernel = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
            kernel = np.asarray(kernel)
        else:
            kernel = [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]
            kernel = np.asarray(kernel)
        return kernel


class ProcessamentoEscalaCinza(Processamento):
    def get_nome(self) -> str:
        return 'Escala Cinza'

    def get_descricao(self) -> str:
        return ''

    def get_permitir_binarias(self) -> bool:
        return False

    def get_permitir_nao_binarias(self) -> bool:
        return True

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        if imagem.get_tipo() == 'P2':
            return imagem

        return converter_pgm(imagem)


class ProcessamentoPretoBranco(Processamento):
    def get_nome(self) -> str:
        return 'Preto e Branco'

    def get_descricao(self) -> str:
        return ''

    def get_permitir_binarias(self) -> bool:
        return False

    def get_permitir_nao_binarias(self) -> bool:
        return True

    def get_default_params(self):
        return [
            ('10%', int(255 * .10)),
            ('25%', int(255 * .25)),
            ('33%', int(255 * .33)),
            ('50%', int(255 * .50)),
            ('66%', int(255 * .66)),
            ('75%', int(255 * .75)),
            ('90%', int(255 * .90)),
        ]

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        if params is None:
            params = int(255 * .50)
        if imagem.get_tipo() == 'P3':
            imagem = self.get_processamentos().get_escala_cinza().processar(imagem)

        pixels = imagem.get_pixels()
        for i in range(len(pixels)):
            p = pixels[i]
            if p > params:
                pixels[i] = 1
            else:
                pixels[i] = 0

        return converter_pbm(imagem)


class ProcessamentoSepararCamada(Processamento):
    def get_nome(self) -> str:
        return 'Separar Camada'

    def get_descricao(self) -> str:
        return ''

    def get_permitir_binarias(self) -> bool:
        return False

    def get_permitir_nao_binarias(self) -> bool:
        return True

    def get_default_params(self):
        return [
            ('Vermelho', 'r'),
            ('Verde', 'g'),
            ('Azul', 'b')
        ]

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        if imagem.get_tipo() != 'P3':
            imagem = converter_ppm(imagem)

        # Azul
        if params == 'b':
            indice = 2
        # Verde
        elif params == 'g':
            indice = 1
        # Vermelho
        else:
            indice = 0

        pixels = imagem.get_pixels()
        for i in range(len(pixels)):
            p = pixels[i]
            novo_pixel = np.zeros(len(p))
            novo_pixel[indice] = p[indice]
            pixels[i] = novo_pixel
        return imagem


class ProcessamentoErosao(Processamento):
    def get_nome(self) -> str:
        return 'Erosão'

    def get_descricao(self) -> str:
        return ''

    def get_permitir_binarias(self) -> bool:
        return True

    def get_permitir_nao_binarias(self) -> bool:
        return False

    def get_default_params(self):
        return [
            ('3x3', 3),
            ('5x5', 5),
            ('7x7', 7),
            ('9x9', 9)
        ]

    def get_estruturante(self, params):
        if params == 9 or params == '9x9':
            estruturante = [[0, 0, 1, 0, 0, 0, 0, 1, 1], [0, 0, 1, 1, 1, 1, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 1, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0, 1, 0, 1],
                            [0, 0, 1, 0, 1, 1, 0, 0, 0], [1, 1, 1, 0, 0, 1, 1, 0, 1], [1, 0, 0, 1, 0, 1, 1, 0, 0]]
        elif params == 7 or params == '7x7':
            estruturante = [[0, 0, 1, 0, 0, 0, 0], [1, 1, 1, 1, 1, 0, 1], [0, 0, 1, 0, 0, 0, 0], [1, 1, 1, 1, 1, 0, 1],
                            [0, 0, 1, 0, 0, 0, 0], [1, 1, 1, 1, 1, 0, 1], [1, 0, 0, 1, 0, 1, 1]]
        elif params == 5 or params == '5x5':
            estruturante = [[1, 1, 0, 0, 1], [1, 0, 0, 1, 1], [1, 1, 0, 0, 0], [1, 1, 0, 0, 1], [1, 1, 1, 1, 1]]
        else:
            estruturante = [[1, 1, 0], [1, 1, 1], [0, 1, 1]]
        return np.asarray(estruturante)

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        estruturante = self.get_estruturante(params)
        pixel = int((len(estruturante) - 1) / 2)

        pixels = imagem.get_pixels()
        pixels = np.reshape(pixels, (imagem.get_altura(), imagem.get_largura()))
        novos_pixels = pixels.copy()
        for i in range(pixel, imagem.get_altura() - pixel):
            for j in range(pixel, imagem.get_largura() - pixel):
                for x in range(len(estruturante)):
                    for y in range(len(estruturante[1])):
                        if pixels[i][j] == 0 and estruturante[x][y] == 1:
                            novos_pixels[i - pixel + x][j - pixel + y] = 0

        novos_pixels = np.reshape(novos_pixels, len(imagem.get_pixels()))
        imagem.set_pixels(novos_pixels)
        return imagem


class ProcessamentoDilatacao(Processamento):
    def get_nome(self) -> str:
        return 'Dilatação'

    def get_descricao(self) -> str:
        return ''

    def get_permitir_binarias(self) -> bool:
        return True

    def get_permitir_nao_binarias(self) -> bool:
        return False

    def get_default_params(self):
        return [
            ('3x3', 3),
            ('5x5', 5),
            ('7x7', 7),
            ('9x9', 9)
        ]

    def get_elemento(self, params):
        if params == 9 or params == '9x9':
            elemento = [[0, 0, 1, 0, 0, 0, 0, 1, 1], [0, 0, 1, 1, 1, 1, 1, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 1],
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 1, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0, 1, 0, 1],
                        [0, 0, 1, 0, 1, 1, 0, 0, 0], [1, 1, 1, 0, 0, 1, 1, 0, 1], [1, 0, 0, 1, 0, 1, 1, 0, 0]]
        elif params == 7 or params == '7x7':
            elemento = [[0, 0, 1, 0, 0, 0, 0], [1, 1, 1, 1, 1, 0, 1], [0, 0, 1, 0, 0, 0, 0],
                        [1, 1, 1, 1, 1, 0, 1], [0, 0, 1, 0, 0, 0, 0], [1, 1, 1, 1, 1, 0, 1],
                        [1, 0, 0, 1, 0, 1, 1]]
        elif params == 5 or params == '5x5':
            elemento = [[1, 1, 0, 0, 1], [1, 0, 0, 1, 1], [1, 1, 0, 0, 0], [1, 1, 0, 0, 1], [1, 1, 1, 1, 1]]
        else:
            elemento = [[1, 0, 1], [0, 1, 0], [1, 0, 0]]
        return np.asarray(elemento)

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        elemento = self.get_elemento(params)
        es = int((len(elemento) - 1) / 2)

        pixels = imagem.get_pixels()
        pixels = np.reshape(pixels, (imagem.get_altura(), imagem.get_largura()))
        novos_pixels = pixels.copy()
        for px in range(es, imagem.get_altura() - es):
            for py in range(es, imagem.get_largura() - es):
                if pixels[px][py] == 1:
                    for ex in range(len(elemento)):
                        for ey in range(len(elemento[1])):
                            if elemento[ex][ey] == 1:
                                novos_pixels[px - es + ex][py - es + ey] = 1

        novos_pixels = np.reshape(novos_pixels, len(imagem.get_pixels()))
        imagem.set_pixels(novos_pixels)
        return imagem


class ProcessamentoAbertura(Processamento):
    def get_nome(self) -> str:
        return 'Abertura'

    def get_descricao(self) -> str:
        return ''

    def get_permitir_binarias(self) -> bool:
        return True

    def get_permitir_nao_binarias(self) -> bool:
        return False

    def get_default_params(self):
        return [
            ('3x3', 3),
            ('5x5', 5),
            ('7x7', 7),
            ('9x9', 9)
        ]

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        imagem = self.get_processamentos().get_erosao().processar(imagem, params)
        imagem = self.get_processamentos().get_dilatacao().processar(imagem, params)
        return imagem


class ProcessamentoFechamento(Processamento):
    def get_nome(self) -> str:
        return 'Fechamento'

    def get_descricao(self) -> str:
        return ''

    def get_permitir_binarias(self) -> bool:
        return True

    def get_permitir_nao_binarias(self) -> bool:
        return False

    def get_default_params(self):
        return [
            ('3x3', 3),
            ('5x5', 5),
            ('7x7', 7),
            ('9x9', 9)
        ]

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        imagem = self.get_processamentos().get_dilatacao().processar(imagem, params)
        imagem = self.get_processamentos().get_erosao().processar(imagem, params)
        return imagem


class ProcessamentoDeteccaoBordaErosao(Processamento):
    def get_nome(self) -> str:
        return 'Detecção de Borda por Erosao'

    def get_descricao(self) -> str:
        return ''

    def get_permitir_binarias(self) -> bool:
        return True

    def get_permitir_nao_binarias(self) -> bool:
        return False

    def get_default_params(self):
        return [
            ('3x3', 3),
            ('5x5', 5),
            ('7x7', 7),
            ('9x9', 9)
        ]

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        imagem_original = imagem
        imagem_erosao = self.get_processamentos().get_erosao().processar(imagem.clonar(), params)

        pixels_original = imagem_original.get_pixels()
        pixels_erosao = imagem_erosao.get_pixels()

        for i in range(len(pixels_original)):
            pixels_original[i] = (pixels_original[i] - pixels_erosao[i]) % 2
        return imagem


class ProcessamentoDeteccaoBordaDilatacao(Processamento):
    def get_nome(self) -> str:
        return 'Detecção de Borda por Dilatacao'

    def get_descricao(self) -> str:
        return ''

    def get_permitir_binarias(self) -> bool:
        return True

    def get_permitir_nao_binarias(self) -> bool:
        return False

    def get_default_params(self):
        return [
            ('3x3', 3),
            ('5x5', 5),
            ('7x7', 7),
            ('9x9', 9)
        ]

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        imagem_original = imagem
        imagem_dilatacao = self.get_processamentos().get_dilatacao().processar(imagem.clonar(), params)

        pixels_original = imagem_original.get_pixels()
        pixels_dilatacao = imagem_dilatacao.get_pixels()

        for i in range(len(pixels_original)):
            pixels_original[i] = (pixels_original[i] - pixels_dilatacao[i]) % 2
        return imagem


class ProcessamentoRodarImagem(Processamento):
    def get_nome(self) -> str:
        return 'Rodar'

    def get_descricao(self) -> str:
        return ''

    def get_permitir_binarias(self) -> bool:
        return True

    def get_permitir_nao_binarias(self) -> bool:
        return True

    def get_default_params(self):
        return [
            ('90º →', 90),
            ('90º ←', 270),
            ('180º', 180)
        ]

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        if params is None:
            params = 90

        indice = int((params % 360) / 90)
        pixels = imagem.get_pixels()
        novos_pixels = []

        if indice % 2 == 1:
            aux = imagem.get_largura()
            imagem.set_largura(imagem.get_altura())
            imagem.set_altura(aux)

        largura = imagem.get_largura()
        altura = imagem.get_altura()

        if indice == 1:  # 90
            for j in range(0, altura):
                for i in range(largura - 1, -1, -1):
                    novos_pixels.append(pixels[imagem.get_pixel_index(i, j)])
        elif indice == 2:  # 180
            for i in range(largura - 1, -1, -1):
                for j in range(altura - 1, -1, -1):
                    novos_pixels.append(pixels[imagem.get_pixel_index(i, j)])
        elif indice == 3:  # 270
            for j in range(altura - 1, -1, -1):
                for i in range(0, largura):
                    novos_pixels.append(pixels[imagem.get_pixel_index(i, j)])

        imagem.set_pixels(np.array(novos_pixels))
        return imagem


class ProcessamentoEspelharImagem(Processamento):
    def get_nome(self) -> str:
        return 'Espelhar'

    def get_descricao(self) -> str:
        return ''

    def get_permitir_binarias(self) -> bool:
        return True

    def get_permitir_nao_binarias(self) -> bool:
        return True

    def get_default_params(self):
        return [
            ('Horizontal', 1),
            ('Vertical', 0)
        ]

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        if params is None:
            params = 0

        indice = params
        pixels = imagem.get_pixels()
        novos_pixels = []

        largura = imagem.get_largura()
        altura = imagem.get_altura()

        if indice == 0:  # Vertical
            for i in range(largura - 1, -1, -1):
                for j in range(0, altura):
                    novos_pixels.append(pixels[imagem.get_pixel_index(i, j)])
        else:  # Horizontal
            for i in range(0, largura):
                for j in range(altura - 1, -1, -1):
                    novos_pixels.append(pixels[imagem.get_pixel_index(i, j)])

        imagem.set_pixels(np.array(novos_pixels))
        return imagem


class ProcessamentoAndyWarhol(Processamento):
    def get_nome(self) -> str:
        return 'Andy Warhol'

    def get_descricao(self) -> str:
        return ''

    def get_permitir_binarias(self) -> bool:
        return False

    def get_permitir_nao_binarias(self) -> bool:
        return True

    def get_default_params(self):
        return [
            ('Normal', 0),
            ('Espelhado', 1)
        ]

    def processar(self, imagem: Imagem, params=None) -> Imagem:
        if params is None:
            params = 0
        if imagem.get_tipo() == 'P3':
            imagem = self.get_processamentos().get_escala_cinza().processar(imagem)

        # Cores pre-definidas
        cores = [[[ 45, 165, 195], [149, 248,  63], [209, 206,  54], [ 95,  15, 191]],
                 [[127, 219, 218], [173, 228, 152], [237, 230, 130], [254, 191,  99]],
                 [[  0,   0,  92], [106,   9, 125], [192,  96, 161], [255, 220, 180]],
                 [[235, 236, 241], [ 32, 106,  93], [ 31,  64, 104], [ 27,  28,  37]]]
        random.shuffle(cores)

        # Colorir imagem
        pixels_coloridos = []
        for i in range(len(cores)):
            pixels_coloridos.append(self._processar_parcial(imagem, cores[i],
                                                            params == 1 and i >= len(cores) / 2))
        # Montar imagem
        meia_largura = imagem.get_largura()
        meia_altura = imagem.get_altura()
        largura = imagem.get_largura() * 2
        altura = imagem.get_altura() * 2

        novos_pixels = []
        for i in range(largura):
            for j in range(altura):
                indice_pixels_coloridos = int(j / meia_largura) * 2 + int(i / meia_largura)
                x = i % meia_largura
                y = j % meia_altura
                indice = x * meia_largura + y

                novos_pixels.append(pixels_coloridos[indice_pixels_coloridos][indice])

        imagem.set_largura(largura)
        imagem.set_altura(altura)
        imagem.set_tipo('P3')
        imagem.set_pixels(np.array(novos_pixels))
        return imagem

    def _processar_parcial(self, imagem, cores, espelhar):
        largura = imagem.get_largura()
        maxval = imagem.get_maxval()
        altura = imagem.get_altura()
        pixels = imagem.get_pixels().copy()

        canais = len(cores)
        por_canal = maxval / canais

        novos_pixels = []
        if not espelhar:  # Nao espelhar
            for i in range(len(pixels)):
                canal_pixel = int(pixels[i] / por_canal)
                novos_pixels.append(np.array(cores[canal_pixel]))
        else:  # Espelhar
            for i in range(0, largura):
                for j in range(altura - 1, -1, -1):
                    indice = imagem.get_pixel_index(i, j)
                    canal_pixel = int(pixels[indice] / por_canal)
                    novos_pixels.append(np.array(cores[canal_pixel]))
            pixels = np.array(novos_pixels)

        return novos_pixels


class Processamentos:
    instance = None

    def __init__(self):
        self.__negativo = None
        self.__correcao_gama = None
        self.__transformacao_logaritmica = None
        self.__filtro_sharpen = None
        self.__filtro_mediana = None
        self.__filtro_gaussiana = None
        self.__filtro_sobel = None
        self.__filtro_deteccao_borda = None
        self.__escala_cinza = None
        self.__preto_branco = None
        self.__erosao = None
        self.__dilatacao = None
        self.__abertura = None
        self.__fechamento = None
        self.__deteccao_borda_erosao = None
        self.__deteccao_borda_dilatacao = None
        self.__rodar_imagem = None
        self.__espelhar_imagem = None
        self.__andy_warhol = None

        self.__get_filtros = [
            self.get_negativo,
            self.get_correcao_gama,
            self.get_transformacao_logaritmica,
            self.get_filtro_sharpen,
            self.get_filtro_mediana,
            self.get_filtro_gaussiana,
            self.get_filtro_sobel,
            self.get_filtro_deteccao_borda,
            self.get_escala_cinza,
            self.get_preto_branco,
            self.get_erosao,
            self.get_dilatacao,
            self.get_abertura,
            self.get_fechamento,
            self.get_deteccao_borda_erosao,
            self.get_deteccao_borda_dilatacao,
            self.get_rodar_imagem,
            self.get_espelhar_imagem,
            self.get_andy_warhol
        ]

        if Processamentos.instance is None:
            Processamentos.instance = self

    def get_todos(self):
        return [f() for f in self.__get_filtros if callable(f)]

    def get_negativo(self):
        if self.__negativo is None:
            self.__negativo = ProcessamentoNegativo()
        return self.__negativo

    def get_correcao_gama(self):
        if self.__correcao_gama is None:
            self.__correcao_gama = ProcessamentoCorrecaoGama()
        return self.__correcao_gama

    def get_transformacao_logaritmica(self):
        if self.__transformacao_logaritmica is None:
            self.__transformacao_logaritmica = ProcessamentoTransformacaoLogaritmica()
        return self.__transformacao_logaritmica

    def get_filtro_sharpen(self):
        if self.__filtro_sharpen is None:
            self.__filtro_sharpen = ProcessamentoFiltroSharpen()
        return self.__filtro_sharpen

    def get_filtro_mediana(self):
        if self.__filtro_mediana is None:
            self.__filtro_mediana = ProcessamentoFiltroMediana()
        return self.__filtro_mediana

    def get_filtro_gaussiana(self):
        if self.__filtro_gaussiana is None:
            self.__filtro_gaussiana = ProcessamentoFiltroGaussiana()
        return self.__filtro_gaussiana

    def get_filtro_sobel(self):
        if self.__filtro_sobel is None:
            self.__filtro_sobel = ProcessamentoFiltroSobel()
        return self.__filtro_sobel

    def get_filtro_deteccao_borda(self):
        if self.__filtro_deteccao_borda is None:
            self.__filtro_deteccao_borda = ProcessamentoFiltroDeteccaoBorda()
        return self.__filtro_deteccao_borda

    def get_escala_cinza(self):
        if self.__escala_cinza is None:
            self.__escala_cinza = ProcessamentoEscalaCinza()
        return self.__escala_cinza

    def get_preto_branco(self):
        if self.__preto_branco is None:
            self.__preto_branco = ProcessamentoPretoBranco()
        return self.__preto_branco

    def get_erosao(self):
        if self.__erosao is None:
            self.__erosao = ProcessamentoErosao()
        return self.__erosao

    def get_dilatacao(self):
        if self.__dilatacao is None:
            self.__dilatacao = ProcessamentoDilatacao()
        return self.__dilatacao

    def get_abertura(self):
        if self.__abertura is None:
            self.__abertura = ProcessamentoAbertura()
        return self.__abertura

    def get_fechamento(self):
        if self.__fechamento is None:
            self.__fechamento = ProcessamentoFechamento()
        return self.__fechamento

    def get_deteccao_borda_erosao(self):
        if self.__deteccao_borda_erosao is None:
            self.__deteccao_borda_erosao = ProcessamentoDeteccaoBordaErosao()
        return self.__deteccao_borda_erosao

    def get_deteccao_borda_dilatacao(self):
        if self.__deteccao_borda_dilatacao is None:
            self.__deteccao_borda_dilatacao = ProcessamentoDeteccaoBordaDilatacao()
        return self.__deteccao_borda_dilatacao

    def get_rodar_imagem(self):
        if self.__rodar_imagem is None:
            self.__rodar_imagem = ProcessamentoRodarImagem()
        return self.__rodar_imagem

    def get_espelhar_imagem(self):
        if self.__espelhar_imagem is None:
            self.__espelhar_imagem = ProcessamentoEspelharImagem()
        return self.__espelhar_imagem

    def get_andy_warhol(self):
        if self.__andy_warhol is None:
            self.__andy_warhol = ProcessamentoAndyWarhol()
        return self.__andy_warhol
