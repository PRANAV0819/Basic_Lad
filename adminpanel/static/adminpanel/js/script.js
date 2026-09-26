/*
  adminpanel/static/adminpanel/js/script.js

  Vanilla JavaScript for Admin Panel interactions:
  - Mobile sidebar drawer toggle & outside-click detection
  - Form validation on login
  - Logout confirmation dialog
*/

document.addEventListener('DOMContentLoaded', () => {

    // 1. Mobile Sidebar Toggle
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('open');
        });

        // Close sidebar when clicking outside on small screens
        document.addEventListener('click', (e) => {
            if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== menuToggle) {
                sidebar.classList.remove('open');
            }
        });
    }

    // 2. Client-side Login Form Validation
    const loginForm = document.querySelector('.login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            const usernameInput = document.getElementById('username');
            const passwordInput = document.getElementById('password');

            if (usernameInput) {
                usernameInput.value = usernameInput.value.trim();
            }

            if (usernameInput && !usernameInput.value) {
                e.preventDefault();
                usernameInput.focus();
                return;
            }

            if (passwordInput && !passwordInput.value) {
                e.preventDefault();
                passwordInput.focus();
                return;
            }
        });
    }

    // 3. Logout Confirmation Feedback
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            const confirmLogout = confirm("Are you sure you want to log out of the Admin Panel?");
            if (!confirmLogout) {
                e.preventDefault();
            }
        });
    }

});
