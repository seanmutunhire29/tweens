// List of all objects that represent each program
const programs = [



    {
        id: 2,
        title: "Tutoring lessons",
        description: "Our tutoring lessons offer personalized academic support to help students excel in their studies. Whether you need help with challenging subjects, homework assistance, or exam preparation, our experienced tutors provide tailored guidance to meet individual learning needs. With interactive and engaging sessions, we ensure students build confidence, master difficult concepts, and achieve their academic goals at their own pace.",
        category: "academic",
        progress: 4,
        showImage: "imagePrograms\\progTutoringLessons1.jpeg",
        media: [
            "imagePrograms\\progTutoringLessons1.jpeg",
            "imagePrograms\\progTutoringLessons2.jpeg",
            "imagePrograms\\progTutoringLessons3.jpeg",
            "imagePrograms\\progTutoringLessons4.jpeg"
        ],
    },
    {
        id: 1,
        title: "Study spaces ",
        description: "Our study spaces provide a quiet and comfortable environment where students can focus, collaborate, and achieve their academic goals. Equipped with ergonomic seating, ample lighting, and a distraction-free atmosphere, these spaces are perfect for deep concentration or group discussions. Whether you're preparing for exams, working on assignments, or engaging in research, our study spaces offer the ideal setting to enhance productivity and learning.",
        category: "academic",
        progress: 3,
        showImage: "imagePrograms\\progStudySpaces.png",
        media: [
            "imagePrograms\\progStudy1.png",
        ],
    },

    {
        id: 3,
        title: "Scholarship mentorship",
        description: "We provide guidance and mentorship to help students navigate scholarship opportunities and application processes. Our information sessions cover available scholarships, eligibility criteria, and application tips, while our mentorship program offers one-on-one support in crafting compelling applications, writing essays, and preparing for interviews. Whether you're seeking local or international scholarships, we equip you with the knowledge and skills to increase your chances of success.",
        category: "academic",
        progress: 8,
        showImage: "imagePrograms\\progScholarship.png",
        media: [
            "imagePrograms\\progScholarshipMentorship1.jpeg",
            "imagePrograms\\progScholarshipMentorship2.jpeg",
            "imagePrograms\\progScholarshipMentorship3.jpeg",
        ],
    },

    {
        id: 4,
        title: "Internet Access",
        description: "Stay connected and access online resources with our high-speed internet, providing 50GB of data per month. Whether you're researching for school projects, attending virtual classes, or working on assignments, our reliable internet ensures seamless browsing, video streaming, and downloads to support your academic needs.",
        category: "resources",
        progress: 10,
        showImage: "imagePrograms\\progInternet.png",
        media: [
            "imagePrograms\\progInternet.png",
        ],
    },

    {
        id: 5,
        title: "Laptops & iPads",
        description: "Enhance your learning experience with access to our five laptops and eight iPads. Whether you're conducting research, completing assignments, coding, or exploring educational apps, these devices provide the tools you need to stay productive and engaged. Perfect for both individual and group work, our tech resources ensure that students have the digital support necessary for academic success.",
        category: "resources",
        progress: 1,
        showImage: "images\\laptops-ipads_enhanced.jpg",
        media: [
            "images\\laptops-ipads_enhanced.jpg",
        ],
    },

    {
        id: 6,
        title: "Form 3 & 4 Textbooks",
        description: "Access a collection of Form 3 and 4 textbooks covering key subjects to support your studies. Whether you need resources for exam preparation, homework, or deeper subject understanding, our textbooks provide reliable content aligned with the curriculum to help you excel academically.",
        category: "academic",
        progress: 0,
        showImage: "imagePrograms\\progBooks.png",
        media: [
            "imagePrograms\\progTextbooks1.jpeg",
            "imagePrograms\\progTextbooks2.jpeg",
        ],
    },

    {
        id: 7,
        title: "Motivational sessions",
        description: "Stay inspired and driven with our motivational sessions designed to encourage personal growth and academic excellence. Through engaging talks, interactive discussions, and mentorship, we empower students to overcome challenges, set ambitious goals, and develop a success-oriented mindset. Whether you need a confidence boost or strategies to stay focused, our sessions provide the motivation to keep pushing forward.",
        category: "wellbeing",
        progress: 3,
        showImage: "imagePrograms\\progMotivation.png",
        media: [
            "imagePrograms\\progMotivation.png",
        ],
    },

    {
        id: 8,
        title: "Wide range of books",
        description: "Discover a diverse collection of books covering various subjects, including academics, self-improvement, fiction, and career development. Whether you're looking for textbooks, inspiring biographies, or engaging novels, our library offers resources to expand your knowledge, spark creativity, and support lifelong learning.",
        category: "wellbeing",
        progress: 2,
        showImage: "imagePrograms\\progWideRangeOfBooks.jpeg",
        media: [
            "imagePrograms\\progWideRangeOfBooks.jpeg",
        ],
    },

    {
        id: 9,
        title: "U.S. College Application Books",
        description: "Gain valuable insights into the U.S. college application process with our collection of books designed to guide you through every step. From crafting compelling essays to understanding admissions requirements, these resources provide essential tips and strategies to help you navigate applications, secure scholarships, and increase your chances of getting into your dream college.",
        category: "resources",
        progress: 9,
        showImage: "imagePrograms\\progUSColleges.jpeg",
        media: [
            "imagePrograms\\progUSColleges.jpeg",
        ],
    },

    {
        id: 10,
        title: "Board games",
        description: "Take a break and challenge your mind with our engaging board games! Whether you're sharpening your strategic thinking with chess or enjoying fast-paced fun with 30 Seconds, our games provide the perfect way to relax, socialize, and develop critical thinking skills in a friendly environment.",
        category: "wellbeing",
        progress: 7,
        showImage: "imagePrograms\\progChess.png",
        media: [
            "imagePrograms\\progBoard1.jpeg",
            "imagePrograms\\progBoard2.jpeg",
            "imagePrograms\\progBoard3.jpeg",
            "imagePrograms\\progBoard4.jpeg",
            "imagePrograms\\progBoard5.jpeg"
        ],
    }
];

function normalizePath(path) {
    const normalized = path.replace(/\\/g, "/");
    return normalized.startsWith("/") ? normalized : `/${normalized}`;
}

// Show programs when page loads
const defaultButton = document.querySelector('.js-button');
showProgs(programs, defaultButton);

// Filter buttons logic
const selectButtons = document.querySelectorAll('.js-button');
selectButtons.forEach((button) => {
    button.addEventListener('click', () => {
        showProgs(programs, button);
    });
});

// Function to display programs based on the selected filter
function showProgs(allProgs, button) {
    document.querySelectorAll('.js-button').forEach((btn) => {
        btn.classList.remove('bg-brand-aqua', 'text-slate-900');
        btn.classList.add('bg-brand-blue', 'text-white');
    });

    if (button) {
        button.classList.add('bg-brand-aqua', 'text-slate-900');
        button.classList.remove('bg-brand-blue', 'text-white');
    }

    let displayProgs = ``;

    allProgs.forEach((program) => {
        const matches =
            button &&
            (button.innerHTML === 'All' || button.innerHTML.toLowerCase() === program.category);

        if (matches) {
            const showImage = normalizePath(program.showImage);
            displayProgs += `
                <div data-id="${program.id}" class="each-prog group overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-xl">
                    <div class="aspect-[4/3] overflow-hidden">
                        <img src="${showImage}" alt="${program.title}" class="h-full w-full object-cover transition duration-500 group-hover:scale-105">
                    </div>
                    <div class="space-y-2 p-5">
                        <h3 class="text-lg font-semibold text-slate-900">${program.title}</h3>
                        <p class="text-sm text-slate-600">${program.description}</p>
                    </div>
                </div>
            `;
        }
    });

    document.querySelector('.prog-body').innerHTML = displayProgs;
}

// Delegate click events for dynamically created program cards
document.querySelector('.prog-body').addEventListener('click', (event) => {
    const prog = event.target.closest('.each-prog');
    if (!prog) {
        return;
    }

    const program = programs.find((one) => one.id == prog.dataset.id);
    if (!program) {
        return;
    }

    const mediaItems = program.media
        .map((pic) => {
            const normalized = normalizePath(pic);
            return `
                <div class="overflow-hidden rounded-2xl border border-slate-200">
                    <img src="${normalized}" class="h-40 w-full object-cover" alt="Program Image">
                </div>
            `;
        })
        .join('');

    const showProg = `
        <div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4">
            <div class="relative w-full max-w-5xl rounded-3xl bg-white p-6 shadow-2xl">
                <button class="js-close absolute right-4 top-4 rounded-full border border-slate-200 p-2 text-slate-500 transition hover:border-brand-aqua hover:text-brand-blue">
                    <i class="fa-solid fa-rectangle-xmark"></i>
                </button>
                <div class="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
                    <div class="grid max-h-[60vh] grid-cols-2 gap-3 overflow-y-auto pr-1">
                        ${mediaItems}
                    </div>
                    <div>
                        <h2 class="text-2xl font-semibold text-slate-900">${program.title}</h2>
                        <p class="mt-3 text-sm text-slate-600">${program.description}</p>
                        <div class="mt-6 flex flex-wrap gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
                            <span class="rounded-full border border-slate-200 px-3 py-1">${program.category}</span>
                            <span class="rounded-full border border-slate-200 px-3 py-1">Impact level ${program.progress}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.querySelector('.eachProg').innerHTML = showProg;
});

// Close pop-up logic
document.querySelector('.eachProg').addEventListener('click', (event) => {
    if (event.target.classList.contains('js-close') || event.target.closest('.js-close')) {
        document.querySelector('.eachProg').innerHTML = '';
    }
});
