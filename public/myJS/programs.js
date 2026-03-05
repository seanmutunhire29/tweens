/* ──────────────────────────────────────────────────────────────────
   programs.js – reads server-rendered .prog-card elements,
   implements category filtering and a centred popup with blur
   ────────────────────────────────────────────────────────────── */

const progBody   = document.querySelector('.prog-body');
const popupHost  = document.querySelector('.eachProg');
const allCards   = Array.from(document.querySelectorAll('.prog-card'));
const filterBtns = document.querySelectorAll('.js-button');

/* ── Category filtering ── */
function filterCards(btn) {
    filterBtns.forEach(b => {
        b.classList.remove('bg-brand-aqua', 'text-slate-900');
        b.classList.add('bg-brand-blue', 'text-white');
    });
    if (btn) {
        btn.classList.add('bg-brand-aqua', 'text-slate-900');
        btn.classList.remove('bg-brand-blue', 'text-white');
    }
    const cat = btn ? btn.textContent.trim().toLowerCase() : 'all';
    allCards.forEach(card => {
        const show = cat === 'all' || card.dataset.category === cat;
        card.style.display = show ? '' : 'none';
    });
}

filterBtns.forEach(btn => btn.addEventListener('click', () => filterCards(btn)));
if (filterBtns.length) filterCards(filterBtns[0]); // default = All

/* ── Popup helpers ── */
function closePopup() {
    if (!popupHost) return;
    const inner = popupHost.querySelector('[data-popup-card]');
    popupHost.style.opacity = '0';
    if (inner) {
        inner.style.opacity = '0';
        inner.style.transform = 'translateY(20px) scale(0.96)';
    }
    setTimeout(() => {
        popupHost.innerHTML = '';
        popupHost.classList.add('hidden');
        popupHost.classList.remove('flex');
    }, 280);
}

function openPopup(card) {
    if (!popupHost || !card) return;
    const title = card.dataset.title;
    const desc  = card.dataset.description;
    const cat   = card.dataset.category;
    let media   = [];
    try { media = JSON.parse(card.dataset.media); } catch(e) {}

    const mediaHTML = media.map(src => `
        <div class="overflow-hidden rounded-2xl border border-slate-200">
            <img src="${src}" class="h-40 w-full object-cover" alt="Program image">
        </div>`).join('');

    const html = `
        <div class="relative w-full max-w-5xl overflow-hidden rounded-3xl bg-white shadow-2xl"
             data-popup-card
             style="max-height:90vh; opacity:0; transform:translateY(20px) scale(0.96);
                    transition:transform 320ms cubic-bezier(.22,1,.36,1), opacity 240ms ease;">
            <div class="relative flex max-h-[90vh] flex-col overflow-y-auto p-6 md:p-8">
                <button class="absolute right-4 top-4 z-10 rounded-full border border-slate-200 bg-white/80 p-2 text-slate-500 transition hover:border-brand-aqua hover:text-brand-blue" data-close="true" aria-label="Close">
                    <i class="fa-solid fa-xmark text-lg"></i>
                </button>
                <div class="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
                    <div class="grid max-h-[60vh] grid-cols-2 gap-3 overflow-y-auto pr-1">
                        ${mediaHTML}
                    </div>
                    <div>
                        <h2 class="text-2xl font-semibold text-slate-900 md:text-3xl">${title}</h2>
                        <p class="mt-3 text-sm leading-7 text-slate-600 md:text-base">${desc}</p>
                        <span class="mt-4 inline-block rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-slate-500">${cat}</span>
                    </div>
                </div>
            </div>
        </div>`;

    popupHost.classList.remove('hidden');
    popupHost.classList.add('flex');
    popupHost.style.opacity = '0';
    popupHost.style.transition = 'opacity 220ms ease';
    popupHost.innerHTML = html;

    requestAnimationFrame(() => {
        popupHost.style.opacity = '1';
        const inner = popupHost.querySelector('[data-popup-card]');
        if (inner) {
            inner.style.opacity = '1';
            inner.style.transform = 'translateY(0) scale(1)';
        }
    });
}

/* ── Card click → open popup ── */
allCards.forEach(card => card.addEventListener('click', () => openPopup(card)));

/* ── Close on backdrop / button / Escape ── */
document.addEventListener('click', e => {
    if (!popupHost) return;
    if (e.target.closest('[data-close="true"]')) { closePopup(); return; }
    if (e.target === popupHost) closePopup();
});
document.addEventListener('keydown', e => { if (e.key === 'Escape') closePopup(); });
