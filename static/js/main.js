// Автолистание галерей на страницах услуг
document.addEventListener("DOMContentLoaded", () => {
  if (!window.Swiper) return;
  document.querySelectorAll(".js-slider").forEach((el) => {
    const slides = el.querySelectorAll(".swiper-slide").length;
    // догружаем фото только для текущего и следующего слайда
    const reveal = (slide) => {
      const img = slide?.querySelector("img[data-src]");
      if (!img) return;
      img.srcset = img.dataset.srcset; img.src = img.dataset.src;
      img.removeAttribute("data-src"); img.removeAttribute("data-srcset");
      slide.style.setProperty("--bg", `url('${img.src}')`);
    };
    const syncVideo = (sw) => {
      reveal(sw.slides[sw.activeIndex]); reveal(sw.slides[sw.activeIndex + 1]);
      el.querySelectorAll("video").forEach((v) => v.pause());
      const v = sw.slides[sw.activeIndex]?.querySelector("video");
      if (v) { v.currentTime = 0; v.play().catch(() => {}); }
    };
    new Swiper(el, {
      loop: slides > 1,
      speed: 600,
      effect: "fade",
      fadeEffect: { crossFade: true },
      autoplay: slides > 1 ? { delay: +el.dataset.delay || 2000, disableOnInteraction: false, pauseOnMouseEnter: true } : false,
      pagination: { el: el.querySelector(".swiper-pagination"), clickable: true, dynamicBullets: slides > 8 },
      grabCursor: true,
      on: { init: syncVideo, slideChangeTransitionStart: syncVideo },
    });
  });
});
