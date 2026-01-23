// Load documents list on page load
async function loadDocuments() {
  try {
    const res = await fetch('/documents');
    const data = await res.json();
    
    const docsList = document.getElementById('docsList');
    const noDocsMsg = document.getElementById('noDocsMsg');
    
    if (data.success && data.documents && data.documents.length > 0) {
      docsList.innerHTML = data.documents.map(doc => `
        <div class="doc-item">
          <div class="doc-info">
            <div class="doc-name">📄 ${escapeHtml(doc.filename)}</div>
            <div class="doc-meta">
              分割數: ${doc.chunks} | 字數: ${doc.content_length.toLocaleString()}
            </div>
          </div>
          <div class="doc-actions">
            <button onclick="deleteDocument('${doc.filename}')">刪除</button>
          </div>
        </div>
      `).join('');
      noDocsMsg.style.display = 'none';
    } else {
      docsList.innerHTML = '';
      noDocsMsg.style.display = 'block';
    }
  } catch (e) {
    console.error('Failed to load documents:', e);
  }
}

// Handle file upload
document.getElementById('fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  
  const formData = new FormData();
  formData.append('file', file);
  
  const statusDiv = document.getElementById('uploadStatus');
  const fileLabel = document.getElementById('fileLabel');
  
  statusDiv.className = 'status-info';
  statusDiv.textContent = '⏳ 正在上傳並處理文檔...';
  fileLabel.classList.add('uploading');
  
  try {
    const res = await fetch('/upload-doc', {
      method: 'POST',
      body: formData
    });
    const result = await res.json();
    
    if (result.success) {
      statusDiv.className = 'status-success';
      statusDiv.innerHTML = `
        ✅ ${result.message}<br/>
        分割為 ${result.chunks_count} 個片段，生成了 ${result.embeddings_count} 個向量化表示
      `;
      document.getElementById('fileInput').value = '';
      loadDocuments();
    } else {
      statusDiv.className = 'status-error';
      statusDiv.textContent = '❌ ' + (result.message || '上傳失敗');
    }
  } catch (e) {
    statusDiv.className = 'status-error';
    statusDiv.textContent = '❌ 上傳失敗: ' + e.message;
  } finally {
    fileLabel.classList.remove('uploading');
  }
});

// Delete document
async function deleteDocument(filename) {
  if (!confirm(`確定要刪除文檔 "${filename}" 嗎？`)) {
    return;
  }
  
  try {
    const res = await fetch(`/documents/${encodeURIComponent(filename)}`, {
      method: 'DELETE'
    });
    const result = await res.json();
    
    if (result.success) {
      alert('文檔已刪除');
      loadDocuments();
    } else {
      alert('刪除失敗: ' + result.message);
    }
  } catch (e) {
    alert('刪除失敗: ' + e.message);
  }
}

// Handle QA
document.getElementById('btn').onclick = async () => {
  const q = document.getElementById('q').value.trim();
  if (!q) {
    alert('請輸入問題');
    return;
  }
  
  const btn = document.getElementById('btn');
  const outDiv = document.getElementById('out');
  
  btn.disabled = true;
  btn.classList.add('loading');
  outDiv.textContent = '⏳ 正在處理你的問題...';
  
  try {
    const res = await fetch('/qa', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: q})
    });
    const j = await res.json();
    
    let out = '';
    if (j.error) {
      outDiv.className = 'error-msg';
      outDiv.textContent = '❌ 錯誤: ' + j.error;
    } else {
      outDiv.className = '';
      out += '🤖 RAG 回答 (基於知識庫):\n';
      out += j.rag_answer + '\n\n';
      out += '———————————————————————————————\n\n';
      out += '💭 基礎回答 (沒有知識庫):\n';
      out += j.baseline_answer + '\n\n';
      
      if (j.sources && j.sources.length > 0) {
        out += '———————————————————————————————\n\n';
        out += '📚 相關來源文檔:\n';
        j.sources.forEach((s, i) => {
          out += `\n${i + 1}. ${s.id || s.filename || 'source'}\n`;
          out += `   相似度分數: ${(s.score || 0).toFixed(4)}\n`;
          out += `   内容: ${(s.text || '').substring(0, 150).replace(/\n/g, ' ')}...\n`;
        });
      } else {
        out += '———————————————————————————————\n\n';
        out += '⚠️  沒有找到相關文檔';
      }
      
      out += '\n\n———————————————————————————————\n';
      out += `⏱️  處理耗時:\n`;
      out += `   文檔檢索: ${j.timings.retrieval_ms}ms\n`;
      out += `   RAG 模型推理: ${j.timings.llm_rag_ms}ms\n`;
      out += `   基礎模型推理: ${j.timings.llm_baseline_ms}ms`;
      
      outDiv.textContent = out;
    }
  } catch (e) {
    outDiv.className = 'error-msg';
    outDiv.textContent = '❌ 請求失敗: ' + e.message;
  } finally {
    btn.disabled = false;
    btn.classList.remove('loading');
  }
};

// Utility function to escape HTML
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Load documents on page load
window.addEventListener('load', loadDocuments);
