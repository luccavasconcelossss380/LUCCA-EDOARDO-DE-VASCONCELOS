"""Operações com imagens separadas da apresentação para facilitar a conferência."""
from io import BytesIO
import numpy as np
from PIL import Image, ImageOps

FORMULAS = {
    "Autoral · estrela": "padrao(x, y, k)",
    "Listras verticais": "(x * k) % 256",
    "Diagonais": "((x + y) * k) % 256",
    "XOR": "((x ^ y) * k) % 256",
    "Círculos": "(((x - 32)**2 + (y - 32)**2) * k // 4) % 256",
    "Produto": "(x * y * k) % 256",
    "Diagonais inclinadas": "((x + 2 * y) * k) % 256",
    "Quadrático": "(x**2 * k) % 256",
}


def ampliar(imagem, k=30):
    return imagem.repeat(k, axis=0).repeat(k, axis=1)


def hex_rgb(cor):
    return tuple(int(cor.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))


def criar_bandeira(altura=12, largura=18, cores=((0, 43, 127), (252, 209, 22), (206, 17, 38))):
    """Romênia: três faixas verticais, desenhadas apenas com fatias NumPy."""
    bandeira = np.zeros((altura, largura, 3), dtype=np.uint8)
    a, b = largura // 3, 2 * largura // 3
    bandeira[:, :a] = cores[0]
    bandeira[:, a:b] = cores[1]
    bandeira[:, b:] = cores[2]
    return bandeira


def padrao(x, y, k):
    """Estrela de cinco pontas; k controla tamanho e rotação."""
    x, y = np.broadcast_arrays(np.asarray(x), np.asarray(y))
    angulos = np.arange(10) * np.pi / 5 - np.pi / 2 + (k - 4) * np.pi / 40
    raio = 20 + 0.4 * k
    raios = np.where(np.arange(10) % 2 == 0, raio, raio * 0.45)
    vx = 31.5 + raios * np.cos(angulos)
    vy = 31.5 + raios * np.sin(angulos)
    dentro = np.zeros(x.shape, dtype=bool)
    for i in range(10):
        j = (i + 1) % 10
        altura = vy[j] - vy[i]
        if abs(altura) < 1e-12:
            continue
        cruza = ((vy[i] > y) != (vy[j] > y)) & (x < (vx[j] - vx[i]) * (y - vy[i]) / altura + vx[i])
        dentro ^= cruza
    return np.where(dentro, 255, 0).astype(np.uint8)


def gerar_padrao(nome, k):
    y, x = np.indices((64, 64))
    # Fórmulas explícitas, sem executar código fornecido pelo usuário.
    formulas = (
        lambda: padrao(x, y, k),
        lambda: (x * k) % 256,
        lambda: ((x + y) * k) % 256,
        lambda: ((x ^ y) * k) % 256,
        lambda: (((x - 32)**2 + (y - 32)**2) * k // 4) % 256,
        lambda: (x * y * k) % 256,
        lambda: ((x + 2 * y) * k) % 256,
        lambda: (x**2 * k) % 256,
    )
    return formulas[list(FORMULAS).index(nome)]().astype(np.uint8)


def demonstracao():
    """Imagem sintética identificada como demonstração, não uma fotografia do aluno."""
    y, x = np.indices((288, 432))
    img = np.empty((288, 432, 3), dtype=np.uint8)
    img[:, :, 0] = np.clip(x / 431 * 255, 0, 255)
    img[:, :, 1] = np.clip(y / 287 * 255, 0, 255)
    img[:, :, 2] = np.clip((1 - x / 431) * 190 + 30, 0, 255)
    for i, cor in enumerate(((255, 45, 45), (45, 230, 90), (35, 80, 255))):
        circulo = (x - (95 + i * 120))**2 + (y - 140)**2 < 43**2
        img[circulo] = cor
    return img


def ler_foto(dados):
    with Image.open(BytesIO(dados)) as original:
        if original.width * original.height > 24_000_000:
            raise ValueError("Escolha uma imagem com até 24 milhões de pixels.")
        foto = ImageOps.exif_transpose(original)
        if foto.mode in ("RGBA", "LA") or "transparency" in foto.info:
            rgba = foto.convert("RGBA")
            fundo = Image.new("RGBA", rgba.size, "white")
            foto = Image.alpha_composite(fundo, rgba)
        return np.array(foto.convert("RGB"))


def separar_canais(img):
    separados = []
    for canal in range(3):
        cor = np.zeros_like(img)
        cor[:, :, canal] = img[:, :, canal]
        separados.append(cor)
    return separados


def tons_cinza(img):
    f = img.astype(np.float64)
    media = f.mean(axis=2).astype(np.uint8)
    ponderada = (0.299 * f[:, :, 0] + 0.587 * f[:, :, 1] + 0.114 * f[:, :, 2]).astype(np.uint8)
    return media, ponderada


def editar_rgb(img, vermelho=100, verde=100, azul=100, brilho=0):
    ganhos = np.array([vermelho, verde, azul], dtype=np.float32) / 100
    resultado = img.astype(np.float32) * ganhos + brilho
    return np.clip(resultado, 0, 255).astype(np.uint8)


def ajustar_brilho(img, valor):
    conta = img.astype(np.int16) + valor
    return (conta % 256).astype(np.uint8), np.clip(conta, 0, 255).astype(np.uint8)


def png(imagem):
    arquivo = BytesIO()
    Image.fromarray(imagem).save(arquivo, format="PNG")
    return arquivo.getvalue()
