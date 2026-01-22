document.getElementById("btn").onclick = async () => {
  const q = document.getElementById("q").value;
  const res = await fetch("/qa", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({question: q})
  });
  const j = await res.json();
  let out = '';
  if (j.error) {
    out = 'Error: ' + j.error;
  } else {
    out += 'RAG Answer:\n' + j.rag_answer + '\n\n';
    out += 'Baseline Answer:\n' + j.baseline_answer + '\n\n';
    out += 'Sources:\n';
    (j.sources||[]).forEach((s, i) => {
      out += `${i+1}. ${s.id || s.filename || 'source'} (score: ${s.score || 0})\n`;
      out += (s.text||'').substring(0,200).replace(/\n/g,' ') + '\n\n';
    });
    out += 'Timings (ms): ' + JSON.stringify(j.timings);
  }
  document.getElementById("out").textContent = out;
};
