function validateLoginForm() {
    document.getElementById('username-error').textContent = '';
    document.getElementById('password-error').textContent = '';
    document.getElementById('captcha-error').textContent = '';
    
    let isValid = true;
    
    const username = document.getElementById('username').value.trim();
    if (username === '') {
        document.getElementById('username-error').textContent = 'Username is required';
        isValid = false;
    } else if (username.length < 3) {
        document.getElementById('username-error').textContent = 'Username must be at least 3 characters';
        isValid = false;
    }
    
    const password = document.getElementById('password').value;
    if (password === '') {
        document.getElementById('password-error').textContent = 'Password is required';
        isValid = false;
    } else if (password.length < 6) {
        document.getElementById('password-error').textContent = 'Password must be at least 6 characters';
        isValid = false;
    }
    
    const captcha = document.getElementById('captcha_input').value.trim();
    if (captcha === '') {
        document.getElementById('captcha-error').textContent = 'CAPTCHA is required';
        isValid = false;
    }
    
    return isValid;
}
