/* ============================================================
   VeloraDrive – Main JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ========== Navbar scroll effect ==========
  const nav = document.getElementById('mainNav');
  if (nav) {
    const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 60);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ========== Scroll-to-top button ==========
  const scrollBtn = document.getElementById('scrollTopBtn');
  if (scrollBtn) {
    window.addEventListener('scroll', () => {
      scrollBtn.classList.toggle('show', window.scrollY > 400);
    }, { passive: true });
    scrollBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  // ========== Toast auto-dismiss ==========
  document.querySelectorAll('.toast.show').forEach(el => {
    setTimeout(() => {
      const toast = bootstrap.Toast.getOrCreateInstance(el, { delay: 4000 });
      toast.show();
      setTimeout(() => toast.hide(), 4500);
    }, 100);
  });

  // ========== AOS-style scroll animations ==========
  const animatedEls = document.querySelectorAll('[data-aos]');
  if (animatedEls.length) {
    const delays = {};
    animatedEls.forEach(el => {
      const d = el.dataset.aosDelay;
      if (d) {
        delays.set ? delays.set(el, d) : (delays[el] = d);
        el.style.transitionDelay = d + 'ms';
      }
    });
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('aos-animate');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    animatedEls.forEach(el => observer.observe(el));
  }

  // ========== Counter animation ==========
  const counters = document.querySelectorAll('.stat-number[data-target]');
  if (counters.length) {
    const counterObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(el => counterObserver.observe(el));
  }

  function animateCounter(el) {
    const target = parseInt(el.dataset.target, 10);
    const duration = 2000;
    const start  = performance.now();
    const step = (timestamp) => {
      const progress = Math.min((timestamp - start) / duration, 1);
      const eased    = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target).toLocaleString();
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target.toLocaleString();
    };
    requestAnimationFrame(step);
  }

  // ========== Loading overlay on form submit ==========
  const overlay  = document.getElementById('loadingOverlay');
  const formsWithLoading = document.querySelectorAll('form[data-loading]');
  formsWithLoading.forEach(form => {
    form.addEventListener('submit', () => {
      if (overlay) overlay.classList.remove('d-none');
    });
  });

  // ========== Date input min today ==========
  const today = new Date().toISOString().split('T')[0];
  document.querySelectorAll('input[type="date"]').forEach(input => {
    if (!input.min) input.min = today;
  });

  // ========== Client-side form validation highlight ==========
  document.querySelectorAll('form[novalidate]').forEach(form => {
    form.addEventListener('submit', (e) => {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
      }
      form.classList.add('was-validated');
    });
  });

  // ========== Smooth active nav link ==========
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
      link.style.color = 'var(--accent)';
    }
  });

  // ========== Image lazy-load fallback ==========
  document.querySelectorAll('img[loading="lazy"]').forEach(img => {
    img.addEventListener('error', () => {
      img.src = 'https://images.pexels.com/photos/3802510/pexels-photo-3802510.jpeg';
    });
  });

});
