"""
    Trabalho Final de Processamento Digital de Imagens
                                   Wender Castro, 2020

    Contém as definições de imagem.
    São elas:
    - PBM
    - PGM
    - PPM
"""

import numpy as np
import re


class Cor:
    def __init__(self, r: int, g: int, b: int):
        self.__r = r
        self.__g = g
        self.__b = b

    def get_r(self) -> int:
        return self.__r

    def get_g(self) -> int:
        return self.__g

    def get_b(self) -> int:
        return self.__b

    def __str__(self):
        return '[' + str(self.get_r()) + ',' + str(self.get_g()) + ',' + str(self.get_b()) + ']'


class FormatoImagem:
    def __init__(self, imagem: 'Imagem'):
        self.__imagem = imagem

    def get_imagem(self) -> 'Imagem':
        return self.__imagem

    def get_binario(self) -> bool:
        pass

    def get_maxval(self) -> int:
        pass

    def set_maxval(self, maxval: int):
        pass

    def get_extensao(self) -> str:
        pass

    def get_pixel(self, x, y) -> Cor or None:
        pass

    def set_pixel(self, x, y, cor: Cor or int):
        pass

    def get_pixels(self):
        pass

    def set_pixels(self, pixels):
        pass

    def read_maxval(self, arquivo):
        pass

    def read_pixels(self, arquivo):
        pass

    def write_maxval(self, arquivo):
        pass

    def write_pixels(self, arquivo):
        pass

    def clonar(self, imagem: 'Imagem') -> 'FormatoImagem':
        pass


class FormatoPBM(FormatoImagem):
    def __init__(self, imagem):
        FormatoImagem.__init__(self, imagem)

        self.__pixels = None

    def get_binario(self) -> bool:
        return True

    def get_maxval(self) -> int:
        return 1

    def set_maxval(self, maxval: int):
        pass

    def get_extensao(self) -> str:
        return '.pbm'

    def get_pixel(self, x, y) -> Cor:
        if self.__pixels is None:
            raise Exception()

        indice = (x * self.get_imagem().get_largura()) + y
        if self.__pixels[indice] == 0:
            cor = 0
        else:
            cor = 255

        return Cor(cor, cor, cor)

    def set_pixel(self, x, y, cor: Cor or int):
        if self.__pixels is None:
            raise Exception()
        if type(cor) != int:
            raise Exception()

        indice = (x * self.get_imagem().get_largura()) + y
        self.__pixels[indice] = cor % 2

    def get_pixels(self):
        return self.__pixels

    def set_pixels(self, pixels):
        self.__pixels = pixels

    def read_maxval(self, arquivo):
        pass

    def read_pixels(self, arquivo):
        imagem = self.get_imagem().pre_processar_resto(arquivo)
        imagem = re.sub(r'\s', '', imagem)
        imagem = np.asarray(list(imagem), dtype=int)
        self.__pixels = imagem

    def write_maxval(self, arquivo):
        pass

    def write_pixels(self, arquivo):
        bits = [str(p) + '\n' for p in self.__pixels]
        arquivo.writelines(bits)

    def clonar(self, imagem: 'Imagem'):
        clone = FormatoPBM(imagem)
        clone.__pixels = np.copy(self.__pixels)
        return clone


class FormatoPGM(FormatoImagem):
    def __init__(self, imagem):
        FormatoImagem.__init__(self, imagem)

        self.__maxval = 255
        self.__pixels = None

    def get_binario(self) -> bool:
        return False

    def get_maxval(self) -> int:
        return self.__maxval

    def set_maxval(self, maxval: int):
        self.__maxval = maxval

    def get_extensao(self) -> str:
        return '.pgm'

    def get_pixel(self, x, y) -> Cor:
        if self.__pixels is None:
            raise Exception()

        indice = (x * self.get_imagem().get_largura()) + y
        cor = Imagem.get_cor_255(self.__pixels[indice], self.__maxval)
        return Cor(cor, cor, cor)

    def set_pixel(self, x, y, cor: Cor or int):
        if self.__pixels is None:
            raise Exception()
        if type(cor) != int:
            raise Exception()

        indice = (x * self.get_imagem().get_largura()) + y
        self.__pixels[indice] = cor % self.__maxval

    def get_pixels(self):
        return self.__pixels

    def set_pixels(self, pixels):
        self.__pixels = pixels

    def read_maxval(self, arquivo):
        self.__maxval = int(self.get_imagem().pre_processar_linha(arquivo))

    def read_pixels(self, arquivo):
        imagem = self.get_imagem().pre_processar_resto(arquivo)
        imagem = np.asarray(imagem.split(), dtype=int)
        self.__pixels = imagem

    def write_maxval(self, arquivo):
        arquivo.write(str(self.get_maxval()) + '\n')

    def write_pixels(self, arquivo):
        bits = [str(p) + '\n' for p in self.__pixels]
        arquivo.writelines(bits)

    def clonar(self, imagem: 'Imagem'):
        clone = FormatoPGM(imagem)
        clone.__maxval = self.__maxval
        clone.__pixels = np.copy(self.__pixels)
        return clone


class FormatoPPM(FormatoImagem):
    def __init__(self, imagem):
        FormatoImagem.__init__(self, imagem)

        self.__maxval = 255
        self.__pixels = None

    def get_binario(self) -> bool:
        return False

    def get_maxval(self) -> int:
        return self.__maxval

    def set_maxval(self, maxval: int):
        self.__maxval = maxval

    def get_extensao(self) -> str:
        return '.ppm'

    def get_pixel(self, x, y) -> Cor:
        if self.__pixels is None:
            raise Exception()

        indice = (x * self.get_imagem().get_largura()) + y
        return Cor(Imagem.get_cor_255(self.__pixels[indice][0], self.__maxval),
                   Imagem.get_cor_255(self.__pixels[indice][1], self.__maxval),
                   Imagem.get_cor_255(self.__pixels[indice][2], self.__maxval))

    def set_pixel(self, x, y, cor: Cor or int):
        if self.__pixels is None:
            raise Exception()
        if type(cor) != Cor:
            raise Exception()

        indice = (x * self.get_imagem().get_largura()) + y
        self.__pixels[indice][0] = Imagem.get_cor_maxval(cor.get_r(), self.__maxval)
        self.__pixels[indice][1] = Imagem.get_cor_maxval(cor.get_g(), self.__maxval)
        self.__pixels[indice][2] = Imagem.get_cor_maxval(cor.get_b(), self.__maxval)

    def get_pixels(self):
        return self.__pixels

    def set_pixels(self, pixels):
        self.__pixels = pixels

    def read_maxval(self, arquivo):
        self.__maxval = int(self.get_imagem().pre_processar_linha(arquivo))

    def read_pixels(self, arquivo):
        imagem = self.get_imagem().pre_processar_resto(arquivo)
        imagem = np.asarray(imagem.split(), dtype=int)
        imagem = np.reshape(imagem, (self.get_imagem().get_altura() * self.get_imagem().get_largura(), 3))
        self.__pixels = imagem

    def write_maxval(self, arquivo):
        arquivo.write(str(self.get_maxval()) + '\n')

    def write_pixels(self, arquivo):
        bits = [str(p[0]) + ' ' + str(p[1]) + ' ' + str(p[2]) + '\n' for p in self.__pixels]
        arquivo.writelines(bits)

    def clonar(self, imagem: 'Imagem'):
        clone = FormatoPPM(imagem)
        clone.__maxval = self.__maxval
        clone.__pixels = np.copy(self.__pixels)
        return clone


class FormatoImagemFactory:
    @staticmethod
    def get_formato(imagem: 'Imagem') -> FormatoImagem or None:
        if imagem.get_tipo() == 'P1':
            return FormatoPBM(imagem)
        elif imagem.get_tipo() == 'P2':
            return FormatoPGM(imagem)
        elif imagem.get_tipo() == 'P3':
            return FormatoPPM(imagem)
        elif imagem.get_tipo() == 'P4' or imagem.get_tipo() == 'P5' or imagem.get_tipo() == 'P6':
            print('Formatos binários nao foram implementados, utilize formatos em plain-text.')
            raise Exception()
        return None


class Imagem:
    """
        Classe que reconhece arquivos de imagem.

        Detalhamento:
          http://netpbm.sourceforge.net/doc/pbm.html
          http://netpbm.sourceforge.net/doc/pgm.html
          http://netpbm.sourceforge.net/doc/ppm.html
    """
    def __init__(self):
        self.__altura = -1
        self.__largura = -1
        self.__caminho = ''
        self.__tipo = ''
        self.__comentario = ''
        self.__erro = ''
        self.__formato = None

    def get_largura(self) -> int:
        return self.__largura

    def set_largura(self, largura: int):
        self.__largura = largura

    def get_altura(self) -> int:
        return self.__altura

    def set_altura(self, altura: int):
        self.__altura = altura

    def get_binario(self) -> bool:
        if self.__formato is None:
            raise Exception()
        return self.__formato.get_binario()

    def get_caminho(self) -> str:
        return self.__caminho

    def get_tipo(self) -> str:
        return self.__tipo

    def set_tipo(self, tipo: str):
        self.__tipo = tipo
        self.__formato = FormatoImagemFactory.get_formato(self)

    def get_comentario(self) -> str:
        return self.__comentario

    def set_comentario(self, comentario: str):
        self.__comentario = comentario

    def get_erro(self) -> str:
        return self.__erro

    def get_maxval(self) -> int:
        if self.__formato is None:
            raise Exception()
        return self.__formato.get_maxval()

    def set_maxval(self, maxval: int):
        if self.__formato is None:
            raise Exception()
        self.__formato.set_maxval(maxval)

    def get_extensao(self) -> int:
        if self.__formato is None:
            raise Exception()
        return self.__formato.get_extensao()

    def get_pixel(self, x, y) -> Cor or None:
        if x < 0 or x >= self.__largura or y < 0 or y >= self.__altura:
            return None
        if self.__formato is None:
            raise Exception()
        return self.__formato.get_pixel(x, y)

    def set_pixel(self, x, y, cor: Cor or int):
        if self.__formato is None:
            raise Exception()
        self.__formato.set_pixel(x, y, cor)

    def get_pixels(self):
        if self.__formato is None:
            raise Exception()
        return self.__formato.get_pixels()

    def set_pixels(self, pixels):
        if self.__formato is None:
            raise Exception()
        self.__formato.set_pixels(pixels)

    def get_pixel_index(self, x: int, y: int) -> int:
        return (x * self.get_largura()) + y

    def get_pixel_position(self, index) -> (int, int):
        linha = int(index / self.get_largura())
        coluna = index % self.get_largura()
        return linha, coluna

    def carregar(self, caminho):
        try:
            # Resetar valores
            self.__altura = -1
            self.__largura = -1
            self.__caminho = caminho
            self.__tipo = None
            self.__comentario = ''
            self.__erro = None
            self.__formato = None

            # Abrir arquivo
            arquivo = open(caminho, 'r')

            # Ler tipo
            self.__tipo = self.pre_processar_linha(arquivo)

            # Pegar formato
            self.__formato = FormatoImagemFactory.get_formato(self)
            if self.__formato is None:
                self.__erro = 'Não foi possível reconhecer o arquivo.'
                return False

            # Ler dimensoes
            dimensoes = self.pre_processar_linha(arquivo)
            dimensoes = dimensoes.split()
            self.__largura = int(dimensoes[0])
            self.__altura = int(dimensoes[1])

            # Ler maxval
            self.__formato.read_maxval(arquivo)

            # Ler pixels
            self.__formato.read_pixels(arquivo)
            return True
        except Exception as e:
            self.__erro = 'Falha ao carregar arquivo.\n' + str(e)
            return False

    def salvar(self, caminho: str) -> bool:
        try:
            extensao = self.__formato.get_extensao().lower()
            if not caminho.lower().endswith(extensao):
                caminho = caminho + extensao

            self.__caminho = caminho

            # Abrir arquivo
            arquivo = open(caminho, 'w')

            # Escrever tipo
            arquivo.write(self.__tipo + '\n')

            # Escrever comentarios
            if self.__comentario is not None and len(self.__comentario) > 0:
                comentarios = self.__comentario.splitlines()
                comentarios = ['# ' + c + '\n' for c in comentarios]
                arquivo.writelines(comentarios)

            # Escrever tamanho
            arquivo.write(str(self.__largura) + ' ' + str(self.__altura) + '\n')

            # Escrever maxval
            self.__formato.write_maxval(arquivo)

            # Escrever pixels
            self.__formato.write_pixels(arquivo)
            return True
        except Exception as e:
            self.__erro = 'Falha ao escrever arquivo.\n' + str(e)
            return False

    def clonar(self) -> 'Imagem':
        clone = Imagem()
        if self.__formato is None:
            return clone

        clone.__altura = self.__altura
        clone.__largura = self.__largura
        clone.__caminho = self.__caminho
        clone.__tipo = self.__tipo
        clone.__comentario = self.__comentario
        clone.__erro = self.__erro
        clone.__formato = self.__formato.clonar(clone)
        return clone

    def pre_processar_linha(self, arquivo) -> str or None:
        (linha, comentario) = Imagem.get_linha(arquivo)
        if comentario is not None:
            if len(self.__comentario) == 0:
                self.__comentario = comentario
            else:
                self.__comentario = self.__comentario + '\n' + comentario

            if len(linha) != 0:
                return linha
            else:
                return self.pre_processar_linha(arquivo)
        else:
            return linha

    def pre_processar_resto(self, arquivo) -> str:
        resto = ''
        while True:
            linha = self.pre_processar_linha(arquivo)
            if linha is not None:
                resto = resto + ' ' + linha
            else:
                break
        return resto.strip()

    @staticmethod
    def get_linha(arquivo) -> (str, str or None):
        linha = arquivo.readline()
        if not linha:
            return None, None
        elif '#' in linha:
            indice = linha.index('#')
            comentario = linha[indice + 1:].strip()
            linha = linha[:indice].strip()

            if len(comentario) == 0:
                comentario = None
            return linha, comentario
        else:
            return linha.strip(), None

    @staticmethod
    def get_cor_255(cor, maxval) -> int:
        # res    cor
        # --- = -----
        # 255   maxval
        # res * maxval = cor * 255
        # res = (cor * 255) / maxval
        return round((cor * 255.0) / maxval)

    @staticmethod
    def get_cor_maxval(cor, maxval) -> int:
        # cor    res
        # --- = -----
        # 255   maxval
        # cor * maxval = res * 255
        # res = (cor * maxval) / 255
        return round((cor * maxval) / 255.0)


def converter_ppm(imagem: Imagem) -> Imagem:
    if imagem.get_tipo() == 'P3':
        return imagem.clonar()

    atualizar_maxval = imagem.get_maxval() == 1

    clone = imagem.clonar()
    clone.set_tipo('P3')

    pixels = []
    if not atualizar_maxval:
        clone.set_maxval(imagem.get_maxval())
        for p in imagem.get_pixels():
            pixels.append([p, p, p])
    else:
        maxval = clone.get_maxval()
        for p in imagem.get_pixels():
            v = p * maxval
            pixels.append([v, v, v])

    clone.set_pixels(np.array(pixels))
    return clone


def converter_pgm(imagem: Imagem) -> Imagem:
    if imagem.get_tipo() == 'P2':
        return imagem.clonar()

    clone = imagem.clonar()
    clone.set_tipo('P2')

    pixels = []
    if imagem.get_tipo() == 'P3':
        clone.set_maxval(imagem.get_maxval())
        for p in imagem.get_pixels():
            v = 0
            for c in p:
                v = v + c
            v = v / len(p)
            pixels.append(v)
    else:
        maxval = clone.get_maxval()
        for p in imagem.get_pixels():
            v = p * maxval
            pixels.append(v)

    clone.set_pixels(np.array(pixels))
    return clone


def converter_pbm(imagem: Imagem) -> Imagem:
    if imagem.get_tipo() == 'P1':
        return imagem.clonar()

    if imagem.get_tipo() == 'P3':
        clone = converter_pgm(imagem)
    else:
        clone = imagem.clonar()
    clone.set_tipo('P1')

    pixels = []
    for p in imagem.get_pixels():
        if p == 0:
            pixels.append(0)
        else:
            pixels.append(1)

    clone.set_pixels(np.array(pixels))
    return clone
