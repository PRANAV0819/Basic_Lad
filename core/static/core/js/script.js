/*
  core/static/core/js/script.js

  WHAT: Vanilla JavaScript for the landing page.

  WHY:  We need a small amount of interactivity — specifically the
        mobile hamburger menu toggle. This does NOT use any library.

  WHERE: Served by Django's staticfiles at /static/core/js/script.js
         Loaded at the bottom of home.html (before </body>).
         Loading it at the bottom is intentional: the HTML DOM elements
         (like #hamburger and #mobileMenu) must already exist in the page
         before our script tries to find them with document.getElementById.

  HOW:  1. Browser parses HTML top-to-bottom.
           2. Reaches <script src="...script.js"> at the bottom of <body>.
           3. Downloads and executes script.js.
           4. Script runs: finds the hamburger button and mobile menu,
              attaches a click event listener.
           5. When user clicks the hamburger, the mobile menu toggles
              the CSS class 'open' (defined in style.css as display: flex).
*/


/* --- Hamburger Menu Toggle --- */

const hamburger   = document.getElementById('hamburger');
const mobileMenu  = document.getElementById('mobileMenu');

if (hamburger && mobileMenu) {
    /*
      addEventListener('click', callback) attaches a function that runs
      every time the element is clicked. We use an arrow function here.
      Arrow functions (()=>{}) are a modern JS syntax — equivalent to
      function() {} but shorter.
    */
    hamburger.addEventListener('click', () => {
        /*
          classList.toggle('open') adds the class if it's not there,
          and removes it if it is. This is cleaner than manually
          checking and setting .className.
        */
        mobileMenu.classList.toggle('open');

        /*
          Update aria-expanded for accessibility.
          This tells screen readers whether the menu is open or closed.
        */
        const isOpen = mobileMenu.classList.contains('open');
        hamburger.setAttribute('aria-expanded', isOpen);
    });

    /*
      Close mobile menu when any nav link inside it is clicked.
      This gives a better UX — clicking "About" scrolls to the section
      AND closes the menu automatically.
    */
    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('open');
            hamburger.setAttribute('aria-expanded', false);
        });
    });
}


/* --- Sign In Dropdowns (Desktop & Hero) --- */

const dropdowns = document.querySelectorAll('.dropdown');

dropdowns.forEach(dropdown => {
    const toggleBtn = dropdown.querySelector('.dropdown-toggle');
    if (!toggleBtn) return;

    // Toggle on button click (useful for touch screens and keyboard users)
    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = dropdown.classList.contains('open');

        // Close any other open dropdowns first
        dropdowns.forEach(d => {
            if (d !== dropdown) {
                d.classList.remove('open');
                const btn = d.querySelector('.dropdown-toggle');
                if (btn) btn.setAttribute('aria-expanded', 'false');
            }
        });

        // Toggle current dropdown
        dropdown.classList.toggle('open', !isOpen);
        toggleBtn.setAttribute('aria-expanded', !isOpen);
    });
});

// Close all open dropdowns when clicking outside
document.addEventListener('click', (e) => {
    dropdowns.forEach(dropdown => {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove('open');
            const toggleBtn = dropdown.querySelector('.dropdown-toggle');
            if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
        }
    });
});

// Close dropdowns on 'Escape' key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('open');
            const toggleBtn = dropdown.querySelector('.dropdown-toggle');
            if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
        });
    }
});


/* --- Mobile Sign In Dropdown --- */

const mobileDropdown = document.getElementById('mobileSignInDropdown');
if (mobileDropdown) {
    const mobileToggle = mobileDropdown.querySelector('.mobile-dropdown-toggle');
    if (mobileToggle) {
        mobileToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            mobileDropdown.classList.toggle('open');
        });
    }
}

