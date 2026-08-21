/* Claim Audit Lab — sealed-trace replay.
 *
 * This is NOT a simulation and NOT live inference. It replays audit traces
 * exactly as CAL recorded them during the 2026-08-02 chunk-granularity probe,
 * side by side across the two passage-unit arms. Every score, rule id and
 * verdict below was read out of a sealed trace file by
 * scripts/gen_docs_traces.py — see assets/traces.js.
 */
(function () {
  "use strict";

  var D = window.CAL_TRACES;
  if (!D) return;

  var FLOOR = D.summary.retrievalFloor;
  var SUPPORTED = D.summary.supportedThreshold;

  var $ = function (sel, root) { return (root || document).querySelector(sel); };

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function verdictPill(v) {
    var cls = { supported: "supported", not_checkable: "notcheckable",
                contradicted: "contradicted", partially_supported: "partial" }[v] || "info";
    return '<span class="pill ' + cls + '">' + esc(v) + "</span>";
  }

  /* Retrieval bars, scaled so the 0.40 floor sits at a readable position. */
  function retrievalBlock(arm) {
    var max = Math.max(1.0, arm.retrieval.length ? arm.retrieval[0].score : 1.0);
    var rows = arm.retrieval.slice(0, 5).map(function (r) {
      var pct = Math.max(2, (r.score / max) * 100);
      var over = r.score >= FLOOR;
      var shortPid = r.pid.split("#")[1] || r.pid;
      return '' +
        '<div class="bar-row">' +
          '<span class="pid" title="' + esc(r.pid) + '">' + esc(shortPid) + "</span>" +
          '<span class="bar-track">' +
            '<span class="bar-fill' + (over ? " over" : "") + '" style="width:' + pct.toFixed(1) + '%"></span>' +
            '<span class="floor-mark" style="left:' + ((FLOOR / max) * 100).toFixed(1) + '%" title="retrieval floor ' + FLOOR + '"></span>' +
          "</span>" +
          '<span class="sc">' + r.score.toFixed(3) + "</span>" +
        "</div>";
    }).join("");

    var anyOver = arm.retrieval.some(function (r) { return r.score >= FLOOR; });
    return '' +
      '<div class="step">' +
        '<div class="step-lbl">1 · Retrieve &middot; ' + arm.nPassages + " passages indexed</div>" +
        rows +
        '<div class="legend">red line = retrieval floor ' + FLOOR.toFixed(2) +
          " &middot; " + (anyOver ? "candidates admitted" : "<strong>nothing clears the floor</strong>") +
        "</div>" +
      "</div>";
  }

  function entailBlock(arm) {
    var reached = arm.retrieval.some(function (r) { return r.score >= FLOOR; });
    if (!reached) {
      return '' +
        '<div class="step">' +
          '<div class="step-lbl">2 · Entail</div>' +
          '<div class="faint">Never runs — the retrieval layer admitted no passage, ' +
          "so the NLI head is given nothing to read.</div>" +
        "</div>";
    }
    var pct = (arm.entail * 100).toFixed(1);
    var isEntail = arm.signal === "entail";
    return '' +
      '<div class="step">' +
        '<div class="step-lbl">2 · Entail &middot; DeBERTa-v3 NLI</div>' +
        '<div class="bar-row">' +
          '<span class="pid">' + esc(arm.signal) + "</span>" +
          '<span class="bar-track">' +
            '<span class="bar-fill' + (isEntail ? " over" : "") + '" style="width:' + pct + '%"></span>' +
          "</span>" +
          '<span class="sc">' + arm.entail.toFixed(3) + "</span>" +
        "</div>" +
        '<div class="legend">' +
          (isEntail
            ? "entailment &ge; supported_threshold " + SUPPORTED.toFixed(2)
            : "<strong>neutral</strong> — the passage takes no position on the claim") +
        "</div>" +
      "</div>";
  }

  function rulesBlock(arm) {
    var chips = arm.rules.map(function (r) {
      return '<span class="rule-chip">' + esc(r) + "</span>";
    }).join(" ");
    return '' +
      '<div class="step">' +
        '<div class="step-lbl">3 · Rules &middot; deterministic</div>' +
        '<div class="verdict-line">' +
          verdictPill(arm.verdict) +
          (chips || '<span class="faint">no rule fired</span>') +
          (arm.reason ? '<span class="faint" style="margin-left:auto">' + esc(arm.reason) + "</span>" : "") +
        "</div>" +
      "</div>";
  }

  function armPanel(title, unit, arm) {
    return '' +
      '<div class="arm">' +
        '<div class="arm-head"><strong>' + esc(title) + "</strong>" +
          '<span class="unit">' + esc(unit) + "</span></div>" +
        '<div class="arm-body">' +
          retrievalBlock(arm) + entailBlock(arm) + rulesBlock(arm) +
        "</div>" +
      "</div>";
  }

  function render(idx) {
    var c = D.cases[idx];
    if (!c) return;

    $("#demo-claim").innerHTML =
      '<div class="lbl">Claim under audit &middot; ' + esc(c.doc) + " &middot; authored relationship: " + esc(c.rel) + "</div>" +
      '<div class="txt">' + esc(c.claim) + "</div>";

    $("#demo-arms").innerHTML =
      armPanel("Section chunking", "7 passages/doc — shipped baseline", c.section) +
      armPanel("Clause chunking", "20 passages/doc — probe arm", c.fine);

    var note;
    if (c.rescued) {
      var secTop = c.section.retrieval[0].score;
      var fineTop = c.fine.retrieval[0].score;
      note = "<strong>Rescued by the unit change.</strong> The supporting text was in the " +
        "pool the whole time. As part of a section it scored " + secTop.toFixed(3) +
        " and fell under the " + FLOOR.toFixed(2) + " floor; as its own clause it scores " +
        fineTop.toFixed(3) + " and the verdict flips to <code>supported</code>. " +
        "This is a <em>retrieval-layer</em> failure and finer units fix it outright.";
    } else {
      note = "<strong>Not rescued.</strong> In the clause arm the premise retrieved at " +
        c.fine.retrieval[0].score.toFixed(3) + " — comfortably above the floor, isolated and " +
        "distraction-free — and the entailer still returned <code>neutral</code> at " +
        c.fine.entail.toFixed(3) + ". This is an <em>entailment-layer</em> failure. " +
        "Better allocation does not touch it.";
    }
    $("#demo-note").innerHTML = note;
  }

  function init() {
    var sel = $("#demo-select");
    if (!sel) return;

    D.cases.forEach(function (c, i) {
      var o = document.createElement("option");
      var tag = c.missKind === "no_evidence" ? "floor miss" : "entailment miss";
      o.value = String(i);
      o.textContent = c.doc + "  —  " + tag + (c.rescued ? "  (rescued)" : "");
      sel.appendChild(o);
    });

    // Open on SOP-MFG-147, the 0.392 -> 0.924 case.
    var start = D.cases.findIndex(function (c) { return c.doc === "SOP-MFG-147"; });
    if (start < 0) start = 0;
    sel.value = String(start);
    render(start);

    sel.addEventListener("change", function () { render(Number(sel.value)); });

    var next = $("#demo-next");
    if (next) {
      next.addEventListener("click", function () {
        var i = (Number(sel.value) + 1) % D.cases.length;
        sel.value = String(i);
        render(i);
      });
    }

    var s = D.summary;
    var sum = $("#demo-summary");
    if (sum) {
      sum.textContent = s.floorRescued + "/" + s.floorTotal + " floor misses rescued · " +
        s.entailRescued + "/" + s.entailTotal + " entailment misses rescued · n=" + s.n;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
