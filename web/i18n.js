// Internationalization (i18n) Module
let currentLanguage = localStorage.getItem('language') || 'en';
let translations = {};

// Make t function globally available
window.t = t;
window.setLanguage = setLanguage;
window.getCurrentLanguage = getCurrentLanguage;

// Load translations
async function loadTranslations() {
    try {
        const response = await fetch('translations.json');
        translations = await response.json();
    } catch (error) {
        console.error('Failed to load translations:', error);
    }
}

// Get translation by key
function t(key) {
    const keys = key.split('.');
    let value = translations[currentLanguage];
    
    for (const k of keys) {
        if (value && value[k]) {
            value = value[k];
        } else {
            console.warn(`Translation missing for key: ${key} in language: ${currentLanguage}`);
            return key;
        }
    }
    
    return value;
}

// Set language
function setLanguage(lang) {
    if (translations[lang]) {
        currentLanguage = lang;
        localStorage.setItem('language', lang);
        updatePageTranslations();
    }
}

// Get current language
function getCurrentLanguage() {
    return currentLanguage;
}

// Update all elements with data-i18n attribute
function updatePageTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = t(key);
        
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            if (element.hasAttribute('placeholder')) {
                element.placeholder = translation;
            } else {
                element.value = translation;
            }
        } else {
            element.textContent = translation;
        }
    });
    
    // Update language selector
    const langSelector = document.getElementById('langSelector');
    if (langSelector) {
        langSelector.value = currentLanguage;
    }
    
    // Dispatch event for custom handlers
    document.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: currentLanguage } }));
}

// Initialize language selector
function initLanguageSelector() {
    const navbar = document.querySelector('.nav-links');
    if (!navbar) return;
    
    const selector = document.createElement('select');
    selector.id = 'langSelector';
    selector.className = 'lang-selector';
    selector.innerHTML = `
        <option value="en">🇬🇧 English</option>
        <option value="el">🇬🇷 Ελληνικά</option>
    `;
    selector.value = currentLanguage;
    selector.addEventListener('change', (e) => setLanguage(e.target.value));
    
    // Insert before login button or at the end
    const loginLink = navbar.querySelector('#navLogin');
    if (loginLink) {
        navbar.insertBefore(selector, loginLink);
    } else {
        navbar.appendChild(selector);
    }
}

// Initialize i18n
async function initI18n() {
    await loadTranslations();
    initLanguageSelector();
    updatePageTranslations();
}

// Auto-initialize on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initI18n);
} else {
    initI18n();
}
