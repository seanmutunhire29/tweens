// To make Hero section dynamic

function changeBackground() {

    const background1 = `
        <div class="home-container home-header-1"  data-id="1">
            <div class="banner-text">
                <h1>Tweens</h1>
                <p>Over five years of improving the lives of children living in Tongogara refugee camp</p>
                <a href="/about"><button>Check Out</button></a>
            </div>
        </div>
    `;

    const background2 = `
        <div class="home-container home-header-2"  data-id="2">
            <div class="banner-text">
                <h1>Welcome to Tweens</h1>
                <p>We are here to assist children in Tongogara Refugee Camp through education and empowerment.</p>
                <a href="#activities"><button>Explore</button></a>
            </div>
        </div>
    `;
    
    const background3 = `
        <div class="home-container home-header-3"  data-id="3">
            <div class="banner-text">
                <h1>Tweens</h1>
                <p>An organisation for refugees by refugees created to change lives for the better.</p>
                <a href="/about"><button>Learnmore</button></a>
            </div>
        </div>
    `;

    const homeContainer = document.querySelector('.home-background');

    const currentBackground = document.querySelector('.home-container');

    if(currentBackground.dataset.id == "1") {
        homeContainer.innerHTML = background2;
    }

    else if(currentBackground.dataset.id == "2") {
        homeContainer.innerHTML = background3;
    }

    else if(currentBackground.dataset.id == "3") {
        homeContainer.innerHTML = background1;
    }
}

setInterval(changeBackground, 6000);



// To change banner background on scroll
window.addEventListener('scroll', () => {
    if (window.scrollY > 20){
        document.querySelector(".nav-banner").style.backgroundColor = "rgba(7, 201, 255, 1)";
        document.querySelector('.open-nav-icon').style.display = 'none';
    }else{
        document.querySelector(".nav-banner").style.backgroundColor = "transparent";
        document.querySelector('.open-nav-icon').style.display = 'inline';
    }
});

