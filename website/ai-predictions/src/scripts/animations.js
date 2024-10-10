import anime from 'animejs/lib/anime.es.js';

document.addEventListener('DOMContentLoaded', () => {
  // Animate league sections
  anime({
    targets: 'section',
    opacity: [0, 1],
    translateY: [20, 0],
    easing: 'easeOutExpo',
    duration: 1000,
    delay: anime.stagger(200)
  });

  // Animate prediction cards
  anime({
    targets: '.bg-gray-700.rounded-lg',
    opacity: [0, 1],
    scale: [0.9, 1],
    easing: 'easeOutExpo',
    duration: 800,
    delay: anime.stagger(50, {start: 300, grid: [5, 1], from: 'center'})
  });
});