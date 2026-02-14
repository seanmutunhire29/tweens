const y2020 = `
        <div class="year">
            <div class="year-heading">
                <h2>2020</h2>
            </div>
            <div class="year-content">
                <div class="year-text" style="margin: 0;">
                    <p>TWEENS was founded in 2020 with a vision to make education accessible for students in need. Without a physical space or resources, we began by offering home tutoring to Form 3 and Form 4 students. Our dedicated tutors provided personalized lessons, not only teaching academics but also inspiring students to believe in their potential.</p>
                    <p>Despite the challenges—teaching in living rooms, kitchens, or even under trees—we remained committed. This resilience laid the foundation for TWEENS to grow into the impactful educational organization it is today.</p>
                </div>
            </div>
        </div>
`;

const y2021 = `
        <div class="year">
            <div class="year-heading">
                <h2>2021</h2>
            </div>
            <div class="year-content">
                <div class="year-text" style="margin: 0;">
                    <p>In 2021, TWEENS took a major leap forward with the Government of Zimbabwe providing a building for our operations. With the help of a Davis Peace Grant won by one of our members, we transformed it into a proper learning space.</p>
                    <p>This new facility enabled us to offer structured, high-quality tutoring in a safe environment, expanding our impact. We also launched fundraising efforts during Refugee Week, with vital support from Education Matters, helping us navigate challenges and achieve key milestones.</p>
                </div>
            </div>
        </div>
`;

const y2022 = `
        <div class="year">
            <div class="year-heading">
                <h2>2022</h2>
            </div>
            <div class="year-content">
                <div class="year-text" style="margin: 0;">
                    <p>In 2022, TWEENS broadened its impact by introducing clubs and extracurricular activities to foster holistic development. Students engaged in sports like table tennis, teqball, chess, volleyball, darts, and soccer, while the launch of a Book Club promoted literacy and analytical thinking.</p>
                    <p>A major milestone was the donation of Biology, Physics, and Chemistry textbooks by Calvin Burns, enabling us to introduce science classes for O-Level students. This expansion enriched both academic and personal growth, strengthening the TWEENS community and providing a well-rounded learning experience.</p>
                </div>
            </div>
        </div>
`;

const y2023 = `
        <div class="year">
            <div class="year-heading">
                <h2>2023</h2>
            </div>
            <div class="year-content">
                <div class="year-text" style="margin: 0;">
                    <p>In 2023, TWEENS took a major step by launching an A-Level program in August to support high-achieving students facing financial barriers after their ZIMSEC exams. This initiative provided a vital opportunity for continued education.</p>
                    <p>Our extracurricular activities thrived, culminating in a December 25 competition showcasing student talent in table tennis, teqball, chess, volleyball, darts, and soccer. The Book Club, launched on July 24, fostered a love for reading and literacy.</p>
                    <p>A proud milestone came on July 27, when two of our members were accepted to Duolingo, highlighting the dedication and success of our students. 2023 was a year of growth, resilience, and opportunity for the TWEENS community.</p>
                </div>
            </div>
        </div>
`;

const y2024 = `
        <div class="year">
            <div class="year-heading">
                <h2>2024</h2>
            </div>
            <div class="year-content">
                <div class="year-text" style="margin: 0;">
                    <p>In 2024, TWEENS deepened its community engagement with monthly cleanup campaigns, fostering responsibility among students. We also expanded our network by attending key workshops and Indabas, including events in Victoria Falls and with the Naledi Foundation, gaining valuable insights for growth.</p>
                    <p>A major milestone was receiving invitations to meetings with international organizations like UNHCR and local government bodies, recognizing our advocacy for refugee education. The year’s greatest achievement was the resettlement of 15 students overseas to continue their studies at USAP Community School, marking a transformative step in their academic journeys.</p>
                    <p>2024 was a year of collaboration, advocacy, and life-changing opportunities, solidifying TWEENS' role in supporting refugee youth and vulnerable communities.</p>
                </div>
            </div>
        </div>
`;

const y2025 = `
        <div class="year">
            <div class="year-heading">
                <h2>2025</h2>
            </div>
            <div class="year-content">
                <div class="year-text" style="margin: 0;">
                    <p>In 2025, TWEENS continued to build on the strong foundation we established in previous years, expanding our programs and creating more opportunities for our students. We recruited Form 5 students to join our A-Level program, further broadening our academic offerings and supporting more learners in their pursuit of higher education. Our church visits, initiated in 2024, remained a vital platform for raising education awareness within local communities, allowing us to connect with congregations and share information about available educational opportunities.</p>
                    <p>A key highlight of 2025 was the introduction of the Big Sister-Little Sister mentorship program, which paired older students with younger ones to foster a sense of community, support, and academic guidance. In February, <span style="font-weight: bold">we proudly signed an MOU with Cohere</span>, strengthening our partnerships and opening doors to new resources and collaborative opportunities. Additionally, we hosted scholarship information sessions in early January, organized by our advisory members, equipping students with the knowledge and confidence to navigate scholarship applications and access financial support.</p>
                    <p>To enhance the learning environment, we added more chairs and tables, ensuring our students had adequate space to study and work. We also continued efforts to improve internet connectivity, expanding access to online resources and virtual learning tools. All activities that began in 2020—tutoring, extracurricular activities, and mentorship—remained integral to our mission. As we reflect on our progress, we are deeply grateful for our dedicated team and the unwavering support of our partners, whose collaboration empowers us to provide quality education to those who need it most.</p>
                </div>
            </div>
        </div>
`;

function Indicator(buttons) {
    document.querySelectorAll('.jsyear').forEach((button) => {
        button.style.backgroundColor = 'blue';
    });
    buttons.style.backgroundColor = 'aqua';
}

const myButtons = document.querySelectorAll('.jsyear');
myButtons.forEach((button) => {
    button.addEventListener('click', () => {
        console.log();
        const year = button.innerHTML;
        const yearHolder = document.querySelector('.years-container');
        
        if (year == 2021){
            Indicator(button);
            yearHolder.innerHTML = y2021;
        } 
        
        else if(year == 2022){
            Indicator(button);
            yearHolder.innerHTML = y2022;
        } 
        
        else if(year == 2023){
            Indicator(button);
            yearHolder.innerHTML = y2023;
        } 
        
        else if(year == 2024){
            Indicator(button);
            yearHolder.innerHTML = y2024;
        } 
        
        else if(year == 2020){
            Indicator(button);
            yearHolder.innerHTML = y2020;
        } 

        else if(year == 2025){
            Indicator(button);
            yearHolder.innerHTML = y2025;
        } 
    });
});