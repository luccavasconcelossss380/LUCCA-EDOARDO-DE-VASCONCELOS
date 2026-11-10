from io import BytesIO
from pathlib import Path
import unittest
from zipfile import ZipFile
import numpy as np
from PIL import Image
from streamlit.testing.v1 import AppTest
from src.processamento import (
    FORMULAS, ampliar, criar_bandeira, gerar_padrao, ler_foto,
    separar_canais, tons_cinza, ajustar_brilho, editar_rgb, png,
)
from src.relatorio import gerar_relatorio
from src.ambiente import pacote_projeto

RAIZ = Path(__file__).resolve().parents[1]


class ProcessamentoTest(unittest.TestCase):
    def test_ampliacao_preserva_blocos_e_canais(self):
        entrada = np.array([[[255, 0, 12], [0, 10, 255]]], dtype=np.uint8)
        resultado = ampliar(entrada, 3)
        self.assertEqual(resultado.shape, (3, 6, 3))
        np.testing.assert_array_equal(resultado[::3, ::3], entrada)

    def test_bandeira_tres_faixas(self):
        img = criar_bandeira()
        self.assertEqual(img.shape, (12, 18, 3))
        self.assertEqual(img.dtype, np.uint8)
        np.testing.assert_array_equal(img[0, [0, 6, 12]], [[0, 43, 127], [252, 209, 22], [206, 17, 38]])
        self.assertEqual(len(np.unique(img.reshape(-1, 3), axis=0)), 3)

    def test_padroes_nos_limites_do_slider(self):
        for nome in FORMULAS:
            for k in (1, 4, 8, 20):
                with self.subTest(nome=nome, k=k):
                    img = gerar_padrao(nome, k)
                    self.assertEqual(img.shape, (64, 64))
                    self.assertEqual(img.dtype, np.uint8)
        self.assertEqual(gerar_padrao("Listras verticais", 8)[0, 32], 0)
        self.assertNotEqual(gerar_padrao(next(iter(FORMULAS)), 1).tobytes(),
                            gerar_padrao(next(iter(FORMULAS)), 20).tobytes())

    def test_brilho_nao_confunde_estouro_com_clip(self):
        img = np.array([[0, 50, 200, 250, 255]], dtype=np.uint8)
        volta, clip = ajustar_brilho(img, 100)
        np.testing.assert_array_equal(volta, [[100, 150, 44, 94, 99]])
        np.testing.assert_array_equal(clip, [[100, 150, 255, 255, 255]])
        volta, clip = ajustar_brilho(img, -100)
        self.assertEqual(int(volta[0, 1]), 206)
        self.assertEqual(int(clip[0, 1]), 0)

    def test_canais_reconstituem_original_sem_mutacao(self):
        img = np.random.default_rng(7).integers(0, 256, (5, 7, 3), dtype=np.uint8)
        antes = img.copy()
        canais = separar_canais(img)
        np.testing.assert_array_equal(sum(c.astype(np.uint16) for c in canais), img)
        np.testing.assert_array_equal(img, antes)

    def test_cinza_cores_saturadas_e_pixel_claro(self):
        img = np.array([[[200, 100, 50], [0, 255, 0], [0, 0, 255], [255, 255, 255]]], dtype=np.uint8)
        media, ponderada = tons_cinza(img)
        np.testing.assert_array_equal(media, [[116, 85, 85, 255]])
        np.testing.assert_array_equal(ponderada, [[124, 149, 29, 255]])

    def test_edicao_rgb_preserva_original_e_limita_valores(self):
        img = np.array([[[200, 100, 50], [255, 0, 255]]], dtype=np.uint8)
        antes = img.copy()
        np.testing.assert_array_equal(editar_rgb(img), img)
        np.testing.assert_array_equal(editar_rgb(img, 200, 0, 100, 10), [[[255, 10, 60], [255, 10, 255]]])
        np.testing.assert_array_equal(editar_rgb(img, 0, 0, 0, -100), np.zeros_like(img))
        np.testing.assert_array_equal(img, antes)

    def test_leitura_cinza_alpha_cmyk_e_png(self):
        for modo, cor in (("L", 128), ("RGBA", (255, 0, 0, 0)), ("CMYK", (0, 255, 255, 0))):
            with self.subTest(modo=modo):
                buffer = BytesIO()
                Image.new(modo, (3, 2), cor).save(buffer, format="JPEG" if modo == "CMYK" else "PNG")
                img = ler_foto(buffer.getvalue())
                self.assertEqual(img.shape, (2, 3, 3))
                self.assertEqual(img.dtype, np.uint8)
                np.testing.assert_array_equal(ler_foto(png(img)), img)
                if modo == "RGBA":
                    self.assertTrue(np.all(img == 255))

    def test_arquivo_invalido(self):
        with self.assertRaises(OSError):
            ler_foto(b"isto nao e uma foto")

    def test_zip_contem_apenas_laboratorio(self):
        with ZipFile(BytesIO(pacote_projeto())) as z:
            arquivos = z.namelist()
            self.assertIn("laboratorio-cg/src/atv4.py", arquivos)
            self.assertIn("laboratorio-cg/uv.lock", arquivos)
            self.assertFalse(any(".venv" in n or "backend/" in n or "__pycache__" in n for n in arquivos))

    def test_relatorio_tem_12_topicos_10_evidencias(self):
        from docx import Document
        evidencia = png(np.full((120, 200, 3), 128, dtype=np.uint8))
        dados = gerar_relatorio("Aluno Teste", "A", "https://github.com/teste/lab", {i: evidencia for i in range(10)}, {}, "Ambiente verificado.")
        doc = Document(BytesIO(dados))
        self.assertEqual(len(doc.inline_shapes), 10)
        titulos = [p.text for p in doc.paragraphs if p.style.name == "Heading 1"]
        self.assertEqual(len(titulos), 12)
        self.assertTrue(titulos[-1].startswith("12 "))


class InterfaceTest(unittest.TestCase):
    def app(self):
        app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=90).run()
        self.assertFalse(app.exception, str(app.exception))
        return app

    def verificar(self, app):
        self.assertFalse(app.exception, str(app.exception))

    def test_primeiro_app_aleatorio_e_tamanho_limite(self):
        app = self.app()
        app.radio(key="modo_inicial").set_value("Valores aleatórios").run()
        app.slider(key="tamanho_inicial").set_value(64).run()
        self.verificar(app)

    def test_navegacao_quatro_atividades(self):
        app = self.app()
        for pagina in ("src/atv2.py", "src/atv3.py", "src/atv4.py", "src/atv1.py"):
            app.switch_page(pagina).run()
            self.verificar(app)
            self.assertEqual(len(app.code), 0)
            self.assertTrue(any("Lucca Edoardo de Vasconcelos" in item.value for item in app.markdown))

    def test_reset_da_bandeira(self):
        app = self.app().switch_page("src/atv2.py").run()
        app.color_picker(key="bandeira_Azul").set_value("#000000").run()
        next(b for b in app.button if b.label == "Restaurar cores da bandeira").click().run()
        self.assertEqual(app.color_picker(key="bandeira_Azul").value, "#002B7F")
        self.verificar(app)

    def test_controles_do_padrao(self):
        app = self.app().switch_page("src/atv3.py").run()
        self.assertEqual(len(app.selectbox), 0)
        self.assertEqual(len(app.tabs), 0)
        self.assertEqual(len(app.slider), 1)
        app.slider(key="padrao_k").set_value(20).run()
        self.verificar(app)

    def test_foto_atualiza_sem_confirmar_e_reset_restaura(self):
        app = self.app().switch_page("src/atv4.py").run()
        antes = app.get("image")[1].proto.SerializeToString()
        app.slider(key="foto_r").set_value(0).run()
        depois = app.get("image")[1].proto.SerializeToString()
        self.assertNotEqual(antes, depois)
        self.verificar(app)
        app.radio(key="foto_modo").set_value("Cinza ponderado").run()
        self.verificar(app)
        next(b for b in app.button if b.label == "Restaurar ajustes").click().run()
        self.assertEqual(app.slider(key="foto_r").value, 100)
        self.assertEqual(app.radio(key="foto_modo").value, "RGB")
        self.assertEqual(antes, app.get("image")[1].proto.SerializeToString())
        self.verificar(app)

    def test_fotografia_pequena_e_colorida(self):
        app = self.app()
        for shape in ((2, 3, 3), (140, 180, 3)):
            app.session_state["foto_rgb"] = np.full(shape, [200, 100, 50], dtype=np.uint8)
            app.session_state["nome_foto_rgb"] = "foto de teste"
            app.switch_page("src/atv4.py").run()
            self.verificar(app)
            self.assertEqual(len(app.header), 4)


if __name__ == "__main__":
    unittest.main()
