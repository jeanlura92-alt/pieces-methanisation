/**
 * Cookie Consent Banner - GDPR/ePrivacy Compliant
 * Lightweight vanilla JavaScript implementation
 * Compatible with French ePrivacy directive (directive 2002/58/CE)
 */

(function() {
  'use strict';

  // Configuration
  const CONSENT_COOKIE_NAME = 'cookie_consent';
  const CONSENT_DURATION_DAYS = 395; // 13 months (CNIL recommendation)
  
  // Consent states
  const CONSENT_STATES = {
    ACCEPTED: 'accepted',
    REFUSED: 'refused',
    PARTIAL: 'partial'
  };

  // CSS styles to inject
  const bannerStyles = `
    .cookie-consent-banner {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      background: linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%);
      color: #ffffff;
      padding: 24px 20px;
      box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3);
      z-index: 10000;
      transform: translateY(100%);
      transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .cookie-consent-banner.show {
      transform: translateY(0);
    }

    .cookie-consent-content {
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      gap: 24px;
      flex-wrap: wrap;
    }

    .cookie-consent-text {
      flex: 1;
      min-width: 280px;
    }

    .cookie-consent-text h3 {
      margin: 0 0 8px 0;
      font-size: 18px;
      font-weight: 700;
      color: #ffffff;
    }

    .cookie-consent-text p {
      margin: 0;
      font-size: 14px;
      line-height: 1.6;
      color: #e0e0e0;
    }

    .cookie-consent-text a {
      color: #4da6ff;
      text-decoration: underline;
      font-weight: 600;
    }

    .cookie-consent-text a:hover {
      color: #80bfff;
    }

    .cookie-consent-actions {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      align-items: center;
    }

    .cookie-consent-btn {
      padding: 12px 24px;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      white-space: nowrap;
      font-family: inherit;
    }

    .cookie-consent-btn-accept {
      background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
      color: #ffffff;
    }

    .cookie-consent-btn-accept:hover {
      background: linear-gradient(135deg, #238b3a 0%, #1ba87e 100%);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
    }

    .cookie-consent-btn-refuse {
      background: transparent;
      color: #ffffff;
      border: 2px solid rgba(255, 255, 255, 0.3);
    }

    .cookie-consent-btn-refuse:hover {
      background: rgba(255, 255, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.5);
    }

    .cookie-consent-btn-customize {
      background: transparent;
      color: #4da6ff;
      border: 2px solid #4da6ff;
    }

    .cookie-consent-btn-customize:hover {
      background: rgba(77, 166, 255, 0.1);
      border-color: #80bfff;
      color: #80bfff;
    }

    /* Modal styles for customization */
    .cookie-consent-modal {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.75);
      z-index: 10001;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.3s ease, visibility 0.3s ease;
    }

    .cookie-consent-modal.show {
      opacity: 1;
      visibility: visible;
    }

    .cookie-consent-modal-content {
      background: #ffffff;
      border-radius: 12px;
      max-width: 600px;
      width: 100%;
      max-height: 80vh;
      overflow-y: auto;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
      transform: scale(0.9);
      transition: transform 0.3s ease;
    }

    .cookie-consent-modal.show .cookie-consent-modal-content {
      transform: scale(1);
    }

    .cookie-consent-modal-header {
      padding: 24px;
      border-bottom: 1px solid #e0e0e0;
      background: linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%);
      color: #ffffff;
      border-radius: 12px 12px 0 0;
    }

    .cookie-consent-modal-header h2 {
      margin: 0;
      font-size: 22px;
      font-weight: 700;
    }

    .cookie-consent-modal-body {
      padding: 24px;
      color: #333333;
    }

    .cookie-category {
      margin-bottom: 24px;
      padding-bottom: 24px;
      border-bottom: 1px solid #e0e0e0;
    }

    .cookie-category:last-child {
      border-bottom: none;
      margin-bottom: 0;
      padding-bottom: 0;
    }

    .cookie-category-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }

    .cookie-category-title {
      font-size: 16px;
      font-weight: 700;
      color: #1a1a2e;
      margin: 0;
    }

    .cookie-category-description {
      font-size: 14px;
      line-height: 1.6;
      color: #666666;
      margin: 0;
    }

    .cookie-toggle {
      position: relative;
      display: inline-block;
      width: 50px;
      height: 26px;
    }

    .cookie-toggle input {
      opacity: 0;
      width: 0;
      height: 0;
    }

    .cookie-toggle-slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #ccc;
      transition: 0.3s;
      border-radius: 26px;
    }

    .cookie-toggle-slider:before {
      position: absolute;
      content: "";
      height: 20px;
      width: 20px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: 0.3s;
      border-radius: 50%;
    }

    .cookie-toggle input:checked + .cookie-toggle-slider {
      background-color: #28a745;
    }

    .cookie-toggle input:checked + .cookie-toggle-slider:before {
      transform: translateX(24px);
    }

    .cookie-toggle input:disabled + .cookie-toggle-slider {
      cursor: not-allowed;
      opacity: 0.5;
    }

    .cookie-required-badge {
      display: inline-block;
      background: #6c757d;
      color: white;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      margin-left: 8px;
    }

    .cookie-consent-modal-footer {
      padding: 20px 24px;
      background: #f8f9fa;
      border-top: 1px solid #e0e0e0;
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      border-radius: 0 0 12px 12px;
    }

    /* Responsive design */
    @media (max-width: 768px) {
      .cookie-consent-content {
        flex-direction: column;
        align-items: flex-start;
      }

      .cookie-consent-actions {
        width: 100%;
        justify-content: stretch;
      }

      .cookie-consent-btn {
        flex: 1;
        text-align: center;
      }

      .cookie-consent-modal-content {
        max-height: 90vh;
      }
    }
  `;

  // Cookie management utilities
  const CookieManager = {
    set: function(name, value, days) {
      const date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      const expires = "expires=" + date.toUTCString();
      document.cookie = name + "=" + value + ";" + expires + ";path=/;SameSite=Lax";
    },

    get: function(name) {
      const nameEQ = name + "=";
      const ca = document.cookie.split(';');
      for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
      }
      return null;
    },

    delete: function(name) {
      document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;";
    }
  };

  // Consent Manager
  const ConsentManager = {
    saveConsent: function(preferences) {
      const consentData = {
        timestamp: new Date().toISOString(),
        preferences: preferences
      };
      CookieManager.set(CONSENT_COOKIE_NAME, JSON.stringify(consentData), CONSENT_DURATION_DAYS);
      this.applyConsent(preferences);
    },

    getConsent: function() {
      const consent = CookieManager.get(CONSENT_COOKIE_NAME);
      if (!consent) return null;
      
      try {
        const data = JSON.parse(consent);
        // Check if consent is still valid (13 months)
        const consentDate = new Date(data.timestamp);
        const now = new Date();
        const daysDiff = (now - consentDate) / (1000 * 60 * 60 * 24);
        
        if (daysDiff > CONSENT_DURATION_DAYS) {
          CookieManager.delete(CONSENT_COOKIE_NAME);
          return null;
        }
        
        return data.preferences;
      } catch(e) {
        return null;
      }
    },

    applyConsent: function(preferences) {
      // Block or allow third-party scripts based on consent
      if (preferences.analytics === false) {
        this.blockAnalytics();
      } else if (preferences.analytics === true) {
        this.allowAnalytics();
      }

      // Note: Stripe cookies are managed by Stripe itself during checkout
      // We inform user but don't block Stripe as it's essential for payment
      if (preferences.stripe === false) {
        console.warn('Stripe cookies refused - Payment functionality may be limited');
      }

      // Dispatch custom event for other scripts to listen to
      window.dispatchEvent(new CustomEvent('cookieConsentUpdated', {
        detail: preferences
      }));
    },

    blockAnalytics: function() {
      // Block Google Analytics if present
      if (window.gtag) {
        window['ga-disable-GA_MEASUREMENT_ID'] = true;
      }
      
      // Remove existing analytics cookies
      const analyticsCookies = ['_ga', '_gid', '_gat'];
      analyticsCookies.forEach(cookie => CookieManager.delete(cookie));
    },

    allowAnalytics: function() {
      // Enable Google Analytics if present
      if (window.gtag) {
        window['ga-disable-GA_MEASUREMENT_ID'] = false;
      }
    }
  };

  // Banner UI
  const BannerUI = {
    banner: null,
    modal: null,

    injectStyles: function() {
      if (document.getElementById('cookie-consent-styles')) return;
      const style = document.createElement('style');
      style.id = 'cookie-consent-styles';
      style.textContent = bannerStyles;
      document.head.appendChild(style);
    },

    createBanner: function() {
      const banner = document.createElement('div');
      banner.className = 'cookie-consent-banner';
      banner.setAttribute('role', 'dialog');
      banner.setAttribute('aria-label', 'Bandeau de consentement aux cookies');
      banner.innerHTML = `
        <div class="cookie-consent-content">
          <div class="cookie-consent-text">
            <h3>🍪 Gestion des cookies</h3>
            <p>
              Nous utilisons des cookies pour garantir le bon fonctionnement du site et pour améliorer votre expérience. 
              Certains cookies nécessitent votre consentement. 
              <a href="/cookies" target="_blank">En savoir plus</a>
            </p>
          </div>
          <div class="cookie-consent-actions">
            <button class="cookie-consent-btn cookie-consent-btn-accept" id="cookie-accept-all" aria-label="Accepter tous les cookies">
              ✓ Accepter tout
            </button>
            <button class="cookie-consent-btn cookie-consent-btn-refuse" id="cookie-refuse-all" aria-label="Refuser les cookies non essentiels">
              ✕ Refuser tout
            </button>
            <button class="cookie-consent-btn cookie-consent-btn-customize" id="cookie-customize" aria-label="Personnaliser les préférences">
              ⚙ Personnaliser
            </button>
          </div>
        </div>
      `;
      
      document.body.appendChild(banner);
      this.banner = banner;

      // Attach event listeners
      document.getElementById('cookie-accept-all').addEventListener('click', () => this.handleAcceptAll());
      document.getElementById('cookie-refuse-all').addEventListener('click', () => this.handleRefuseAll());
      document.getElementById('cookie-customize').addEventListener('click', () => this.showCustomizeModal());

      // Show banner with animation
      setTimeout(() => banner.classList.add('show'), 100);
    },

    createCustomizeModal: function() {
      const modal = document.createElement('div');
      modal.className = 'cookie-consent-modal';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-label', 'Personnalisation des cookies');
      modal.innerHTML = `
        <div class="cookie-consent-modal-content">
          <div class="cookie-consent-modal-header">
            <h2>Personnaliser vos préférences</h2>
          </div>
          <div class="cookie-consent-modal-body">
            <div class="cookie-category">
              <div class="cookie-category-header">
                <h3 class="cookie-category-title">
                  Cookies essentiels
                  <span class="cookie-required-badge">Requis</span>
                </h3>
                <label class="cookie-toggle">
                  <input type="checkbox" checked disabled>
                  <span class="cookie-toggle-slider"></span>
                </label>
              </div>
              <p class="cookie-category-description">
                Ces cookies sont nécessaires au fonctionnement du site et ne peuvent pas être désactivés. 
                Ils incluent les cookies de session et de sécurité.
              </p>
            </div>

            <div class="cookie-category">
              <div class="cookie-category-header">
                <h3 class="cookie-category-title">Cookies analytiques</h3>
                <label class="cookie-toggle">
                  <input type="checkbox" id="toggle-analytics">
                  <span class="cookie-toggle-slider"></span>
                </label>
              </div>
              <p class="cookie-category-description">
                Ces cookies nous permettent de mesurer l'audience et d'améliorer les performances du site. 
                Toutes les données sont anonymisées.
              </p>
            </div>

            <div class="cookie-category">
              <div class="cookie-category-header">
                <h3 class="cookie-category-title">Cookies Stripe (Paiement)</h3>
                <label class="cookie-toggle">
                  <input type="checkbox" id="toggle-stripe">
                  <span class="cookie-toggle-slider"></span>
                </label>
              </div>
              <p class="cookie-category-description">
                Cookies utilisés par Stripe pour sécuriser les paiements et prévenir la fraude. 
                <strong>Requis pour effectuer un paiement.</strong>
              </p>
            </div>
          </div>
          <div class="cookie-consent-modal-footer">
            <button class="cookie-consent-btn cookie-consent-btn-refuse" id="modal-cancel">
              Annuler
            </button>
            <button class="cookie-consent-btn cookie-consent-btn-accept" id="modal-save">
              Enregistrer mes préférences
            </button>
          </div>
        </div>
      `;

      document.body.appendChild(modal);
      this.modal = modal;

      // Close modal when clicking outside
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          this.hideCustomizeModal();
        }
      });

      // Attach event listeners
      document.getElementById('modal-cancel').addEventListener('click', () => this.hideCustomizeModal());
      document.getElementById('modal-save').addEventListener('click', () => this.handleSavePreferences());
    },

    showCustomizeModal: function() {
      if (!this.modal) {
        this.createCustomizeModal();
      }
      
      // Load current preferences if any
      const currentConsent = ConsentManager.getConsent();
      if (currentConsent) {
        document.getElementById('toggle-analytics').checked = currentConsent.analytics || false;
        document.getElementById('toggle-stripe').checked = currentConsent.stripe !== false; // Default true
      } else {
        // Default: analytics off, stripe on
        document.getElementById('toggle-analytics').checked = false;
        document.getElementById('toggle-stripe').checked = true;
      }

      this.modal.classList.add('show');
    },

    hideCustomizeModal: function() {
      if (this.modal) {
        this.modal.classList.remove('show');
      }
    },

    hideBanner: function() {
      if (this.banner) {
        this.banner.classList.remove('show');
        setTimeout(() => {
          if (this.banner && this.banner.parentNode) {
            this.banner.parentNode.removeChild(this.banner);
          }
          this.banner = null;
        }, 400);
      }
    },

    handleAcceptAll: function() {
      const preferences = {
        essential: true,
        analytics: true,
        stripe: true
      };
      ConsentManager.saveConsent(preferences);
      this.hideBanner();
      this.hideCustomizeModal();
    },

    handleRefuseAll: function() {
      const preferences = {
        essential: true,
        analytics: false,
        stripe: false
      };
      ConsentManager.saveConsent(preferences);
      this.hideBanner();
      this.hideCustomizeModal();
    },

    handleSavePreferences: function() {
      const preferences = {
        essential: true,
        analytics: document.getElementById('toggle-analytics').checked,
        stripe: document.getElementById('toggle-stripe').checked
      };
      ConsentManager.saveConsent(preferences);
      this.hideBanner();
      this.hideCustomizeModal();
    }
  };

  // Public API
  window.CookieConsent = {
    // Show banner manually (for "Manage cookies" link)
    show: function() {
      BannerUI.injectStyles();
      BannerUI.createBanner();
    },

    // Get current consent
    getPreferences: function() {
      return ConsentManager.getConsent();
    },

    // Revoke consent and show banner again
    revoke: function() {
      CookieManager.delete(CONSENT_COOKIE_NAME);
      this.show();
    }
  };

  // Initialize on DOM ready
  function init() {
    // Check if consent has already been given
    const existingConsent = ConsentManager.getConsent();
    
    if (!existingConsent) {
      // First visit or consent expired - show banner
      BannerUI.injectStyles();
      BannerUI.createBanner();
    } else {
      // Apply existing consent
      ConsentManager.applyConsent(existingConsent);
    }
  }

  // Run initialization
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
