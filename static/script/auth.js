let password = document.querySelector('#password-container')
if (password) {
    let toggle = password.querySelector('span'),
        icon = toggle.querySelector('i'),
        input = password.querySelector('input');

    toggle.addEventListener('click', e => {
        icon.classList.toggle('hgi-view');
        icon.classList.toggle('hgi-view-off-slash');
        if (icon.classList.contains('hgi-view-off-slash')) {
            input.type = 'text';
        } else {
            input.type = 'password';
        }
    })
}