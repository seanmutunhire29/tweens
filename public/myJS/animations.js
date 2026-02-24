function isReducedMotionPreferred() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function getRevealTargets(root) {
    return root.querySelectorAll(
        [
            'main > section',
            'main > article',
            'main > aside',
            'main > div',
            '.achievements > *',
            '.prog-body > *',
            '.years-container > *',
            '.article-body',
            '#success-message'
        ].join(',')
    );
}

function shouldSkipTarget(element) {
    return Boolean(
        element.closest('.mother-container') ||
        element.closest('.eachProg .fixed')
    );
}

function prepareRevealTarget(element, indexInGroup) {
    if (element.dataset.motionReady === 'true' || shouldSkipTarget(element)) {
        return;
    }

    element.dataset.motionReady = 'true';
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    element.style.transitionProperty = 'opacity, transform';
    element.style.transitionDuration = '650ms';
    element.style.transitionTimingFunction = 'cubic-bezier(0.22, 1, 0.36, 1)';
    element.style.transitionDelay = `${Math.min(indexInGroup * 55, 240)}ms`;
}

function revealElement(element) {
    element.style.opacity = '1';
    element.style.transform = 'translateY(0)';
}

function runGlobalAnimations() {
    const targets = Array.from(getRevealTargets(document));
    if (!targets.length) {
        return;
    }

    if (isReducedMotionPreferred()) {
        targets.forEach((target) => {
            target.style.opacity = '1';
            target.style.transform = 'none';
        });
        return;
    }

    targets.forEach((target, index) => {
        prepareRevealTarget(target, index);
    });

    if (!('IntersectionObserver' in window)) {
        targets.forEach((target) => revealElement(target));
        return;
    }

    const observer = new IntersectionObserver((entries, observed) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) {
                return;
            }

            revealElement(entry.target);
            observed.unobserve(entry.target);
        });
    }, {
        threshold: 0.12,
        rootMargin: '0px 0px -36px 0px'
    });

    targets.forEach((target) => observer.observe(target));

    const dynamicContainers = document.querySelectorAll('.achievements, .prog-body, .years-container');
    dynamicContainers.forEach((container) => {
        const mutationObserver = new MutationObserver(() => {
            const dynamicTargets = Array.from(container.children);
            dynamicTargets.forEach((target, index) => {
                prepareRevealTarget(target, index);
                observer.observe(target);
            });
        });

        mutationObserver.observe(container, {
            childList: true,
            subtree: false
        });
    });

    const heroContent = document.querySelector('header .mx-auto.flex.max-w-6xl.flex-col.gap-6');
    if (heroContent) {
        heroContent.style.opacity = '0';
        heroContent.style.transform = 'translateY(12px)';
        heroContent.style.transition = 'opacity 520ms ease-out, transform 520ms ease-out';
        requestAnimationFrame(() => {
            heroContent.style.opacity = '1';
            heroContent.style.transform = 'translateY(0)';
        });
    }
}

runGlobalAnimations();
