document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".forecast-card").forEach(item => {
        item.addEventListener("click", () => {
            const locData = item.dataset.city;

            document.getElementById("locationModalText").textContent = `Set "${locData.split("|")[0]}" as your location?`;
            document.getElementById("locationData").value = locData;
        });
    });
});

