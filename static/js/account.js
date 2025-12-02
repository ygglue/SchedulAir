document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".forecast-card").forEach(item => {
        item.addEventListener("click", () => {
            const locData = item.dataset.city;

            document.getElementById("locationModalText").textContent = `Set "${locData.split("|")[0]}" as your location?`;
            document.getElementById("locationData").value = locData;
        });
    });
});
document.addEventListener("DOMContentLoaded", () => {
    
    const editForm = document.getElementById("editProfileForm");

    editForm.addEventListener("submit", function (e) {
        e.preventDefault();

        fetch("/account/edit/", {
            method: "POST",
            body: new FormData(editForm),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert("Profile updated successfully!");

                location.reload();
            } else {
                console.log(data.errors);
                alert("Error updating profile.");
            }
        });
    });

});

