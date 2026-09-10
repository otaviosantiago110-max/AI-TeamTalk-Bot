// web_ui/static/js/modules/users.js
import { userListTableBody, addUserForm, newUsernameInput, newPasswordInput, confirmPasswordInput, addUserModal } from './elements.js';
import { showFlashMessage } from './utils.js';

const I18N = window.WEB_I18N || {};
const t = (key, vars = {}) => { let text = I18N[key] ?? key; for (const [k, v] of Object.entries(vars)) text = text.replaceAll(`{${k}}`, v); return text; };

export async function fetchUsers() {
    const response = await fetch('/users');
    const users = await response.json();
    userListTableBody.innerHTML = '';
    users.forEach(user => {
        const row = userListTableBody.insertRow();
        row.innerHTML = `
            <td>${user.username}</td>
            <td>${user.role}</td>
            <td>
                <button class="btn btn-danger btn-sm delete-user-btn" data-user-id="${user.id}">${t('web.user_management.delete_user')}</button>
            </td>
        `;
    });
    // Add event listeners for delete buttons
    document.querySelectorAll('.delete-user-btn').forEach(button => {
        button.addEventListener('click', async (event) => {
            const userId = event.target.dataset.userId;
            if (confirm(t('web.flash.confirm_delete_user', { username: userId }))) {
                const response = await fetch(`/users/${userId}`, {
                    method: 'DELETE',
                });
                const data = await response.json();
                if (data.status === 'success') {
                    showFlashMessage(data.message, 'success');
                    fetchUsers(); // Refresh user list
                } else {
                    showFlashMessage(data.message, 'danger');
                }
            }
        });
    });
}

export function setupAddUserForm() {
    addUserForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const username = newUsernameInput.value;
        const password = newPasswordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        const role = addUserForm.querySelector('input[name="role"]:checked').value;

        if (password !== confirmPassword) {
            showFlashMessage(t('web.flash.password_mismatch'), 'danger');
            return;
        }

        const response = await fetch('/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password, role }),
        });
        const data = await response.json();
        if (data.status === 'success') {
            showFlashMessage(data.message, 'success');
            addUserModal.hide(); // Close the modal
            addUserForm.reset(); // Clear the form
            fetchUsers(); // Refresh user list
        } else {
            showFlashMessage(data.message, 'danger');
        }
    });
}
