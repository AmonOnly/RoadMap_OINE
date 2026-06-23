# OINE AI Roadmap (Física)

Aplicativo desktop em Tkinter para gerar uma trilha de estudos personalizada para a OINE em Física.

## ✅ Recursos

- Formulário simples para aluno, nível, horas e objetivo.
- Roadmap semanal com sugestões inteligentes.
- Texto pronto para copiar e estudar.
- Quiz com perguntas online (fallback offline) e feedback por resposta.
- Trilha diária estilo Duolingo com bolinhas, conteúdos e progresso salvo.
- Versão web com frontend moderno e backend Flask.
- **Assistente de IA Claude integrado** para ajudar nas dúvidas de Física.
- **3 Páginas principais**: Conteúdos (hub), Conteúdo Diário e Quiz Adaptativo.

## ▶️ Como executar

### 1. Instalar dependências

```bash
python -m pip install -r requirements.txt
```

### 2. Configurar a IA Claude (Opcional)

Para usar o assistente de IA, você precisa de uma chave API do Claude:

1. Acesse [https://console.anthropic.com/](https://console.anthropic.com/)
2. Crie uma conta e gere uma chave API
3. Copie o arquivo `.env.example` para `.env` e adicione sua chave:

```bash
cp .env.example .env
```

4. Edite `.env` e substitua `your_api_key_here` pela sua chave:

```
CLAUDE_API_KEY=sua_chave_aqui
```

### 3. Executar a aplicação web

```bash
python web/app.py
```

Abra http://127.0.0.1:5000 no navegador.

### 4. Executar a versão desktop (Tkinter)

```bash
python main.py
```

## 📱 Páginas da versão web

1. **Conteúdos** (`/conteudos`) - Hub central com acesso a todos os recursos
2. **Conteúdo Diário** (`/conteudo-diario`) - Conteúdo específico do dia com explicações
3. **Quiz Adaptativo** (`/quiz`) - Quiz inteligente que se adapta ao seu desempenho

## 🧪 Testes rápidos

```bash
python -m unittest discover -s tests
```

## ℹ️ Observações

- Se o Tkinter não estiver disponível na sua distro Linux, instale o pacote do sistema `python3-tk`.
- O progresso diário é salvo em `progress.json`.
- A IA é totalmente opcional - o app funciona sem ela.
- As perguntas do quiz são buscadas da Open Trivia Database com fallback para perguntas locais.
