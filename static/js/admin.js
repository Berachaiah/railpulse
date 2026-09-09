function animateFlap(el) {
  const target = el.getAttribute("data-flap-target");
  if (target == null) return;

  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReduced) {
    el.textContent = target;
    return;
  }

  const digits = "0123456789";
  const duration = 700;
  const start = performance.now();
  const targetChars = target.split("");

  function frame(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const settledCount = Math.floor(progress * targetChars.length * 1.4);

    el.textContent = targetChars
      .map((ch, i) => {
        if (!/[0-9]/.test(ch)) return ch;          // keep commas, $, % etc. static
        if (i < settledCount) return ch;            // this digit has landed
        return digits[Math.floor(Math.random() * 10)];
      })
      .join("");

    if (progress < 1) requestAnimationFrame(frame);
    else el.textContent = target;
  }
  requestAnimationFrame(frame);
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-flap-target]").forEach((el, i) => {
    setTimeout(() => animateFlap(el), i * 120); // slight stagger per card
  });
});
