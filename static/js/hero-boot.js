import { initHyperspeed } from './hyperspeed.js';

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('hero-hyperspeed');
  if (!container) return;

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) return;

  const isNarrow = window.innerWidth < 768;
  if (isNarrow) return; // mobile uses a static image instead — see hyperspeed.css

  const isLowCoreCount = (navigator.hardwareConcurrency || 8) <= 4;
  const lowPower = isLowCoreCount;

  let app = null;

  try {
    // Now an ambient page-wide background rather than the hero's focal
    // centerpiece, and it runs for as long as someone stays on the page
    // (not just while the hero is in view) -- toned down from the
    // original hero-only settings so sustained rendering stays cheap.
    app = initHyperspeed(container, {
      distortion: 'turbulentDistortion',
      length: 400,
      roadWidth: 9,
      islandWidth: 1.4,
      lanesPerRoad: 2,           // reads as twin rail tracks rather than a highway
      fov: 85,
      baseSpeed: 0.08,
      lowPower,
      maxPixelRatio: lowPower ? 1 : Math.min(window.devicePixelRatio, 1.5),
      lightPairsPerRoadWay: lowPower ? 10 : 20,
      totalSideLightSticks: lowPower ? 8 : 16,
      carLightsLength: [10, 50],
      movingAwaySpeed: [16, 24],
      movingCloserSpeed: [-30, -48],
      colors: {
        roadColor: 0x081321,
        islandColor: 0x0a1a2c,
        background: 0x081321,
        shoulderLines: 0x22d3ee,
        brokenLines: 0x22d3ee,
        leftCars: [0x22d3ee, 0x38bdf8, 0x6366f1],
        rightCars: [0x6366f1, 0x818cf8, 0x22d3ee],
        sticks: 0x22d3ee
      }
    });
  } catch (err) {
    console.warn('Hyperspeed background could not start:', err);
    return;
  }

  // Stop rendering when the tab is hidden — no point burning GPU/battery.
  document.addEventListener('visibilitychange', () => {
    if (!app) return;
    if (document.hidden) app.pause();
    else app.resume();
  });

  // No longer paused on scroll -- it's a page-wide ambient background now,
  // so it should keep running as long as the tab itself is visible
  // (handled by the visibilitychange listener above).
});
