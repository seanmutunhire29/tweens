const heroSlides = [
    {
        id: 1,
        title: "Tweens",
        text: "Over five years of improving the lives of children living in Tongogara refugee camp.",
        buttonText: "Check Out",
        buttonHref: "/about",
        image: "/images/home1.png"
    },
    {
        id: 2,
        title: "Welcome to Tweens",
        text: "We are here to assist children in Tongogara Refugee Camp through education and empowerment.",
        buttonText: "Explore",
        buttonHref: "#activities",
        image: "/images/home2.jpeg"
    },
    {
        id: 3,
        title: "Tweens",
        text: "An organisation for refugees by refugees created to change lives for the better.",
        buttonText: "Learn More",
        buttonHref: "/about",
        image: "/images/home3.png"
    }
];

function renderHero(slide) {
    return `
        <div class="home-container absolute inset-0 flex items-center transition-opacity duration-1000 ease-in-out" data-id="${slide.id}" style="background-image: linear-gradient(rgba(15, 23, 42, 0.65), rgba(15, 23, 42, 0.65)), url('${slide.image}'); background-position: center; background-size: cover; opacity: 1; will-change: opacity;">
            <div class="relative z-10 mx-auto w-full max-w-6xl px-6 py-24 text-white">
                <div class="max-w-2xl space-y-6">
                    <h1 class="text-5xl font-semibold leading-tight md:text-6xl">${slide.title}</h1>
                    <p class="text-lg text-white/85">${slide.text}</p>
                    <div class="flex flex-wrap gap-3">
                        <a href="${slide.buttonHref}" class="rounded-full bg-brand-aqua px-6 py-3 text-sm font-semibold text-slate-900 transition hover:brightness-110">${slide.buttonText}</a>
                        <a href="/donations" class="rounded-full border border-white/40 px-6 py-3 text-sm font-semibold text-white transition hover:border-white hover:bg-white/10">Donate</a>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function fadeToHero(nextSlide) {
    const homeContainer = document.querySelector('.home-background');
    const currentBackground = document.querySelector('.home-container');
    if (!homeContainer || !currentBackground) {
        return;
    }

    const slideShell = document.createElement('div');
    slideShell.innerHTML = renderHero(nextSlide).trim();
    const incomingBackground = slideShell.firstElementChild;

    if (!incomingBackground) {
        return;
    }

    incomingBackground.style.opacity = '0';
    homeContainer.appendChild(incomingBackground);

    requestAnimationFrame(() => {
        currentBackground.style.opacity = '0';
        incomingBackground.style.opacity = '1';
    });

    setTimeout(() => {
        currentBackground.remove();
    }, 1000);
}

function changeBackground() {
    const currentBackground = document.querySelector('.home-container');
    if (!currentBackground) {
        return;
    }

    const currentId = Number(currentBackground.dataset.id);
    const currentIndex = heroSlides.findIndex((slide) => slide.id === currentId);
    const nextIndex = currentIndex === -1 ? 0 : (currentIndex + 1) % heroSlides.length;
    fadeToHero(heroSlides[nextIndex]);
}

function initializeHeroBackground() {
    const firstBackground = document.querySelector('.home-container');
    if (!firstBackground) {
        return;
    }

    const initialImage = firstBackground.dataset.image;
    if (!initialImage) {
        return;
    }

    firstBackground.style.backgroundImage = `linear-gradient(rgba(15, 23, 42, 0.65), rgba(15, 23, 42, 0.65)), url('${initialImage}')`;
}

initializeHeroBackground();
setInterval(changeBackground, 7000);

function setupScrollReveal() {
    const revealElements = document.querySelectorAll('[data-reveal]');
    if (!revealElements.length) {
        return;
    }

    revealElements.forEach((element, index) => {
        const stagger = element.dataset.revealDelay || `${Math.min(index * 60, 420)}`;
        element.style.opacity = '0';
        element.style.transition = 'opacity 750ms ease-out';
        element.style.transitionDelay = `${stagger}ms`;
    });

    const observer = new IntersectionObserver((entries, observe) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) {
                return;
            }

            entry.target.style.opacity = '1';
            observe.unobserve(entry.target);
        });
    }, {
        threshold: 0.14,
        rootMargin: '0px 0px -40px 0px'
    });

    revealElements.forEach((element) => observer.observe(element));
}

window.addEventListener('scroll', () => {
    const banner = document.querySelector(".nav-banner");
    const mobileToggle = document.querySelector('.open-nav-icon');
    if (!banner || !mobileToggle) {
        return;
    }

    if (window.scrollY > 20) {
        banner.style.backgroundColor = "rgba(7, 201, 255, 0.9)";
        mobileToggle.style.display = 'none';
    } else {
        banner.style.backgroundColor = "transparent";
        mobileToggle.style.display = 'inline';
    }
});

setupScrollReveal();

