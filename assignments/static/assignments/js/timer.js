/**
 * assignments/static/assignments/js/timer.js
 *
 * Placement Readiness Platform - Exam Timer & Examination Interface Script
 * Written in 100% Vanilla JavaScript (No external libraries, No jQuery).
 *
 * Responsibilities:
 * 1. Synchronize countdown timer based on server-injected remaining seconds.
 * 2. Visual warning when less than 2 minutes remain.
 * 3. Auto-submit form when timer reaches 00:00.
 * 4. Question palette interactivity (jump to question, answered state tracking).
 */

document.addEventListener('DOMContentLoaded', function () {
    const timerElement = document.getElementById('timerDisplay');
    const testForm = document.getElementById('testForm');
    const submitBtn = document.getElementById('submitBtn');

    if (timerElement && testForm) {
        // Read remaining seconds passed from Django view
        let remainingSeconds = parseInt(timerElement.getAttribute('data-remaining-seconds'), 10);
        if (isNaN(remainingSeconds) || remainingSeconds < 0) {
            remainingSeconds = 0;
        }

        let isSubmitting = false;

        function updateDisplay() {
            const hours = Math.floor(remainingSeconds / 3600);
            const minutes = Math.floor((remainingSeconds % 3600) / 60);
            const seconds = remainingSeconds % 60;

            let timeString = '';
            if (hours > 0) {
                timeString += String(hours).padStart(2, '0') + ':';
            }
            timeString += String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
            timerElement.textContent = timeString;

            // Visual warning when time is low (<= 2 minutes)
            if (remainingSeconds <= 120 && remainingSeconds > 0) {
                timerElement.classList.add('timer-warning');
            } else {
                timerElement.classList.remove('timer-warning');
            }

            // Expiry condition
            if (remainingSeconds <= 0) {
                clearInterval(timerInterval);
                if (!isSubmitting) {
                    isSubmitting = true;
                    timerElement.textContent = '00:00';
                    alert('Time is up! Your test will now be submitted automatically.');
                    testForm.submit();
                }
            }
        }

        // Initial render
        updateDisplay();

        // 1-second ticker
        const timerInterval = setInterval(function () {
            if (remainingSeconds > 0) {
                remainingSeconds--;
                updateDisplay();
            }
        }, 1000);

        // Prevent double submit on manual button click
        testForm.addEventListener('submit', function () {
            isSubmitting = true;
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Submitting...';
            }
        });
    }

    // =========================================================
    // Question Palette & Selection Tracking
    // =========================================================
    const questionCards = document.querySelectorAll('.question-card');
    const paletteButtons = document.querySelectorAll('.palette-btn');

    // Function to update palette answered states
    function refreshAnsweredState() {
        questionCards.forEach(function (card) {
            const qId = card.getAttribute('data-question-id');
            const inputs = card.querySelectorAll('input[type="radio"], input[type="checkbox"]');
            let isAnswered = false;

            inputs.forEach(function (input) {
                const label = input.closest('.option-choice-item');
                if (input.checked) {
                    isAnswered = true;
                    if (label) label.classList.add('selected');
                } else {
                    if (label) label.classList.remove('selected');
                }
            });

            const paletteBtn = document.querySelector('.palette-btn[data-question-id="' + qId + '"]');
            if (paletteBtn) {
                if (isAnswered) {
                    paletteBtn.classList.add('answered');
                } else {
                    paletteBtn.classList.remove('answered');
                }
            }
        });
    }

    // Listen to changes on all choices
    document.querySelectorAll('.option-choice-item input').forEach(function (input) {
        input.addEventListener('change', refreshAnsweredState);
    });

    // Jump to question on palette click
    paletteButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const targetId = btn.getAttribute('data-question-id');
            const targetCard = document.querySelector('.question-card[data-question-id="' + targetId + '"]');
            if (targetCard) {
                targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    });

    // Initial check on load
    refreshAnsweredState();
});
