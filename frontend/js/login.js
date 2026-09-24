const loginForm = document.getElementById("loginForm");

if (loginForm) {
loginForm.addEventListener("submit", function(event) {

    const studentNumber = document.getElementById("student_number");
    const adminId = document.getElementById("admin_id");
    const password = document.getElementById("password");

    if (studentNumber && studentNumber.value.trim() === "") {
        event.preventDefault();
        alert("Please enter your student number.");
        return;
    }

    if (adminId && adminId.value.trim() === "") {
        event.preventDefault();
        alert("Please enter your admin ID.");
        return;
    }

    if (password && password.value.trim() === "") {
        event.preventDefault();
        alert("Please enter your password.");
    }
});

}
