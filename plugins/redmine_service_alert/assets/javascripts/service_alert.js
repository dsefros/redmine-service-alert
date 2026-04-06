(function () {
  function init() {
    var modal = document.getElementById('service-alert-modal');
    if (!modal) return;

    var version = modal.dataset.version || '0';
    var key = 'service_alert_seen_' + version;

    if (sessionStorage.getItem(key)) return;

    modal.style.display = 'flex';

    function close() {
      sessionStorage.setItem(key, '1');
      modal.style.display = 'none';
    }

    var btn = modal.querySelector('.service-alert-modal-dismiss');
    if (btn) {
      btn.addEventListener('click', close);
    }

    // (опционально) клик по фону тоже закрывает
    modal.addEventListener('click', function (e) {
      if (e.target === modal) {
        close();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
