/* ──────────────────────────────────────────────────────────────────
   achievements.js – reads server-rendered .achieve-card elements
   and powers the full-screen popup modal with image
   ────────────────────────────────────────────────────────────── */

const modal = document.querySelector('.mother-container');

function closeModal() {
    if (!modal) return;
    const card = modal.querySelector('[data-popup-card]');
    modal.style.opacity = '0';
    if (card) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px) scale(0.96)';
    }
    setTimeout(() => {
        modal.innerHTML = '';
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }, 280);
}

function openModal(el) {
    if (!modal || !el) return;
    const title = el.dataset.title;
    const text  = el.dataset.text;
    const image = el.dataset.image;

    const html = `
        <div class="relative w-full max-w-4xl overflow-hidden rounded-3xl border border-white/30 bg-white shadow-2xl"
             data-popup-card style="max-height:90vh; opacity:0; transform:translateY(20px) scale(0.96); transition:transform 320ms cubic-bezier(.22,1,.36,1), opacity 240ms ease;">
            <div class="relative flex max-h-[90vh] flex-col">
                <button class="absolute right-4 top-4 z-10 rounded-full border border-slate-200 bg-white/80 p-2 text-slate-500 transition hover:border-brand-aqua hover:text-brand-blue" data-close="true" aria-label="Close popup">
                    <i class="fa-solid fa-xmark text-lg"></i>
                </button>
                <img src="${image}" alt="${title}" class="h-56 w-full object-cover md:h-72">
                <div class="overflow-y-auto p-6 md:p-8">
                    <h1 class="text-2xl font-semibold text-slate-900 md:text-3xl">${title}</h1>
                    <p class="mt-4 text-sm leading-7 text-slate-600 md:text-base">${text}</p>
                </div>
            </div>
        </div>`;

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    modal.style.opacity = '0';
    modal.style.transition = 'opacity 220ms ease';
    modal.innerHTML = html;

    requestAnimationFrame(() => {
        modal.style.opacity = '1';
        const popup = modal.querySelector('[data-popup-card]');
        if (popup) {
            popup.style.opacity = '1';
            popup.style.transform = 'translateY(0) scale(1)';
        }
    });
}

/* Attach click handlers to every server-rendered card */
document.querySelectorAll('.achieve-card').forEach(card => {
    card.addEventListener('click', () => openModal(card));
});

/* Close on backdrop click, close button, or Escape key */
document.addEventListener('click', e => {
    if (!modal) return;
    if (e.target.closest('[data-close="true"]')) { closeModal(); return; }
    if (e.target === modal) closeModal();
});
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });