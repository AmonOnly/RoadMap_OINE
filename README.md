# OINE AI Roadmap (Física)

Aplicativo desktop em Tkinter para gerar uma trilha de estudos personalizada para a OINE em Física.

## ✅ Recursos

- Formulário simples para aluno, nível, horas e objetivo.
- Roadmap semanal com sugestões inteligentes.
- Texto pronto para copiar e estudar.
- Quiz com perguntas online (fallback offline) e feedback por resposta.
- Trilha diária estilo Duolingo com bolinhas, conteúdos e progresso salvo.
- Versão web com frontend moderno e backend Flask.

## ▶️ Como executar

1. Certifique-se de ter Python 3 instalado (Tkinter já vem com a instalação padrão).
2. Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

3. Rode o aplicativo (desktop Tkinter):

```bash
python main.py
```

## 🌐 Versão web (backend + frontend)

```bash
python -m pip install -r requirements.txt
python web/app.py
```

Abra http://127.0.0.1:5000 no navegador.

## 🧪 Testes rápidos

```bash
python -m unittest discover -s tests
```

## ℹ️ Observações

Se o Tkinter não estiver disponível na sua distro Linux, instale o pacote do sistema `python3-tk`.

O progresso diário é salvo em `progress.json`.
