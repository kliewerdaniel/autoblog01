'use client';

import { useRef, useEffect } from 'react';

const GlitchBackground = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Glitch effect variables
    let time = 0;
    let frameCount = 0;

    const animate = () => {
      time += 0.01;
      frameCount++;

      // Clear canvas with slight trail effect
      ctx.fillStyle = 'rgba(10, 10, 10, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Create glitch blocks
      for (let i = 0; i < 20; i++) {
        const x = (Math.sin(time + i * 0.5) * canvas.width * 0.4) + canvas.width * 0.5;
        const y = (Math.cos(time * 0.7 + i * 0.3) * canvas.height * 0.4) + canvas.height * 0.5;
        const size = Math.sin(time * 2 + i) * 50 + 100;

        // Random color from glitch palette
        const colors = ['#00fff7', '#ff00ff', '#39ff14', '#ff073a'];
        ctx.fillStyle = colors[i % colors.length];

        // Add some randomness
        const glitchX = x + (Math.random() - 0.5) * 20;
        const glitchY = y + (Math.random() - 0.5) * 20;

        ctx.fillRect(glitchX, glitchY, size, size);

        // Add glow effect
        ctx.shadowColor = colors[i % colors.length];
        ctx.shadowBlur = 20;
        ctx.fillRect(glitchX, glitchY, size, size);
        ctx.shadowBlur = 0;
      }

      // Add scan lines
      if (frameCount % 3 === 0) {
        ctx.strokeStyle = '#00fff7';
        ctx.lineWidth = 1;
        for (let y = 0; y < canvas.height; y += 4) {
          if (Math.random() > 0.7) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
          }
        }
      }

      // Add noise
      const imageData = ctx.createImageData(canvas.width, canvas.height);
      const data = imageData.data;

      for (let i = 0; i < data.length; i += 4) {
        if (Math.random() > 0.95) {
          const noise = Math.random() * 255;
          data[i] = noise;     // red
          data[i + 1] = noise; // green
          data[i + 2] = noise; // blue
          data[i + 3] = 255;   // alpha
        }
      }

      ctx.putImageData(imageData, 0, 0);

      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full pointer-events-none z-0"
      style={{ opacity: 0.3 }}
    />
  );
};

export default GlitchBackground;
