// weather_earth_particles.js
// Simple weather and earth-themed particle animation using Canvas

window.addEventListener('DOMContentLoaded', () => {
  const canvas = document.createElement('canvas');
  canvas.id = 'particle-canvas';
  canvas.style.position = 'fixed';
  canvas.style.top = 0;
  canvas.style.left = 0;
  canvas.style.width = '100vw';
  canvas.style.height = '100vh';
  canvas.style.zIndex = '-1';
  document.body.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  let width = window.innerWidth;
  let height = window.innerHeight;
  canvas.width = width;
  canvas.height = height;

  // Load cloud image
  const cloudImage = new Image();
  cloudImage.src = 'data:image/png;base64,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';
  let cloudImageLoaded = false;
  
  cloudImage.onload = () => {
    cloudImageLoaded = true;
  };

  window.addEventListener('resize', () => {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
  });

  // Particle types: clouds, raindrops, earth orbs
  const PARTICLE_TYPES = ['cloud', 'raindrop', 'earth'];

  function randomType() {
    const r = Math.random();
    if (r < 0.4) return 'cloud';
    if (r < 0.8) return 'raindrop';
    return 'earth';
  }

  function randomColor(type) {
    if (type === 'cloud') return 'rgba(255,255,255,0.7)';
    if (type === 'raindrop') return 'rgba(100,180,255,0.7)';
    if (type === 'earth') return 'rgba(34,139,34,0.7)';
    return 'white';
  }

  class Particle {
    constructor() {
      this.type = randomType();
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.radius = this.type === 'cloud' ? 30 + Math.random() * 30 : (this.type === 'earth' ? 10 + Math.random() * 10 : 2 + Math.random() * 2);
      this.speedY = this.type === 'raindrop' ? 2 + Math.random() * 3 : (this.type === 'cloud' ? 0.2 + Math.random() * 0.3 : 0.1 + Math.random() * 0.2);
      this.speedX = this.type === 'cloud' ? 0.2 + Math.random() * 0.2 : (this.type === 'earth' ? 0.1 * (Math.random() - 0.5) : 0);
      this.color = randomColor(this.type);
    }
    update() {
      this.x += this.speedX;
      this.y += this.speedY;
      if (this.type === 'raindrop' && this.y > height) {
        this.x = Math.random() * width;
        this.y = -10;
      }
      if (this.type === 'cloud' && this.x > width + 60) {
        this.x = -60;
        this.y = Math.random() * height * 0.5;
      }
      if (this.type === 'earth' && (this.x < 0 || this.x > width || this.y < 0 || this.y > height)) {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
      }
    }
    draw(ctx) {
      ctx.save();
      if (this.type === 'cloud' && cloudImageLoaded) {
        // Draw cloud image instead of circle
        const size = this.radius * 2;
        ctx.globalAlpha = 0.7;
        ctx.drawImage(cloudImage, this.x - this.radius, this.y - this.radius, size, size);
        ctx.globalAlpha = 1;
      } else {
        // Draw shapes for raindrops and earth orbs
        ctx.beginPath();
        if (this.type === 'cloud') {
          ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
        } else if (this.type === 'raindrop') {
          ctx.ellipse(this.x, this.y, this.radius * 0.5, this.radius * 2, 0, 0, 2 * Math.PI);
        } else if (this.type === 'earth') {
          ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
        }
        ctx.fillStyle = this.color;
        ctx.fill();
      }
      ctx.restore();
    }
  }

  const particles = [];
  for (let i = 0; i < 60; i++) {
    particles.push(new Particle());
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);
    for (const p of particles) {
      p.update();
      p.draw(ctx);
    }
    requestAnimationFrame(animate);
  }
  animate();
});
