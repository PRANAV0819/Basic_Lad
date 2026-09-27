/**
 * theme.js
 * Placement Readiness Platform - Global UI Controller (Light Theme)
 *
 * Ensures dark theme is completely removed, clears any legacy localStorage theme tokens,
 * and maintains the CodeHelp global search keyboard shortcut (Ctrl + K).
 */

(function () {
    // Clean up any legacy dark theme setting from localStorage
    try {
        localStorage.removeItem('theme');
        document.documentElement.removeAttribute('data-theme');
    } catch (e) {}

    // Global keyboard shortcut: Ctrl + K (focus search bar)
    document.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
            e.preventDefault();
            var searchInput = document.getElementById('globalSearchInput') ||
                              document.querySelector('.search-input-pill') ||
                              document.querySelector('.search-input');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
    });
})();
