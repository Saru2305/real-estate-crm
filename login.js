
const togglePassword = document.getElementById("togglePassword");
const password = document.getElementById("password");

togglePassword.addEventListener("click", function () {

    if (password.type === "password") {

        password.type = "text";
        togglePassword.textContent = "🙈";

    } else {

        password.type = "password";
        togglePassword.textContent = "👁";

    }

});

