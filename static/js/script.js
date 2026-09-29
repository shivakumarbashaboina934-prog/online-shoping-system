document.addEventListener("DOMContentLoaded", () => {
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = "0";
            alert.style.transition = "opacity .5s";
        }, 3500);
    });
});
