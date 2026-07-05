const state = {
  days: [],
  selected: null,
  selectedDate: null,
  quiz: [],
  topic: "Cinemática",
  stats: { xp: 0, streak: 0 },
  onboardingStep: 0,
};

const page = document.body?.dataset?.page || "home";

const daysGrid = document.getElementById("days-grid");
const dayLabel = document.getElementById("day-label");
const dayDifficulty = document.getElementById("day-difficulty");
const summary = document.getElementById("summary");
const quizArea = document.getElementById("quiz-area");
const quizSource = document.getElementById("quiz-source");
const quizInfo = document.getElementById("quiz-info");
const xpTotal = document.getElementById("xp-total");
const streak = document.getElementById("streak");
const resourceList = document.getElementById("resource-list");
const chatBox = document.getElementById("chat");
const chatInput = document.getElementById("chat-input");

const nameInput = document.getElementById("student-name");
const hoursInput = document.getElementById("hours");
const daysInput = document.getElementById("days");
const goalInput = document.getElementById("goal");
const languageInput = document.getElementById("language");

const contentOverview = document.getElementById("content-overview");
const contentConcepts = document.getElementById("content-concepts");
const contentFormulas = document.getElementById("content-formulas");
const contentExample = document.getElementById("content-example");
const contentDemo = document.getElementById("content-demo");
const contentGallery = document.getElementById("content-gallery");

const onboardingScript = [
  "Oi! Sou seu assistente de estudos. Qual é o seu nome?",
  "Quanto tempo você consegue estudar por dia? (ex: 1.5)",
  "Quantos dias você quer planejar agora? (ex: 7)",
  "Qual é o seu objetivo principal? (ENEM, vestibular, reforço)",
];

// Traduz valores que podem vir em inglês do backend (ex.: dificuldade, origem da questão)
const DIFFICULTY_LABELS = {
  easy: "Fácil",
  beginner: "Fácil",
  medium: "Médio",
  intermediate: "Médio",
  hard: "Difícil",
  advanced: "Difícil",
  facil: "Fácil",
  medio: "Médio",
  dificil: "Difícil",
};

const QUIZ_SOURCE_LABELS = {
  ia: "Gerado por IA",
  ai: "Gerado por IA",
  online: "Banco online (genérico)",
  offline: "Banco local do tópico",
  cache: "Banco de questões",
  fallback: "Perguntas padrão",
  static: "Perguntas padrão",
};

function translateLabel(map, value, fallbackPrefix = "") {
  if (!value) return "";
  const key = String(value).trim().toLowerCase();
  if (map[key]) return map[key];
  // Se já vier em português (ou valor desconhecido), mantém o texto original com a primeira letra maiúscula
  const text = String(value);
  return fallbackPrefix + text.charAt(0).toUpperCase() + text.slice(1);
}

function normalizeText(text) {
  return text.trim();
}

function getParams() {
  return {
    hours: parseFloat(hoursInput?.value || 2),
    days: parseInt(daysInput?.value || 7, 10),
    goal: goalInput?.value || "ENEM",
    language: languageInput?.value || "pt",
  };
}

function addChatBubble(text, who = "bot") {
  if (!chatBox) return;
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${who}`;
  bubble.textContent = text;
  chatBox.appendChild(bubble);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function loadProfile() {
  try {
    const response = await fetch("/api/profile");
    if (!response.ok) throw new Error(`status ${response.status}`);
    const data = await response.json();
    if (nameInput) nameInput.value = data.name || "Aluno";
    if (hoursInput) hoursInput.value = data.hours || 2;
    if (daysInput) daysInput.value = data.days || 7;
    if (goalInput) goalInput.value = data.goal || "ENEM";
    if (languageInput) languageInput.value = data.language || "pt";

    if (!data.is_new) {
      state.onboardingStep = onboardingScript.length;
      state.userName = data.name;
    }
  } catch (error) {
    console.error("Erro ao carregar perfil:", error);
  }
}

async function saveProfile() {
  try {
    const { hours, days, goal, language } = getParams();
    const response = await fetch("/api/onboarding", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: nameInput?.value || "Aluno",
        hours,
        days,
        goal,
        language,
      }),
    });
    if (!response.ok) throw new Error(`status ${response.status}`);
  } catch (error) {
    console.error("Erro ao salvar perfil:", error);
    addChatBubble("Não consegui salvar seu perfil agora. Tente novamente em instantes.");
  }
}

async function loadStats() {
  try {
    const response = await fetch("/api/stats");
    if (!response.ok) throw new Error(`status ${response.status}`);
    const data = await response.json();
    state.stats = data;
    if (xpTotal) xpTotal.textContent = data.xp;
    if (streak) streak.textContent = `${data.streak} dias`;
  } catch (error) {
    console.error("Erro ao carregar estatísticas:", error);
    if (streak) streak.textContent = "--";
  }
}

async function loadDailyPlan() {
  try {
    const { hours, days } = getParams();
    const response = await fetch(`/api/daily-plan?hours=${hours}&days=${days}`);
    if (!response.ok) throw new Error(`status ${response.status}`);
    const data = await response.json();
    state.days = data.days || [];
    if (summary) {
      summary.textContent = `${data.summary.completed}/${data.summary.total} dias`;
    }
    renderDays();
    if (state.days.length) {
      selectDay(state.selected ?? 0);
    }
  } catch (error) {
    console.error("Erro ao carregar plano diário:", error);
    if (summary) summary.textContent = "Não foi possível carregar seu plano.";
  }
}

function renderDays() {
  if (!daysGrid) return;
  daysGrid.innerHTML = "";
  const fragment = document.createDocumentFragment();
  state.days.forEach((day, index) => {
    const pill = document.createElement("button");
    pill.className = "day-pill";
    if (day.completed) pill.classList.add("completed");
    if (state.selected === index) pill.classList.add("active");

    pill.innerHTML = `<span>${day.label}</span>${day.topic}`;
    pill.addEventListener("click", () => selectDay(index));
    fragment.appendChild(pill);
  });
  daysGrid.appendChild(fragment);
}

function selectDay(index) {
  state.selected = index;
  const day = state.days[index];
  if (!day) return;
  state.topic = day.topic;
  state.selectedDate = day.date;
  if (dayLabel) dayLabel.textContent = `Dia ${day.label} • ${day.topic}`;
  if (dayDifficulty) {
    dayDifficulty.textContent = `Nível: ${translateLabel(DIFFICULTY_LABELS, day.difficulty)}`;
  }
  if (page === "content" || page === "subject") {
    loadDayContent(day.date);
  }
  renderResources(day.resources || []);
  renderDays();
}

function renderResources(resources) {
  if (!resourceList) return;
  resourceList.innerHTML = "";
  if (!resources.length) {
    resourceList.innerHTML = `<p class="muted">Sem recomendações extras hoje.</p>`;
    return;
  }
  const fragment = document.createDocumentFragment();
  resources.forEach((item) => {
    const card = document.createElement("div");
    card.className = "resource-card";
    const type = item.type ? item.type.toUpperCase() : "RECURSO";
    card.innerHTML = `
      <p>${type} • ${item.source || ""}</p>
      <a href="${item.url}" target="_blank" rel="noreferrer">${item.title}</a>
    `;
    fragment.appendChild(card);
  });
  resourceList.appendChild(fragment);
}

async function markDayComplete() {
  const day = state.days[state.selected];
  if (!day) return;
  try {
    const response = await fetch("/api/complete-day", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ date: day.date }),
    });
    if (!response.ok) throw new Error(`status ${response.status}`);
    await Promise.all([loadDailyPlan(), loadStats()]);
  } catch (error) {
    console.error("Erro ao concluir o dia:", error);
    addChatBubble("Não consegui marcar o dia como concluído. Tente novamente.");
  }
}

async function openQuiz() {
  if (!quizArea) return;
  quizArea.innerHTML = `<p class="muted">Carregando perguntas...</p>`;
  try {
    const { hours, days, language } = getParams();
    const day = state.days[state.selected] || state.days[0];
    const response = await fetch(
      `/api/quiz?hours=${hours}&days=${days}&topic=${encodeURIComponent(
        state.topic
      )}&language=${language}${day ? `&date=${encodeURIComponent(day.date)}` : ""}`
    );
    if (!response.ok) throw new Error(`status ${response.status}`);
    const data = await response.json();
    if (quizSource) {
      quizSource.textContent = translateLabel(QUIZ_SOURCE_LABELS, data.source);
    }
    if (quizInfo) {
      quizInfo.textContent = `Tópico: ${data.topic || state.topic} • Nível ${Math.round(
        (data.proficiency || 0) * 100
      )}%`;
    }
    state.quiz = data.questions || [];
    renderQuiz();
  } catch (error) {
    console.error("Erro ao carregar o quiz:", error);
    quizArea.innerHTML = `<p class="muted">Não foi possível carregar as perguntas agora. Tente novamente.</p>`;
  }
}

function renderQuiz() {
  if (!quizArea) return;
  quizArea.innerHTML = "";
  if (!state.quiz.length) {
    quizArea.innerHTML = `<p class="muted">Nenhuma pergunta disponível.</p>`;
    return;
  }

  const fragment = document.createDocumentFragment();
  state.quiz.forEach((question, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "quiz-question";
    wrapper.innerHTML = `<h4>Questão ${index + 1}</h4><p>${question.prompt}</p>`;

    const options = document.createElement("div");
    options.className = "quiz-options";

    question.options.forEach((option) => {
      const btn = document.createElement("button");
      btn.textContent = option;
      btn.addEventListener("click", () => {
        evaluateAnswer(btn, question, option);
      });
      options.appendChild(btn);
    });

    wrapper.appendChild(options);
    fragment.appendChild(wrapper);
  });
  quizArea.appendChild(fragment);
}

async function evaluateAnswer(button, question, selected) {
  if (button.dataset.locked) return;

  const buttons = button.parentElement.querySelectorAll("button");
  buttons.forEach((btn) => (btn.disabled = true));

  try {
    const day = state.days[state.selected];
    const response = await fetch("/api/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: question.prompt,
        selected,
        correct: question.correct,
        topic: state.topic,
        day: day ? day.date : undefined,
      }),
    });
    if (!response.ok) throw new Error(`status ${response.status}`);
    const data = await response.json();

    buttons.forEach((btn) => {
      btn.dataset.locked = "true";
      btn.disabled = false;
      if (btn.textContent === question.correct) {
        btn.classList.add("correct");
      } else if (btn.textContent === selected && !data.correct) {
        btn.classList.add("wrong");
      }
    });
  } catch (error) {
    console.error("Erro ao enviar resposta:", error);
    buttons.forEach((btn) => (btn.disabled = false));
    addChatBubble("Não consegui registrar sua resposta. Tente novamente.");
  }
}

async function handleChat() {
  if (!chatInput) return;
  const text = normalizeText(chatInput.value);
  if (!text) return;
  addChatBubble(text, "user");
  chatInput.value = "";

  // Fase de onboarding
  if (state.onboardingStep < onboardingScript.length) {
    if (state.onboardingStep === 0 && nameInput) {
      nameInput.value = text;
    } else if (state.onboardingStep === 1 && hoursInput) {
      hoursInput.value = text;
    } else if (state.onboardingStep === 2 && daysInput) {
      daysInput.value = text;
    } else if (state.onboardingStep === 3 && goalInput) {
      goalInput.value = text;
    }

    state.onboardingStep += 1;
    if (state.onboardingStep < onboardingScript.length) {
      addChatBubble(onboardingScript[state.onboardingStep]);
    } else {
      addChatBubble("Perfeito! Vou ajustar sua trilha agora.");
      await saveProfile();
      await loadDailyPlan();
      await loadStats();
    }
  } else {
    // Fase de chat com IA (depois do onboarding)
    const chatSendButton = document.getElementById("chat-send");
    if (chatSendButton) chatSendButton.disabled = true;
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      if (response.ok) {
        const data = await response.json();
        addChatBubble(data.response || "Desculpe, não consegui gerar uma resposta.");
      } else {
        addChatBubble("Erro ao conectar com o assistente. Tente novamente.");
      }
    } catch (error) {
      addChatBubble("Erro de conexão. Verifique sua internet e tente novamente.");
    } finally {
      if (chatSendButton) chatSendButton.disabled = false;
    }
  }
}

function initChat() {
  if (!chatBox) return;
  if (state.onboardingStep >= onboardingScript.length) {
    addChatBubble(
      `Bem-vindo de volta, ${state.userName || "Aluno"}! Como posso ajudar com seus estudos de Física hoje?`
    );
  } else {
    addChatBubble(onboardingScript[0]);
  }
}

async function loadDayContent(dateStr) {
  if (contentOverview) contentOverview.textContent = "Carregando conteúdo...";
  try {
    const { hours } = getParams();
    const response = await fetch(`/api/day-content?date=${dateStr}&hours=${hours}`);
    if (!response.ok) throw new Error(`status ${response.status}`);
    const data = await response.json();
    if (!data.topicContent) return;

    const content = data.topicContent;
    if (contentOverview) contentOverview.textContent = content.overview;
    const topicMeta = document.getElementById("content-topic-meta");
    if (topicMeta) {
      const baseTopic = data.baseTopic || state.topic;
      topicMeta.textContent = `${data.topic || state.topic} • ${baseTopic}`;
    }

    if (contentConcepts) {
      contentConcepts.innerHTML = "";
      (content.concepts || []).forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        contentConcepts.appendChild(li);
      });
    }

    if (contentFormulas) {
      contentFormulas.innerHTML = "";
      (content.formulas || []).forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        contentFormulas.appendChild(li);
      });
    }

    if (contentExample) contentExample.textContent = content.example;
    if (contentDemo) contentDemo.textContent = content.demo;

    const contentPractice = document.getElementById("content-practice");
    if (contentPractice) {
      contentPractice.innerHTML = "";
      (content.practice || []).forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        contentPractice.appendChild(li);
      });
    }

    const contentMistakes = document.getElementById("content-mistakes");
    if (contentMistakes) {
      contentMistakes.innerHTML = "";
      (content.common_mistakes || []).forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        contentMistakes.appendChild(li);
      });
    }

    const contentExamTips = document.getElementById("content-exam-tips");
    if (contentExamTips) {
      contentExamTips.innerHTML = "";
      (content.exam_tips || []).forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        contentExamTips.appendChild(li);
      });
    }

    if (contentGallery) {
      contentGallery.innerHTML = "";
      (content.images || []).forEach((img) => {
        const card = document.createElement("div");
        card.className = "gallery-item";
        card.innerHTML = `<img src="${img.src}" alt="${img.caption}" />
          <p>${img.caption}</p>`;
        contentGallery.appendChild(card);
      });
    }
  } catch (error) {
    console.error("Erro ao carregar conteúdo do dia:", error);
    if (contentOverview) {
      contentOverview.textContent = "Não foi possível carregar o conteúdo deste dia.";
    }
  }
}

const refreshButton = document.getElementById("refresh");
if (refreshButton) {
  refreshButton.addEventListener("click", async () => {
    await saveProfile();
    loadDailyPlan();
  });
}

const completeButton = document.getElementById("complete-day");
if (completeButton) {
  completeButton.addEventListener("click", markDayComplete);
}

const openQuizButton = document.getElementById("open-quiz");
if (openQuizButton) {
  openQuizButton.addEventListener("click", openQuiz);
}

const startDayButton = document.getElementById("start-day");
if (startDayButton) {
  startDayButton.addEventListener("click", () => selectDay(0));
}

const chatSendButton = document.getElementById("chat-send");
if (chatSendButton) {
  chatSendButton.addEventListener("click", handleChat);
}
if (chatInput) {
  chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      handleChat();
    }
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  await loadProfile();
  await Promise.all([loadDailyPlan(), loadStats()]);
  initChat();
  if (page === "quiz") {
    openQuiz();
  } else if (page === "subject") {
    selectDay(0);
  }
});