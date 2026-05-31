const state = {
  days: [],
  selected: null,
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
  "Oi! Sou seu assistente de estudos. Qual seu nome?",
  "Quanto tempo voce consegue estudar por dia? (ex: 1.5)",
  "Quantos dias voce quer planejar agora? (ex: 7)",
  "Qual seu objetivo principal? (ENEM, vestibular, reforco)",
];

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
  const response = await fetch("/api/profile");
  const data = await response.json();
  if (nameInput) nameInput.value = data.name || "Aluno";
  if (hoursInput) hoursInput.value = data.hours || 2;
  if (daysInput) daysInput.value = data.days || 7;
  if (goalInput) goalInput.value = data.goal || "ENEM";
  if (languageInput) languageInput.value = data.language || "pt";
}

async function saveProfile() {
  const { hours, days, goal, language } = getParams();
  await fetch("/api/onboarding", {
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
}

async function loadStats() {
  const response = await fetch("/api/stats");
  const data = await response.json();
  state.stats = data;
  if (xpTotal) xpTotal.textContent = data.xp;
  if (streak) streak.textContent = `${data.streak} dias`;
}

async function loadDailyPlan() {
  const { hours, days } = getParams();
  const response = await fetch(`/api/daily-plan?hours=${hours}&days=${days}`);
  const data = await response.json();
  state.days = data.days;
  if (summary) {
    summary.textContent = `${data.summary.completed}/${data.summary.total} dias`;
  }
  renderDays();
  if (state.days.length) {
    selectDay(state.selected ?? 0);
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
  if (dayLabel) dayLabel.textContent = `Dia ${day.label} • ${day.topic}`;
  if (dayDifficulty) dayDifficulty.textContent = `Nivel: ${day.difficulty}`;
  if (page === "content") {
    loadDayContent(day.date);
  }
  renderResources(day.resources || []);
  renderDays();
}

function renderResources(resources) {
  if (!resourceList) return;
  resourceList.innerHTML = "";
  if (!resources.length) {
    resourceList.innerHTML = `<p class="muted">Sem recomendacoes extras hoje.</p>`;
    return;
  }
  const fragment = document.createDocumentFragment();
  resources.forEach((item) => {
    const card = document.createElement("div");
    card.className = "resource-card";
    card.innerHTML = `
      <p>${item.type.toUpperCase()} • ${item.source}</p>
      <a href="${item.url}" target="_blank" rel="noreferrer">${item.title}</a>
    `;
    fragment.appendChild(card);
  });
  resourceList.appendChild(fragment);
}

async function markDayComplete() {
  const day = state.days[state.selected];
  if (!day) return;
  await fetch("/api/complete-day", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ date: day.date }),
  });
  await Promise.all([loadDailyPlan(), loadStats()]);
}

async function openQuiz() {
  const { hours, language } = getParams();
  const response = await fetch(
    `/api/quiz?hours=${hours}&topic=${encodeURIComponent(
      state.topic
    )}&language=${language}`
  );
  const data = await response.json();
  if (quizSource) quizSource.textContent = data.source;
  if (quizInfo) {
    quizInfo.textContent = `Topico: ${data.topic} • Nivel ${Math.round(
      data.proficiency * 100
    )}%`;
  }
  state.quiz = data.questions;
  renderQuiz();
}

function renderQuiz() {
  if (!quizArea) return;
  quizArea.innerHTML = "";
  if (!state.quiz.length) {
    quizArea.innerHTML = `<p class="muted">Nenhuma pergunta disponivel.</p>`;
    return;
  }

  const fragment = document.createDocumentFragment();
  state.quiz.forEach((question, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "quiz-question";
    wrapper.innerHTML = `<h4>Questao ${index + 1}</h4><p>${question.prompt}</p>`;

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
  const data = await response.json();

  const buttons = button.parentElement.querySelectorAll("button");
  buttons.forEach((btn) => {
    btn.dataset.locked = "true";
    if (btn.textContent === question.correct) {
      btn.classList.add("correct");
    } else if (btn.textContent === selected && !data.correct) {
      btn.classList.add("wrong");
    }
  });
}

function handleChat() {
  if (!chatInput) return;
  const text = normalizeText(chatInput.value);
  if (!text) return;
  addChatBubble(text, "user");
  chatInput.value = "";

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
    saveProfile().then(loadDailyPlan).then(loadStats);
  }
}

function initChat() {
  if (!chatBox) return;
  addChatBubble(onboardingScript[0]);
}

async function loadDayContent(dateStr) {
  const { hours } = getParams();
  const response = await fetch(`/api/day-content?date=${dateStr}&hours=${hours}`);
  const data = await response.json();
  if (!data.topicContent) return;

  const content = data.topicContent;
  if (contentOverview) contentOverview.textContent = content.overview;

  if (contentConcepts) {
    contentConcepts.innerHTML = "";
    content.concepts.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      contentConcepts.appendChild(li);
    });
  }

  if (contentFormulas) {
    contentFormulas.innerHTML = "";
    content.formulas.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      contentFormulas.appendChild(li);
    });
  }

  if (contentExample) contentExample.textContent = content.example;
  if (contentDemo) contentDemo.textContent = content.demo;

  if (contentGallery) {
    contentGallery.innerHTML = "";
    content.images.forEach((img) => {
      const card = document.createElement("div");
      card.className = "gallery-item";
      card.innerHTML = `<img src="${img.src}" alt="${img.caption}" />
        <p>${img.caption}</p>`;
      contentGallery.appendChild(card);
    });
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
  }
});
