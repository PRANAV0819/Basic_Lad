/*
  student/static/student/js/script.js

  Vanilla JavaScript for Student Module interactions:
  - Mobile sidebar drawer toggle & outside-click detection
  - Form validation and input trimming
  - Password confirmation check
  - Logout confirmation
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

    // 2. Client-side Form Sanitization
    const forms = document.querySelectorAll('.auth-form, .profile-form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const inputs = form.querySelectorAll('input:not([type="password"])');
            inputs.forEach(input => {
                input.value = input.value.trim();
            });

            // Password confirmation check on signup
            const pwd = form.querySelector('#password');
            const confirmPwd = form.querySelector('#confirm_password');
            if (pwd && confirmPwd) {
                if (pwd.value !== confirmPwd.value) {
                    e.preventDefault();
                    alert("Passwords do not match. Please re-enter.");
                    confirmPwd.focus();
                }
            }
        });
    });

    // 3. Logout Confirmation Dialog
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            const confirmLogout = confirm("Are you sure you want to log out of your student account?");
            if (!confirmLogout) {
                e.preventDefault();
            }
        });
    }

});
