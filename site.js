const grid = document.getElementById('work-grid');

function card(work) {
  const el = document.createElement('article');
  el.className = 'card';
  el.innerHTML = `
    <a class="card-media" href="${work.href}" aria-label="打开 ${work.title}">
      <img src="${work.hero}" alt="${work.title} ${work.subtitle || ''} 主视觉" loading="lazy">
    </a>
    <div class="card-body">
      <p class="card-meta">${work.date || ''}${work.tags?.length ? ' · ' + work.tags.join(' / ') : ''}</p>
      <h3>${work.title}${work.subtitle ? `<span>${work.subtitle}</span>` : ''}</h3>
      <p>${work.summary || ''}</p>
      <div class="tags">${(work.tags || []).map(t => `<span>${t}</span>`).join('')}</div>
    </div>
    ${work.downloads?.length ? `<div class="downloads">${work.downloads.map(d =>
      `<a href="${d.href}" download><span>${d.label}</span><b>${d.note || '↘'}</b></a>`
    ).join('')}</div>` : ''}
  `;
  return el;
}

try {
  const res = await fetch('./works.json', { cache: 'no-store' });
  if (!res.ok) throw new Error(res.statusText);
  const works = await res.json();
  grid.replaceChildren(...works.map(card));
} catch (err) {
  grid.innerHTML = `<p style="color:#6b655c">作品列表暂时读不到：${err.message}</p>`;
}
