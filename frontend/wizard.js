// Wizard State Management
let currentStep = 0;
const totalSteps = 6; // Vitals, Cardio, Digital, Lifestyle, Mental, Habits

// Initialize wizard on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeWizard();
    attachOptionListeners();
});

function initializeWizard() {
    showStep(0);
    updateProgress();

    // Add navigation button listeners
    document.getElementById('btn-prev')?.addEventListener('click', () => navigateStep(-1));
    document.getElementById('btn-next')?.addEventListener('click', () => navigateStep(1));
}

function showStep(stepIndex) {
    const sections = document.querySelectorAll('.form-section');
    sections.forEach((section, index) => {
        if (index === stepIndex) {
            section.classList.add('active');
            section.classList.remove('hidden');
            section.style.animationDelay = '0s';
        } else {
            section.classList.remove('active');
            section.classList.add('hidden');
        }
    });

    currentStep = stepIndex;
    updateProgress();
    updateNavigationButtons();
}

function navigateStep(direction) {
    const newStep = currentStep + direction;
    if (newStep >= 0 && newStep < totalSteps) {
        showStep(newStep);
        // Scroll to top of form smoothly
        document.getElementById('assessment-form').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function updateProgress() {
    const progressFill = document.querySelector('.progress-fill');
    const progressSteps = document.querySelectorAll('.progress-step');

    // Update progress bar
    const percentage = ((currentStep + 1) / totalSteps) * 100;
    if (progressFill) {
        progressFill.style.width = `${percentage}%`;
    }

    // Update step indicators
    progressSteps.forEach((step, index) => {
        const circle = step.querySelector('.step-circle');
        // Ensure number is wrapped in span for CSS targeting
        if (circle && !circle.querySelector('span')) {
            circle.innerHTML = `<span>${index + 1}</span>`;
        }

        step.classList.remove('active', 'completed');
        if (index < currentStep) {
            step.classList.add('completed');
        } else if (index === currentStep) {
            step.classList.add('active');
        }
    });
}

function updateNavigationButtons() {
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const btnSubmit = document.querySelector('.cta-button');

    // Show/hide previous button
    if (btnPrev) {
        btnPrev.style.display = currentStep === 0 ? 'none' : 'flex';
    }

    // Show next or submit button
    if (currentStep === totalSteps - 1) {
        if (btnNext) btnNext.style.display = 'none';
        if (btnSubmit) btnSubmit.style.display = 'flex';
    } else {
        if (btnNext) btnNext.style.display = 'flex';
        if (btnSubmit) btnSubmit.style.display = 'none';
    }
}

// Interactive Option Buttons
function attachOptionListeners() {
    // Convert all select elements to custom option buttons
    document.querySelectorAll('select').forEach(select => {
        if (select.id.startsWith('q')) {
            createOptionButtons(select);
        }
    });
}

function createOptionButtons(selectElement) {
    const parent = selectElement.parentElement;
    const optionGroup = document.createElement('div');
    optionGroup.className = 'option-group';

    // Create buttons for Yes/No options
    ['No', 'Yes'].forEach((label, index) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'option-button';
        button.textContent = label;
        button.dataset.value = index === 0 ? 'false' : 'true';

        button.addEventListener('click', () => {
            // Update select value
            selectElement.value = button.dataset.value;

            // Update visual state
            optionGroup.querySelectorAll('.option-button').forEach(btn => {
                btn.classList.remove('selected');
            });
            button.classList.add('selected');

            // Trigger change event
            selectElement.dispatchEvent(new Event('change'));
        });

        optionGroup.appendChild(button);
    });

    // Hide original select and add option buttons
    selectElement.style.display = 'none';
    parent.appendChild(optionGroup);

    // Set initial selection if value exists
    if (selectElement.value) {
        const selectedBtn = optionGroup.querySelector(`[data-value="${selectElement.value}"]`);
        if (selectedBtn) selectedBtn.classList.add('selected');
    }
}

// Enhanced Input Interactions
document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener('focus', (e) => {
        e.target.parentElement.style.transform = 'scale(1.02)';
        e.target.parentElement.style.transition = 'transform 0.2s ease';
    });

    input.addEventListener('blur', (e) => {
        e.target.parentElement.style.transform = 'scale(1)';
    });
});

// Keyboard Navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' && currentStep < totalSteps - 1) {
        navigateStep(1);
    } else if (e.key === 'ArrowLeft' && currentStep > 0) {
        navigateStep(-1);
    }
});
