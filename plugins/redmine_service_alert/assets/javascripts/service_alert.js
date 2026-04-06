(function () {
  function initServiceAlertModal() {
    var modal = document.getElementById('service-alert-modal');
    if (!modal) return;

    var enabled = modal.dataset.enabled === 'true';
    var showPopup = modal.dataset.showPopup === 'true';
    var version = modal.dataset.version || '0';

    if (!enabled || !showPopup) return;

    var storageKey = 'service_alert_seen_version_' + version;
    if (window.sessionStorage.getItem(storageKey)) {
      modal.style.display = 'none';
      return;
    }

    modal.style.display = 'flex';

    var closeButton = modal.querySelector('.service-alert-modal-close');
    if (closeButton) {
      closeButton.addEventListener('click', function () {
        window.sessionStorage.setItem(storageKey, '1');
        modal.style.display = 'none';
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initServiceAlertModal);
  } else {
    initServiceAlertModal();
  }
})();
