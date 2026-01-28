document.addEventListener("DOMContentLoaded", () => {

    // Animation d’apparition des cartes
    document.querySelectorAll(".card").forEach(card => {
        card.style.opacity = 0;
        card.style.transform = "translateY(20px)";
        setTimeout(() => {
            card.style.transition = "0.6s";
            card.style.opacity = 1;
            card.style.transform = "translateY(0)";
        }, 200);
    });

    // Gantt dynamique
    document.querySelectorAll(".bar").forEach(bar => {
        const duration = bar.dataset.duration;
        bar.style.width = (duration * 40) + "px";
    });

});
