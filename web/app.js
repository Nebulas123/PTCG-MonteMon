const deckText = document.querySelector("#deckText");
const targetText = document.querySelector("#targetText");
const targetName = document.querySelector("#targetName");
const requiredRows = document.querySelector("#requiredRows");
const anyRows = document.querySelector("#anyRows");
const runBtn = document.querySelector("#runBtn");
const syncJsonBtn = document.querySelector("#syncJsonBtn");
const addRequiredBtn = document.querySelector("#addRequiredBtn");
const addAnyBtn = document.querySelector("#addAnyBtn");
const fixedSeed = document.querySelector("#fixedSeed");
const seedInput = document.querySelector("#seed");
const loadDeckBtn = document.querySelector("#loadDeckBtn");
const loadT2TargetBtn = document.querySelector("#loadT2TargetBtn");
const loadOpeningTargetBtn = document.querySelector("#loadOpeningTargetBtn");
const statusEl = document.querySelector("#status");
const resultsEl = document.querySelector("#results");

const zones = [
  ["hand", "手牌"],
  ["active", "战斗场"],
  ["bench", "备战区"],
  ["prizes", "奖赏卡"],
  ["discard", "弃牌区"],
  ["stadium", "竞技场"],
  ["deck", "牌库"],
];

const defaultDeck = `Pokémon: 21
4 Archeops SIT 147
3 Lugia V SIT 138
3 Lugia VSTAR SIT 139
2 Minccino TEF 136
2 Cinccino TEF 137
2 Lumineon V BRS 40
1 Squawkabilly ex PAL 169
1 Iron Bundle PAR 56
1 Bloodmoon Ursaluna ex TWM 141
1 Iron Hands ex PAR 70
1 Fezandipiti ex SFA 38

Trainer: 23
3 Boss's Orders PAL 172
2 Professor's Research SVI 189
2 Iono PAL 185
1 Roseanne's Backup BRS 148
1 Jacq SVI 175
1 Thorton LOR 167
1 Carmine TWM 145
4 Ultra Ball SVI 196
4 Capturing Aroma SIT 153
2 Great Ball PAL 183
2 Mesagoza SVI 178

Energy: 16
4 Jet Energy PAL 190
4 Mist Energy TEF 161
3 Gift Energy LOR 171
2 Double Turbo Energy BRS 151
2 V Guard Energy SIT 169
1 Legacy Energy TWM 167`;

deckText.value = defaultDeck;
loadT2Target();

addRequiredBtn.addEventListener("click", () => {
  addCondition(requiredRows, "hand", "", 1);
  syncFormToJson();
});

addAnyBtn.addEventListener("click", () => {
  addCondition(anyRows, "active", "", 1);
  syncFormToJson();
});

syncJsonBtn.addEventListener("click", syncJsonToForm);
runBtn.addEventListener("click", runSimulation);
targetName.addEventListener("input", syncFormToJson);
loadDeckBtn.addEventListener("click", () => {
  deckText.value = defaultDeck;
  statusEl.className = "status";
  statusEl.textContent = "已恢复 Lugia 卡组";
});
loadT2TargetBtn.addEventListener("click", loadT2Target);
loadOpeningTargetBtn.addEventListener("click", loadOpeningTarget);
fixedSeed.addEventListener("change", () => {
  seedInput.disabled = !fixedSeed.checked;
  if (fixedSeed.checked && !seedInput.value) {
    seedInput.value = "42";
  }
});

function loadT2Target() {
  document.querySelector("#mode").value = "two-turn";
  targetName.value = "T2 Lugia VSTAR in play, 2 Archeops discarded";
  requiredRows.innerHTML = "";
  anyRows.innerHTML = "";
  addCondition(requiredRows, "discard", "Archeops", 2);
  addCondition(anyRows, "active", "Lugia VSTAR", 1);
  addCondition(anyRows, "bench", "Lugia VSTAR", 1);
  syncFormToJson();
  statusEl.className = "status";
  statusEl.textContent = "已载入默认 T2 目标";
}

function loadOpeningTarget() {
  document.querySelector("#mode").value = "opening-hand";
  targetName.value = "Opening hand contains Lugia V";
  requiredRows.innerHTML = "";
  anyRows.innerHTML = "";
  addCondition(requiredRows, "hand", "Lugia V", 1);
  syncFormToJson();
  statusEl.className = "status";
  statusEl.textContent = "已载入起手 Lugia V 目标";
}

function addCondition(container, zone = "hand", card = "", count = 1) {
  const row = document.createElement("div");
  row.className = "condition-row";
  row.innerHTML = `
    <label>
      区域
      <select class="zone-input">
        ${zones.map(([value, label]) => `<option value="${value}">${label}</option>`).join("")}
      </select>
    </label>
    <label>
      卡名
      <input class="card-input" placeholder="Lugia V" />
    </label>
    <label>
      数量
      <input class="count-input" type="number" min="1" value="1" />
    </label>
    <button class="icon-button" type="button" title="删除">×</button>
  `;
  row.querySelector(".zone-input").value = zone;
  row.querySelector(".card-input").value = card;
  row.querySelector(".count-input").value = count;
  row.querySelector(".icon-button").addEventListener("click", () => {
    row.remove();
    syncFormToJson();
  });
  row.querySelectorAll("input, select").forEach((input) => input.addEventListener("input", syncFormToJson));
  container.appendChild(row);
}

function syncFormToJson() {
  const target = {
    name: targetName.value || "Custom target",
    zones: collectRequired(),
  };
  const anyOf = collectAnyOf();
  if (anyOf.length) {
    target.any_of = anyOf;
  }
  targetText.value = JSON.stringify(target, null, 2);
}

function syncJsonToForm() {
  try {
    const parsed = JSON.parse(targetText.value);
    targetName.value = parsed.name || "Custom target";
    requiredRows.innerHTML = "";
    anyRows.innerHTML = "";

    for (const [zone, cards] of Object.entries(parsed.zones || {})) {
      for (const [card, count] of Object.entries(cards)) {
        addCondition(requiredRows, zone, card, count);
      }
    }

    for (const group of parsed.any_of || []) {
      for (const [zone, cards] of Object.entries(group)) {
        for (const [card, count] of Object.entries(cards)) {
          addCondition(anyRows, zone, card, count);
        }
      }
    }
    syncFormToJson();
    statusEl.className = "status";
    statusEl.textContent = "JSON 已同步到表单";
  } catch (error) {
    statusEl.className = "status error";
    statusEl.textContent = `JSON 无法同步：${error.message}`;
  }
}

function collectRequired() {
  return collectRows(requiredRows);
}

function collectAnyOf() {
  return [...anyRows.querySelectorAll(".condition-row")]
    .map(rowToRequirement)
    .filter(Boolean)
    .map(({ zone, card, count }) => ({ [zone]: { [card]: count } }));
}

function collectRows(container) {
  const output = {};
  [...container.querySelectorAll(".condition-row")]
    .map(rowToRequirement)
    .filter(Boolean)
    .forEach(({ zone, card, count }) => {
      output[zone] ||= {};
      output[zone][card] = (output[zone][card] || 0) + count;
    });
  return output;
}

function rowToRequirement(row) {
  const zone = row.querySelector(".zone-input").value;
  const card = row.querySelector(".card-input").value.trim();
  const count = Number(row.querySelector(".count-input").value);
  if (!card || !Number.isFinite(count) || count < 1) {
    return null;
  }
  return { zone, card, count };
}

async function runSimulation() {
  syncFormToJson();
  statusEl.className = "status";
  statusEl.textContent = "运行中...";
  resultsEl.innerHTML = "";
  runBtn.disabled = true;

  try {
    JSON.parse(targetText.value);
    const response = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        deck: deckText.value,
        target: targetText.value,
        trials: Number(document.querySelector("#trials").value),
        seed: fixedSeed.checked ? seedInput.value : "",
        mode: document.querySelector("#mode").value,
        going: document.querySelector("#going").value,
        opponent_turn1_disruption: document.querySelector("#opp1").value,
        opponent_turn2_disruption: document.querySelector("#opp2").value,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "运行失败");
    }
    renderResults(payload);
    statusEl.textContent = `完成：${payload.target}`;
  } catch (error) {
    statusEl.className = "status error";
    statusEl.textContent = error.message;
  } finally {
    runBtn.disabled = false;
  }
}

function renderResults(payload) {
  resultsEl.innerHTML = "";
  for (const result of payload.results) {
    const card = document.createElement("article");
    card.className = "result-card";
    card.innerHTML = `
      <h3>${result.going === "first" ? "先手" : "后手"}</h3>
      <div class="metric">
        <div><strong>${(result.probability * 100).toFixed(2)}%</strong>概率</div>
        <div><strong>${result.successes}</strong>成功</div>
        <div><strong>${result.trials}</strong>样本</div>
      </div>
      <p>平均 mulligan：${result.average_mulligans.toFixed(3)}</p>
    `;

    result.routes.forEach((route, index) => {
      const details = document.createElement("details");
      details.open = index === 0;
      details.innerHTML = `<summary>成功路线 ${index + 1}</summary>`;
      const list = document.createElement("ol");
      route.forEach((step) => {
        const item = document.createElement("li");
        item.textContent = step;
        list.appendChild(item);
      });
      details.appendChild(list);
      card.appendChild(details);
    });

    if (!result.routes.length) {
      const empty = document.createElement("p");
      empty.textContent = "当前样本没有成功路线。";
      card.appendChild(empty);
    }

    resultsEl.appendChild(card);
  }
}
