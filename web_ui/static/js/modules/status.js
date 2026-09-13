// web_ui/static/js/modules/status.js
import { botStatusSpan, statusIndicator, startButton, stopButton, restartButton, featureListDiv, serverInfoCard, serverInfoDisplay } from './elements.js';
import { showFlashMessage } from './utils.js';

const I18N = window.WEB_I18N || {};
const t = (key) => I18N[key] ?? key;

const featureMap = {
    "announce_join_leave": "jcl",
    "allow_channel_messages": "chanmsg",
    "allow_broadcast": "broadcast",
    "allow_groq_pm": "groqpm",
    "allow_groq_channel": "groqchan",
    "filter_enabled": "filter",
    "bot_locked": "lock",
    "context_history_enabled": "context_history",
    "debug_logging_enabled": "debug_logging"
};

export async function fetchStatus() {
    try {
        const response = await fetch('/status');
        
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            throw new TypeError("Oops, we didn't get JSON!");
        }

        const data = await response.json();
        
        if (data.running) {
        botStatusSpan.textContent = t('web.status.running');
        statusIndicator.className = 'status-indicator running';
        startButton.disabled = true;
        stopButton.disabled = false;
        restartButton.style.display = 'inline-block'; // Show restart button

        // Clear any previous messages or features when bot is running
        featureListDiv.innerHTML = '';

        // Update features when bot is running
        const existingFeatures = new Set();
        if (data.features) {
            for (const fullKey in data.features) {
                const shortKey = featureMap[fullKey] || fullKey; // Use short key if available
                const isEnabled = data.features[fullKey];
                const inputId = `feature-${shortKey}`;
                existingFeatures.add(inputId);

                let checkbox = document.getElementById(inputId);
                if (!checkbox) {
                    // Feature does not exist, create it
                    const colDiv = document.createElement('div');
                    colDiv.className = 'col';
                    colDiv.innerHTML = `
                        <div class="form-check form-switch feature-card">
                            <input class="form-check-input" type="checkbox" role="switch" id="${inputId}">
                            <label class="form-check-label" for="${inputId}">${t(`web.status.feature_labels.${fullKey}`)}</label>
                        </div>
                    `;
                    featureListDiv.appendChild(colDiv);
                    checkbox = document.getElementById(inputId);
                    if (checkbox) {
                        checkbox.addEventListener('change', async (event) => {
                            const toggleResponse = await fetch(`/toggle_feature/${shortKey}`, {
                                method: 'POST',
                            });
                            const toggleData = await toggleResponse.json();
                            if (toggleData.status === 'success') {
                                console.log(toggleData.message);
                                fetchStatus(); // Refresh status to show updated state
                            } else {
                                alert(`Error toggling feature: ${toggleData.message}`);
                                event.target.checked = !event.target.checked; // Revert checkbox state
                            }
                        });
                    }
                }

                // Update existing checkbox properties
                if (checkbox) {
                    checkbox.checked = isEnabled;
                    checkbox.disabled = !data.running;
                }
            }
        }

        // Show server info card
        serverInfoCard.style.display = 'block';

        // Populate server info
        if (data.server_info) {
            serverInfoDisplay.innerHTML = ''; // Clear previous content
            const infoMap = {
                "host": t('web.status.server.host'),
                "tcp_port": t('web.status.server.tcp_port'),
                "udp_port": t('web.status.server.udp_port'),
                "nickname": t('web.status.server.nickname'),
                "username": t('web.status.server.username'),
                "target_channel_path": t('web.status.server.target_channel_path'),
                "my_user_id": t('web.status.server.my_user_id'),
                "my_rights": t('web.status.server.my_rights'),
                "client_name": t('web.status.server.client_name'),
                "client_id": t('web.status.server.client_id'),
                "application_version": t('web.status.server.application_version'),
                "application_version_label": t('web.status.server.application_version_label'),
                "teamtalk_version": t('web.status.server.teamtalk_version'),
                "status_message": t('web.status.server.status_message'),
                "logged_in": t('web.status.server.logged_in'),
                "in_channel": t('web.status.server.in_channel')
            };

            for (const key in infoMap) {
                if (data.server_info.hasOwnProperty(key)) {
                    const value = data.server_info[key];
                    const displayValue = typeof value === 'boolean' ? (value ? t('web.common.yes') : t('web.common.no')) : value;
                    const colDiv = document.createElement('div');
                    colDiv.className = 'col-md-6 col-12';
                    colDiv.innerHTML = `<p><strong>${infoMap[key]}:</strong> ${displayValue}</p>`;
                    serverInfoDisplay.appendChild(colDiv);
                }
            }
        }

    } else {
        updateUIForStoppedBot();
    }
    } catch (error) {
        console.error("Error fetching status:", error);
        updateUIForStoppedBot();
    }
}

export function updateUIForStoppedBot() {
    botStatusSpan.textContent = t('web.status.stopped');
    statusIndicator.className = 'status-indicator stopped';
    startButton.disabled = false;
    stopButton.disabled = true;
    restartButton.style.display = 'none'; // Hide restart button

    // Hide server info card
    serverInfoCard.style.display = 'none';

    // Always display the stopped message and clear features
    featureListDiv.innerHTML = `<p class="text-muted">${t('web.status.stopped_message')}</p>`;
}
