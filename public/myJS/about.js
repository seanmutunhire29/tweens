const y2020 = `
    <div class="year rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex items-center justify-between">
            <h2 class="text-2xl font-semibold text-brand-blue">2020</h2>
            <span class="rounded-full bg-brand-aqua/20 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-brand-blue">Milestone</span>
        </div>
        <div class="mt-4 space-y-3 text-sm text-slate-600">
            <p>TWEENS was founded in 2020 with a vision to make education accessible for students in need. Without a physical space or resources, we began by offering home tutoring to Form 3 and Form 4 students.</p>
            <p>Despite the challenges—teaching in living rooms, kitchens, or even under trees—we remained committed. This resilience laid the foundation for TWEENS to grow into the impactful educational organization it is today.</p>
        </div>
    </div>
`;

const y2021 = `
    <div class="year rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex items-center justify-between">
            <h2 class="text-2xl font-semibold text-brand-blue">2021</h2>
            <span class="rounded-full bg-brand-aqua/20 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-brand-blue">Growth</span>
        </div>
        <div class="mt-4 space-y-3 text-sm text-slate-600">
            <p>In 2021, TWEENS took a major leap forward with the Government of Zimbabwe providing a building for our operations. With the help of a Davis Peace Grant, we transformed it into a proper learning space.</p>
            <p>This new facility enabled us to offer structured, high-quality tutoring in a safe environment, expanding our impact.</p>
        </div>
    </div>
`;

const y2022 = `
    <div class="year rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex items-center justify-between">
            <h2 class="text-2xl font-semibold text-brand-blue">2022</h2>
            <span class="rounded-full bg-brand-aqua/20 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-brand-blue">Expansion</span>
        </div>
        <div class="mt-4 space-y-3 text-sm text-slate-600">
            <p>In 2022, TWEENS broadened its impact by introducing clubs and extracurricular activities to foster holistic development. Students engaged in sports, book club discussions, and leadership sessions.</p>
            <p>Textbook donations enabled the introduction of science classes for O-Level students, enriching academic growth.</p>
        </div>
    </div>
`;

const y2023 = `
    <div class="year rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex items-center justify-between">
            <h2 class="text-2xl font-semibold text-brand-blue">2023</h2>
            <span class="rounded-full bg-brand-aqua/20 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-brand-blue">Momentum</span>
        </div>
        <div class="mt-4 space-y-3 text-sm text-slate-600">
            <p>In 2023, TWEENS launched an A-Level program to support high-achieving students facing financial barriers.</p>
            <p>Extracurricular activities thrived, and the Book Club fostered a love for reading and literacy.</p>
            <p>A proud milestone came on July 27, when two members were accepted to Duolingo, highlighting student success.</p>
        </div>
    </div>
`;

const y2024 = `
    <div class="year rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex items-center justify-between">
            <h2 class="text-2xl font-semibold text-brand-blue">2024</h2>
            <span class="rounded-full bg-brand-aqua/20 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-brand-blue">Advocacy</span>
        </div>
        <div class="mt-4 space-y-3 text-sm text-slate-600">
            <p>TWEENS deepened community engagement with monthly cleanup campaigns and expanded networks through key workshops.</p>
            <p>Invitations from international organizations recognized advocacy for refugee education.</p>
            <p>The resettlement of 15 students overseas marked a transformative academic milestone.</p>
        </div>
    </div>
`;

const y2025 = `
    <div class="year rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex items-center justify-between">
            <h2 class="text-2xl font-semibold text-brand-blue">2025</h2>
            <span class="rounded-full bg-brand-aqua/20 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-brand-blue">Leadership</span>
        </div>
        <div class="mt-4 space-y-3 text-sm text-slate-600">
            <p>TWEENS expanded programs and recruited Form 5 students into A-Level offerings, broadening academic opportunities.</p>
            <p>The Big Sister-Little Sister mentorship program launched, and an MOU with Cohere opened new resources.</p>
            <p>Scholarship information sessions empowered students to access financial support for continued learning.</p>
        </div>
    </div>
`;

function setActive(button) {
    document.querySelectorAll('.jsyear').forEach((btn) => {
        btn.classList.remove('bg-brand-aqua', 'text-slate-900');
        btn.classList.add('bg-brand-blue', 'text-white');
    });
    button.classList.add('bg-brand-aqua', 'text-slate-900');
    button.classList.remove('bg-brand-blue', 'text-white');
}

const myButtons = document.querySelectorAll('.jsyear');
myButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const year = button.innerHTML.trim();
        const yearHolder = document.querySelector('.years-container');
        if (!yearHolder) {
            return;
        }

        setActive(button);

        if (year === "2021") {
            yearHolder.innerHTML = y2021;
        } else if (year === "2022") {
            yearHolder.innerHTML = y2022;
        } else if (year === "2023") {
            yearHolder.innerHTML = y2023;
        } else if (year === "2024") {
            yearHolder.innerHTML = y2024;
        } else if (year === "2025") {
            yearHolder.innerHTML = y2025;
        } else {
            yearHolder.innerHTML = y2020;
        }
    });
});

if (myButtons.length > 0) {
    setActive(myButtons[0]);
    const yearHolder = document.querySelector('.years-container');
    if (yearHolder) {
        yearHolder.innerHTML = y2020;
    }
}