const logoutForm = document.getElementById("logoutForm");

if (logoutForm) {


logoutForm.addEventListener("submit", function (event) {

    const confirmed = window.confirm(
        "Are you sure you want to log out?"
    );

    if (!confirmed) {
        event.preventDefault();
    }

});

}
