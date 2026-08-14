import flet as ft
import json
import random
import os

# Aponta para o arquivo JSON na mesma pasta
diretorio_atual = os.getcwd()
caminho_json = os.path.join(diretorio_atual, "questoes.json")

with open(caminho_json, "r", encoding="utf-8") as arquivo:
    questoes_originais = json.load(arquivo)

def main(page: ft.Page):
    page.title = "Quiz de Redes - Unidade 1"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    questoes_pendentes = questoes_originais.copy()
    random.shuffle(questoes_pendentes)

    pontuacao = 0
    total_questoes = len(questoes_originais)
    questao_atual = None
    lista_checkboxes = []

    texto_pontuacao = ft.Text(size=28, weight=ft.FontWeight.BOLD, color="blue")
    texto_pergunta = ft.Text(size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    
    # O feedback agora precisa ser uma Coluna para listar os erros e acertos separadamente
    coluna_feedback = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.START)
    coluna_opcoes = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.START)

    botao_confirmar = ft.ElevatedButton("Confirmar Resposta ✔️", on_click=lambda e: verificar_resposta())
    botao_continuar = ft.ElevatedButton("Continuar ➡️", visible=False, on_click=lambda e: carregar_proxima_questao())

    def verificar_resposta():
        nonlocal pontuacao

        respostas_certas = questao_atual["respostas_certas"]
        explicacoes = questao_atual.get("explicacoes", {})

        # Verifica se pelo menos uma foi marcada
        marcou_alguma = any(cb.value for cb in lista_checkboxes)
        if not marcou_alguma:
            coluna_feedback.controls.clear()
            coluna_feedback.controls.append(ft.Text("⚠️ Marque pelo menos uma opção antes de confirmar!", color="orange", weight=ft.FontWeight.BOLD))
            page.update()
            return

        botao_confirmar.visible = False
        for cb in lista_checkboxes:
            cb.disabled = True

        coluna_feedback.controls.clear()
        teve_erro = False
        teve_falta = False

        # Analisa checkbox por checkbox
        for cb in lista_checkboxes:
            resp = cb.data
            marcada = cb.value
            texto_explicacao = explicacoes.get(resp, "")

            if marcada and resp in respostas_certas:
                coluna_feedback.controls.append(ft.Text(f"✅ Acertou: {resp}\n👉 {texto_explicacao}", color="green", weight=ft.FontWeight.W_500))
            elif marcada and resp not in respostas_certas:
                teve_erro = True
                coluna_feedback.controls.append(ft.Text(f"❌ Errou ao marcar: {resp}\n👉 {texto_explicacao}", color="red", weight=ft.FontWeight.W_500))
            elif not marcada and resp in respostas_certas:
                teve_falta = True
                coluna_feedback.controls.append(ft.Text(f"⚠️ Esqueceu de marcar: {resp}\n👉 {texto_explicacao}", color="orange", weight=ft.FontWeight.W_500))

        # Se foi 100% perfeito (nenhum erro e nenhuma faltando)
        if not teve_erro and not teve_falta:
            pontuacao += 1
            coluna_feedback.controls.insert(0, ft.Text("🎉 Perfeito! Você acertou tudo nesta questão!", size=18, color="green", weight=ft.FontWeight.BOLD))
        else:
            coluna_feedback.controls.insert(0, ft.Text("📝 Você cometeu alguns deslizes:", size=18, color="red", weight=ft.FontWeight.BOLD))
            
            # Repetição Espaçada: volta pro bolo
            if len(questoes_pendentes) > 0:
                questoes_pendentes.insert(random.randint(0, len(questoes_pendentes)), questao_atual)
            else:
                questoes_pendentes.append(questao_atual)

        botao_continuar.visible = True
        page.update()

    def carregar_proxima_questao():
        nonlocal questao_atual
        coluna_feedback.controls.clear()
        botao_continuar.visible = False
        botao_confirmar.visible = True

        if len(questoes_pendentes) > 0:
            questao_atual = questoes_pendentes.pop(0)

            texto_pontuacao.value = f"{pontuacao:02d}/{total_questoes:02d}"
            texto_pergunta.value = questao_atual['pergunta']

            opcoes = questao_atual["opcoes"].copy()
            random.shuffle(opcoes)

            coluna_opcoes.controls.clear()
            lista_checkboxes.clear()

            for opcao in opcoes:
                cb = ft.Checkbox(label=opcao, value=False, data=opcao)
                lista_checkboxes.append(cb)
                coluna_opcoes.controls.append(cb)
        else:
            texto_pontuacao.value = f"{pontuacao:02d}/{total_questoes:02d}"
            texto_pergunta.value = "🎉 Parabéns! Você dominou a lista de Redes I!"
            coluna_opcoes.controls.clear()
            botao_confirmar.visible = False

        page.update()

    page.add(
        texto_pontuacao,
        texto_pergunta,
        coluna_opcoes,
        botao_confirmar,
        coluna_feedback,
        botao_continuar
    )

    carregar_proxima_questao()

ft.app(target=main)