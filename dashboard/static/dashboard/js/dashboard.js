function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function postAjax(url, data) {
    const csrfToken = getCookie('csrftoken');
    const body = new URLSearchParams(data);
    return fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: body.toString(),
    }).then((response) => response.json());
}

document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebarToggle');
    if (toggle && sidebar) {
        toggle.addEventListener('click', () => sidebar.classList.toggle('show'));
    }

    document.querySelectorAll('.ajax-status').forEach(function (select) {
        select.addEventListener('change', function () {
            postAjax(select.dataset.url, {
                field: select.dataset.field,
                value: select.value,
            }).then(function (data) {
                if (!data.success) alert(data.error || 'حدث خطأ');
            });
        });
    });

    document.querySelectorAll('.ajax-reservation').forEach(function (select) {
        select.addEventListener('change', function () {
            postAjax(select.dataset.url, { status: select.value }).then(function (data) {
                if (!data.success) alert(data.error || 'حدث خطأ');
            });
        });
    });

    document.querySelectorAll('.ajax-toggle').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const field = btn.dataset.field || '';
            postAjax(btn.dataset.url, field ? { field: field } : {}).then(function (data) {
                if (data.success) location.reload();
                else alert(data.error || 'حدث خطأ');
            });
        });
    });

    document.querySelectorAll('.ajax-toggle-read').forEach(function (btn) {
        btn.addEventListener('click', function () {
            postAjax(btn.dataset.url, {}).then(function (data) {
                if (data.success) location.reload();
            });
        });
    });
});
