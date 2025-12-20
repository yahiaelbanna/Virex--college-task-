document.getElementById('avatarInput').addEventListener('change', e => {
    if (e.target.files && e.target.files[0]) {
        let url = URL.createObjectURL(e.target.files[0]);

        document.getElementById('avatar').src = url;
    }
})