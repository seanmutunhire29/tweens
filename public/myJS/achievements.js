const allAchievements = [

    {
        id: 1,
        title: 'Empowering Students',
        image: 'images/achieveEmpower.png',
        text: 'In a remarkable display of leadership and mentorship, we inspired more than seven girls to retake their O-Level national exams after they initially faced setbacks. Recognizing the challenges these girls were experiencing, we took the initiative to provide emotional and academic support, encouraging them to overcome their doubts and persevere in their educational journey. Through one-on-one conversations, motivational talks, and sharing our collective experiences of overcoming obstacles, we helped them regain their confidence and commitment to their academic goals. Our approach focused not only on the importance of academic success but also on the resilience and strength it takes to rise after failure. As a result, these girls were able to regain their determination and successfully retake their exams, showing the power of encouragement and empowerment in transforming lives. This achievement reflects our passion for inspiring others, particularly young women, to pursue their dreams, no matter the obstacles they may face.',
    },
    {
        id: 2,
        title: 'Impactful Outreach',
        image: 'images/achieveOutreach.jpeg',
        text: 'Through dedicated efforts, we reached more than 500 students via awareness campaigns and motivational sessions aimed at fostering personal growth and academic success. Recognizing the importance of inspiring and educating young minds, we organized a series of interactive sessions that not only raised awareness about key issues such as educational opportunities, mental health, and self-motivation, but also empowered students to take proactive steps in their own lives. The sessions were carefully designed to be engaging, practical, and filled with actionable advice, all while creating a safe space for students to share their concerns and challenges. By connecting with so many students, we were able to foster a sense of community, encourage self-belief, and ultimately inspire them to pursue their goals with renewed enthusiasm. This outreach exemplifies our commitment to impacting the lives of youth, guiding them towards a brighter, more confident future.'
    },
    {
        id: 3,
        title: 'Comprehensive Student Support',
        image: 'images/achieveStudentSupport.png',
        text: 'We provided a wide range of essential services to up to 200 students, ensuring they had the resources and support necessary for academic success and personal growth. Our offerings included tutoring lessons tailored to meet individual learning needs, cozy study spaces designed for optimal focus, and reliable Wi-Fi to facilitate uninterrupted learning. Additionally, students had access to laptops and iPads, allowing them to engage with digital tools and resources, and a comprehensive collection of textbooks to support their academic curriculum. Beyond academics, we also provided after-school recreational activities, such as board games and motivational sessions, fostering a balanced and enriching experience for every student. This holistic approach aimed at addressing both the educational and personal development needs of students, empowering them to excel in their studies while cultivating essential life skills.'
    },
    {
        id: 4,
        title: 'Scholarship Success',
        image: 'images/achieveScholarSuccess.jpeg',
        text: 'We celebrated an incredible milestone as five of our students earned full scholarships for their A-Level studies at the prestigious USAP Community School, run by Education Matters. This achievement marks a significant step in empowering these students to pursue their educational dreams without financial barriers. Through personalized mentorship, guidance on scholarship applications, and motivational support, we helped these students navigate the application process, strengthening their essays, interview skills, and overall confidence. Securing full scholarships not only provided them with financial relief but also opened doors to a world of academic excellence and future opportunities. This accomplishment highlights our dedication to supporting students in achieving their highest potential and demonstrating that with the right guidance and determination, remarkable academic achievements are within reach.'
    },
    {
        id: 5,
        title: 'International Scholarships',
        image: 'images/achieveInternationalScholarships.png',
        text: 'A total of eight of our dedicated members have earned scholarships to pursue higher education abroad, marking a significant achievement in their academic journeys. These scholarships open doors to world-class educational opportunities, allowing the recipients to study at prestigious institutions outside the country. Through personalized mentorship, application support, and guidance on securing international funding, we helped these students develop competitive applications, refine their academic goals, and build the confidence needed to pursue their dreams globally. This achievement reflects our commitment to empowering students with the tools and knowledge to succeed on the international stage, ensuring they are well-equipped to make a lasting impact in their chosen fields.'
    },
    {
        id: 6,
        title: 'O-Level Success',
        image: 'images/achieveOLevelSuccess.png',
        text: 'Tens of non-formal education students successfully passed their O-Level exams, a direct result of the dedicated tutoring provided by TWEENS tutors. Our tutors played a pivotal role in equipping these students with the academic skills, knowledge, and confidence needed to succeed. By offering personalized tutoring sessions, we focused on reinforcing key concepts, addressing individual learning gaps, and helping students build exam strategies. This tailored approach ensured that each student received the support they needed to thrive, despite coming from non-formal education backgrounds. The success of these students highlights the impact of quality tutoring and the commitment of TWEENS tutors to empower learners, demonstrating that with the right guidance, all students can achieve their academic potential.'
    },
    {
        id: 7,
        title: 'Night Study Solar Lights',
        image: 'images/achieveSolarLights.png',
        text: 'Thanks to the solar lights facilitated through TWEENS by Naledi, more than 50 girls now have the ability to study at night in their homes, overcoming the barriers of limited electricity access. These solar-powered lights have provided a reliable and sustainable source of light, enabling the girls to continue their studies after dark, even in areas with power shortages. By ensuring that these students have the necessary tools for evening study sessions, we have significantly expanded their learning opportunities. This initiative has empowered them to complete homework, review lessons, and prepare for exams in a comfortable and safe environment, further enhancing their academic success. It reflects our commitment to breaking down the barriers to education and creating opportunities for all students to thrive, no matter the circumstances.'
    },
    {
        id: 8,
        title: 'Book Donation',
        image: 'images/achieveBookDonation.png',
        text: "Through the generous donation of more than 200 books by Kate Chambers, the JRS local library has received a significant boost in its collection, providing students and community members with a wider array of resources for learning and personal development. These books cover a variety of subjects, including academic texts, fiction, and self-help, offering something for every reader. The donation has not only enriched the library's offerings but also increased access to valuable reading materials, encouraging literacy and a love for learning within the community. Kate Chambers' contribution has made a lasting impact, empowering local residents to explore new ideas, enhance their knowledge, and pursue their educational goals."
    },
    {
        id: 9,
        title: 'Church Outreach Initiative',
        image: 'images/achieveChurch.png',
        text: "In 2023, we successfully reached out to 1,920 individuals across nine Christian denominations during our church visit initiative. This outreach allowed us to engage with a diverse group of people, fostering unity and connection within the community. By sharing important messages, offering support, and building relationships, we were able to spread awareness about various initiatives, provide guidance, and encourage personal growth. The visits created an opportunity to reach individuals from different backgrounds, offering them encouragement and practical advice. This outreach reflects our commitment to serving and empowering communities, creating lasting impacts through faith-based engagement and collaboration."
    }
]


let starsHTML = '';
allAchievements.forEach((achievement) => {
    const imagePath = achievement.image.startsWith('/') ? achievement.image : `/${achievement.image}`;
    const shortText = achievement.text.length > 145 ? `${achievement.text.slice(0, 145)}...` : achievement.text;
    const myStar = `
        <button class="achievement-card group relative flex h-full flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white text-left shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-xl" data-id="${achievement.id}" aria-label="Open ${achievement.title}" style="height: clamp(24rem, 48vw, 28rem);">
            <div class="bg-cover bg-center" style="height: 50%; background-image: linear-gradient(rgba(15, 23, 42, 0.2), rgba(15, 23, 42, 0.55)), url('${imagePath}');"></div>
            <div class="flex flex-col justify-between space-y-3 p-5" style="height: 50%;">
                <h3 class="text-xl font-semibold text-slate-900">${achievement.title}</h3>
                <p class="text-sm text-slate-600">${shortText}</p>
                <span class="inline-flex items-center gap-2 text-sm font-semibold text-brand-blue">Read full story <i class="fa-solid fa-arrow-right text-xs"></i></span>
            </div>
        </button>
    `;

    starsHTML += myStar;
});
const achievementsContainer = document.querySelector('.achievements');
if (achievementsContainer) {
    achievementsContainer.innerHTML = starsHTML;
}

const modal = document.querySelector('.mother-container');

function closeModal() {
    if (!modal) {
        return;
    }

    const popupCard = modal.querySelector('[data-popup-card="true"]');

    modal.style.opacity = '0';
    if (popupCard) {
        popupCard.style.opacity = '0';
        popupCard.style.transform = 'translateY(20px) scale(0.96)';
    }

    setTimeout(() => {
        modal.innerHTML = '';
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }, 280);
}

function openModal(chosenObject) {
    if (!modal || !chosenObject) {
        return;
    }

    const generatedHTML = `
        <div class="relative w-full max-w-5xl overflow-hidden rounded-3xl border border-white/30 bg-white shadow-2xl" data-popup-card="true" role="dialog" aria-modal="true" aria-label="${chosenObject.title}" style="max-height: 86vh; opacity: 0; transform: translateY(20px) scale(0.96); transition: transform 320ms cubic-bezier(0.22, 1, 0.36, 1), opacity 240ms ease;">
            <div class="relative flex max-h-[86vh] flex-col p-6 md:p-8">
                <button class="absolute right-4 top-4 rounded-full border border-slate-200 p-2 text-slate-500 transition hover:border-brand-aqua hover:text-brand-blue" data-close="true" aria-label="Close popup">
                    <i class="fa-solid fa-rectangle-xmark"></i>
                </button>
                <h1 class="pr-12 text-2xl font-semibold text-slate-900 md:text-3xl">${chosenObject.title}</h1>
                <p class="mt-4 overflow-y-auto pr-1 text-sm leading-7 text-slate-600 md:text-base">${chosenObject.text}</p>
            </div>
        </div>
    `;

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    modal.style.opacity = '0';
    modal.style.transition = 'opacity 220ms ease';
    modal.innerHTML = generatedHTML;

    requestAnimationFrame(() => {
        modal.style.opacity = '1';
        const popupCard = modal.querySelector('[data-popup-card="true"]');
        if (!popupCard) {
            return;
        }
        popupCard.style.opacity = '1';
        popupCard.style.transform = 'translateY(0) scale(1)';
    });
}

const allCards = document.querySelectorAll('.achievement-card');
allCards.forEach((card) => {
    card.addEventListener('click', () => {
        const cardId = Number(card.dataset.id);
        const chosenObject = allAchievements.find((object) => object.id === cardId);
        openModal(chosenObject);
    });
});

document.addEventListener('click', (event) => {
    if (!modal) {
        return;
    }

    const target = event.target;
    if (target && target.closest('[data-close="true"]')) {
        closeModal();
        return;
    }

    if (target === modal) {
        closeModal();
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closeModal();
    }
});