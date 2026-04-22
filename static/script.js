// ===================================
// SS RAIL WORKS - script.js
// Final Version
// ===================================

document.addEventListener("DOMContentLoaded", function () {

    // ===================================
    // MOBILE MENU TOGGLE
    // ===================================

    const menuBtn = document.getElementById("menuBtn");
    const navLinks = document.getElementById("navLinks");

    if (menuBtn && navLinks) {
        menuBtn.addEventListener("click", function () {
            navLinks.classList.toggle("show");
        });
    }

    // ===================================
    // PROJECT SEARCH
    // ===================================

    const searchInput = document.getElementById("searchInput");
    const tableRows = document.querySelectorAll("#projectTable tbody tr");

    if (searchInput && tableRows.length > 0) {

        searchInput.addEventListener("keyup", function () {

            let value = searchInput.value.toLowerCase().trim();

            tableRows.forEach(row => {

                let text = row.innerText.toLowerCase();

                if (text.includes(value)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }

            });

        });

    }

    // ===================================
    // PROGRESS BAR AUTO FILL
    // ===================================

    const bars = document.querySelectorAll(".fill");

    bars.forEach(bar => {

        const progress = bar.getAttribute("data-progress");

        if (progress !== null) {

            setTimeout(() => {
                bar.style.width = progress + "%";
            }, 200);

        }

    });

    // ===================================
    // LOGOUT CONFIRMATION
    // ===================================

    const logoutLinks = document.querySelectorAll(".logout-link");

    logoutLinks.forEach(link => {

        link.addEventListener("click", function (e) {

            let ok = confirm("Are you sure you want to logout?");

            if (!ok) {
                e.preventDefault();
            }

        });

    });

    // ===================================
    // DELETE CONFIRMATION
    // ===================================

    const deleteLinks = document.querySelectorAll(".delete-link");

    deleteLinks.forEach(link => {

        link.addEventListener("click", function (e) {

            let ok = confirm("Delete this project permanently?");

            if (!ok) {
                e.preventDefault();
            }

        });

    });

    // ===================================
    // FLASH MESSAGE AUTO HIDE
    // ===================================

    const flashMessages = document.querySelectorAll(".flash, .flash-msg");

    flashMessages.forEach(msg => {

        setTimeout(() => {

            msg.style.transition = "0.5s";
            msg.style.opacity = "0";

            setTimeout(() => {
                msg.style.display = "none";
            }, 500);

        }, 3000);

    });

    // ===================================
    // TODAY DATE
    // ===================================

    const dateBox = document.getElementById("todayDate");

    if (dateBox) {

        const today = new Date();

        const options = {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric"
        };

        dateBox.innerText = today.toLocaleDateString("en-US", options);

    }

    // ===================================
    // INPUT NUMBER LIMIT (0 to 100)
    // ===================================

    const progressInput = document.querySelector('input[name="progress"]');

    if (progressInput) {

        progressInput.addEventListener("input", function () {

            let val = parseInt(this.value);

            if (val > 100) this.value = 100;
            if (val < 0) this.value = 0;

        });

    }

    // ===================================
    // TABLE ROW HOVER EFFECT
    // ===================================

    tableRows.forEach(row => {

        row.addEventListener("mouseenter", function () {
            row.style.background = "#f8fafc";
        });

        row.addEventListener("mouseleave", function () {
            row.style.background = "";
        });

    });

});