document.addEventListener("DOMContentLoaded", () => {
  // Mobile menu toggle
  const menuBtn = document.getElementById("menuButton");
  const mobileMenu = document.getElementById("mobileMenu");
  if (menuBtn && mobileMenu) {
    menuBtn.onclick = () => mobileMenu.classList.toggle("hidden");
  }

  // Sticky glass navbar on scroll (visuals live in navbar.css via .nav-scrolled)
  const nav = document.querySelector("nav");
  window.addEventListener("scroll", () => {
    nav?.classList.toggle("nav-scrolled", window.scrollY > 20);
  });

  // Scroll reveal
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("opacity-100", "translate-y-0");
        entry.target.classList.remove("opacity-0", "translate-y-8");
        observer.unobserve(entry.target);
      }
    });
  }, { root: null, threshold: 0.1, rootMargin: "0px 0px -50px 0px" });

  document.querySelectorAll("section, .glass, .card").forEach((el) => {
    el.classList.add("transition-all", "duration-700", "ease-out", "opacity-0", "translate-y-8");
    revealObserver.observe(el);
  });

  // Scrollspy: highlight the nav link matching the section in view
  const navLinks = document.querySelectorAll(".nav-link");
  const sections = [...navLinks]
    .map(link => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);

  if (sections.length && "IntersectionObserver" in window) {
    const spy = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          const id = `#${entry.target.id}`;
          navLinks.forEach(link => {
            link.classList.toggle("nav-link-active", link.getAttribute("href") === id);
          });
        });
      },
      { rootMargin: "-45% 0px -45% 0px", threshold: 0 }
    );
    sections.forEach(section => spy.observe(section));
  }

  // Typewriter hero text (HERO_TEXTS is injected inline by the template)
  const targetEl = document.getElementById("hero-typewriter");
  if (targetEl && typeof HERO_TEXTS !== "undefined") {
    let textIndex = 0;
    let charIndex = 0;
    let deletingMode = false;
    const typingSpeed = 60;
    const deletingSpeed = 30;
    const pauseDuration = 2000;

    function type() {
      const currentText = HERO_TEXTS[textIndex];
      if (deletingMode) {
        targetEl.textContent = currentText.substring(0, charIndex - 1);
        charIndex--;
      } else {
        targetEl.textContent = currentText.substring(0, charIndex + 1);
        charIndex++;
      }

      let delta = deletingMode ? deletingSpeed : typingSpeed;
      if (!deletingMode && charIndex === currentText.length) {
        delta = pauseDuration;
        deletingMode = true;
      } else if (deletingMode && charIndex === 0) {
        deletingMode = false;
        textIndex = (textIndex + 1) % HERO_TEXTS.length;
        delta = 500;
      }
      setTimeout(type, delta);
    }
    type();
  }
});
