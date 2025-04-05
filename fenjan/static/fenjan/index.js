// static/fenjan/index.js

// Message handler for Django messages
function showNextMessage() {
    const messages = document.querySelectorAll(".stored_messages");
    for (let i = 0; i < messages.length; i++) {
        if (messages[i].style.display === "none") {
            messages[i].style.display = "block";
            return; // Show only one message at a time
        } else {
            messages[i].remove(); // Remove the closed message from DOM
        }
    }
}

document.addEventListener("DOMContentLoaded", function () {
    showNextMessage(); // Show the first message when the page loads
});

// Make showNextMessage globally accessible (needed for inline HTML onclick)
window.showNextMessage = showNextMessage;


// Form handling
function submitForm(event) {
    event.preventDefault();  // Prevent default area href behavior

    const form = document.getElementById("myform");

    if (validateForm(form)) {
        form.submit();
    } else {
        console.error("Form validation failed");
    }
}

function validateForm(form) {
    const name = form.querySelector("#name").value.trim();
    const email = form.querySelector("#email").value.trim();
    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;

    if (name === "") {
        alert("Name is required");
        return false;
    }

    if (email === "" || !emailPattern.test(email)) {
        alert("Valid email is required");
        return false;
    }

    return true;
}
