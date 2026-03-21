(function () {
    async function callApi(methodName) {
        if (window.pywebview && window.pywebview.api && typeof window.pywebview.api[methodName] === 'function') {
            try {
                return await window.pywebview.api[methodName]();
            } catch (err) {
                console.error('窗口控制失败:', err);
            }
        }
        return null;
    }

    function bindWindowControls() {
        const btnMin = document.getElementById('btnMinimize');
        const btnMax = document.getElementById('btnMaximize');
        const btnClose = document.getElementById('btnClose');

        if (btnMin) {
            btnMin.addEventListener('click', function (event) {
                event.preventDefault();
                callApi('minimize_window');
            });
        }

        if (btnMax) {
            btnMax.addEventListener('click', async function (event) {
                event.preventDefault();
                const result = await callApi('toggle_maximize');
                if (result && typeof result.maximized !== 'undefined') {
                    btnMax.textContent = result.maximized ? '❐' : '□';
                }
            });
        }

        if (btnClose) {
            btnClose.addEventListener('click', function (event) {
                event.preventDefault();
                callApi('close_window');
            });
        }
    }

    document.addEventListener('DOMContentLoaded', bindWindowControls);
    window.addEventListener('pywebviewready', bindWindowControls);
})();
