"use strict";

(() => {
  const words = ["robots", "help", "humans", "and", "doctors"];
  const lanes = [[], [], []];
  const bank = document.querySelector("#word-bank");
  const dropzones = [...document.querySelectorAll(".dropzone")];
  const prediction = document.querySelector("#prediction");
  const compare = document.querySelector("#compare");
  const reset = document.querySelector("#reset");
  const status = document.querySelector("#status");
  const reveal = document.querySelector("#reveal");

  const sentence = (lane) => lanes[lane].length ? `${lanes[lane].join(" ")}.` : "Your sentence will appear here.";
  const complete = (lane) => lanes[lane].length === words.length && words.every((word) => lanes[lane].includes(word));
  const allComplete = () => lanes.every((_, laneIndex) => complete(laneIndex));
  const allDifferent = () => new Set(lanes.map((lane) => lane.join(" "))).size === lanes.length;

  function setStatus(message) {
    status.textContent = message;
  }

  function clearDropMarkers() {
    dropzones.forEach((zone) => {
      const marker = zone.querySelector?.(".drop-marker");
      if (marker) marker.remove();
      delete zone.dataset.dropIndex;
    });
  }

  function render() {
    clearDropMarkers();
    dropzones.forEach((zone, laneIndex) => {
      zone.innerHTML = lanes[laneIndex].length
        ? lanes[laneIndex].map((word, wordIndex) => `<button class="word-chip" draggable="true" data-word="${word}" data-index="${wordIndex}" aria-label="${word}, drag to reorder">${word}</button>`).join("")
        : '<span class="drop-hint">Drop words here</span>';
      zone.querySelectorAll(".word-chip").forEach((chip) => {
        chip.addEventListener("dragstart", dragStart);
        chip.addEventListener("dragend", dragEnd);
      });
      const line = document.querySelector(`#sentence-${laneIndex}`);
      line.textContent = sentence(laneIndex);
      line.classList.toggle("empty", !lanes[laneIndex].length);
    });

    const ready = allComplete() && allDifferent() && prediction.value;
    compare.disabled = !ready;
    const placedCount = lanes[0].length;
    if (!allComplete()) setStatus(placedCount ? `Drag ${words.length - placedCount} more word${words.length - placedCount === 1 ? "" : "s"} into any lane.` : "Drag a word into any lane. It will appear in all three lanes.");
    else if (!allDifferent()) setStatus("Reorder the chips in each lane so the sentences differ.");
    else if (!prediction.value) setStatus("Make your prediction before comparing.");
    else setStatus("Ready. Compare the three representations.");
  }

  function addWordToAll(word, targetIndex) {
    if (!words.includes(word)) return;
    lanes.forEach((lane) => {
      if (!lane.includes(word)) lane.splice(Math.min(targetIndex, lane.length), 0, word);
    });
    reveal.hidden = true;
    render();
  }

  function moveWord(laneIndex, fromIndex, toIndex) {
    if (fromIndex === toIndex || fromIndex < 0 || toIndex < 0) return;
    const [word] = lanes[laneIndex].splice(fromIndex, 1);
    lanes[laneIndex].splice(Math.min(toIndex, lanes[laneIndex].length), 0, word);
    reveal.hidden = true;
    render();
  }

  function sourceChip(zone, sourceIndex) {
    return [...zone.querySelectorAll(".word-chip")].find((chip) => chip.dataset.index === sourceIndex);
  }

  function insertionIndex(zone, event, draggedChip) {
    const chips = [...zone.querySelectorAll(".word-chip")].filter((chip) => chip !== draggedChip);
    for (const [index, chip] of chips.entries()) {
      const rect = chip.getBoundingClientRect?.();
      if (!rect) {
        if (event.target?.closest?.(".word-chip") === chip) return index;
        continue;
      }
      const beforeRow = event.clientY < rect.top + rect.height / 2;
      const sameRow = event.clientY >= rect.top && event.clientY <= rect.bottom;
      const beforeChip = event.clientX < rect.left + rect.width / 2;
      if (beforeRow || (sameRow && beforeChip)) return index;
    }
    return chips.length;
  }

  function showDropMarker(zone, index) {
    const marker = document.createElement("span");
    marker.className = "drop-marker";
    marker.setAttribute("aria-hidden", "true");
    const chips = [...zone.querySelectorAll(".word-chip")];
    zone.insertBefore(marker, chips[index] || null);
    zone.dataset.dropIndex = String(index);
  }

  function dragStart(event) {
    const chip = event.currentTarget;
    chip.classList.add("dragging");
    event.dataTransfer.effectAllowed = "copyMove";
    event.dataTransfer.setData("text/plain", chip.dataset.word);
    if (chip.classList.contains("word-chip")) {
      event.dataTransfer.setData("application/x-lane", chip.closest(".dropzone").dataset.laneTarget);
      event.dataTransfer.setData("application/x-index", chip.dataset.index);
    } else {
      event.dataTransfer.setData("application/x-bank", "true");
    }
  }

  function dragEnd(event) {
    event.currentTarget.classList.remove("dragging");
    clearDropMarkers();
  }

  bank.querySelectorAll(".bank-word").forEach((tile) => {
    tile.addEventListener("dragstart", dragStart);
    tile.addEventListener("dragend", dragEnd);
  });

  dropzones.forEach((zone) => {
    zone.addEventListener("dragover", (event) => {
      event.preventDefault();
      const laneIndex = Number(zone.dataset.laneTarget);
      const sourceLane = event.dataTransfer.getData("application/x-lane");
      const isBankDrag = event.dataTransfer.getData("application/x-bank") === "true";
      if (!isBankDrag && sourceLane !== String(laneIndex)) return;
      event.dataTransfer.dropEffect = isBankDrag ? "copy" : "move";
      clearDropMarkers();
      showDropMarker(zone, insertionIndex(zone, event, sourceChip(zone, event.dataTransfer.getData("application/x-index"))));
      zone.classList.add("over");
    });
    zone.addEventListener("dragleave", (event) => {
      if (!zone.contains(event.relatedTarget)) {
        zone.classList.remove("over");
        clearDropMarkers();
      }
    });
    zone.addEventListener("drop", (event) => {
      event.preventDefault();
      const laneIndex = Number(zone.dataset.laneTarget);
      const sourceLane = event.dataTransfer.getData("application/x-lane");
      const sourceIndex = event.dataTransfer.getData("application/x-index");
      const isBankDrag = event.dataTransfer.getData("application/x-bank") === "true";
      const draggedChip = sourceLane === String(laneIndex) ? sourceChip(zone, sourceIndex) : null;
      const targetIndex = zone.dataset.dropIndex === undefined
        ? insertionIndex(zone, event, draggedChip)
        : Number(zone.dataset.dropIndex);
      zone.classList.remove("over");
      clearDropMarkers();

      if (sourceLane !== "" && sourceLane === String(laneIndex)) {
        moveWord(laneIndex, Number(sourceIndex), targetIndex);
        return;
      }

      if (isBankDrag) addWordToAll(event.dataTransfer.getData("text/plain"), targetIndex);
    });
  });

  prediction.addEventListener("change", render);

  compare.addEventListener("click", () => {
    const vocabulary = [...words].sort();
    const predictionText = prediction.value === "same"
      ? "Your prediction was right: every row has the same counts."
      : prediction.value === "different"
        ? "The vectors match, even though the sentences do not."
        : "The three rows below make the answer visible: the vectors match.";
    document.querySelector("#prediction-result").textContent = predictionText;
    document.querySelector("#sentence-stack").innerHTML = lanes.map((lane, index) =>
      `<div class="revealed-sentence revealed-${String.fromCharCode(97 + index)}"><span class="sentence-label">Sentence ${String.fromCharCode(65 + index)}</span><span>${sentence(index)}</span></div>`
    ).join("");
    document.querySelector("#vector-table").innerHTML = `<table class="vector-table"><thead><tr><th>sentence</th>${vocabulary.map((word) => `<th>${word}</th>`).join("")}</tr></thead><tbody>${lanes.map((lane, index) => `<tr class="row-${String.fromCharCode(97 + index)}"><td>Sentence ${String.fromCharCode(65 + index)}</td>${vocabulary.map(() => "<td>1</td>").join("")}</tr>`).join("")}</tbody></table>`;
    reveal.hidden = false;
    reveal.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  reset.addEventListener("click", () => {
    lanes.forEach((lane) => lane.splice(0));
    prediction.value = "";
    reveal.hidden = true;
    render();
  });

  render();
})();
