// Missions page JavaScript

let currentMissions = [];

async function loadMissions() {
    try {
        const data = await fetchData('/api/missions/');
        currentMissions = data.missions;
        displayMissions(currentMissions);
        showSuccess(`Loaded ${data.count} missions`, 'missions-status');
    } catch (error) {
        showError(`Failed to load missions: ${error.message}`, 'missions-status');
    }
}

function displayMissions(missions) {
    const missionsList = document.getElementById('missions-list');
    
    if (!missions || missions.length === 0) {
        missionsList.innerHTML = '<p>No missions found</p>';
        return;
    }
    
    const missionsHTML = missions.map(mission => `
        <div class="mission-item">
            <h4>${mission.name}</h4>
            <p>${mission.description || 'No description available'}</p>
            <div class="mission-meta">
                <strong>Type:</strong> ${mission.mission_type || 'N/A'} | 
                <strong>Status:</strong> ${mission.status} | 
                <strong>Launch Date:</strong> ${formatDate(mission.launch_date)} |
                <strong>Agency:</strong> ${mission.agency}
            </div>
            <div class="mission-actions">
                <button onclick="editMission(${mission.id})">Edit</button>
                <button onclick="deleteMission(${mission.id})">Delete</button>
                <button onclick="viewMissionData(${mission.id})">View Data</button>
            </div>
        </div>
    `).join('');
    
    missionsList.innerHTML = missionsHTML;
}

function showCreateMissionForm() {
    document.getElementById('mission-form').style.display = 'block';
    document.getElementById('new-mission-form').reset();
}

function hideMissionForm() {
    document.getElementById('mission-form').style.display = 'none';
}

document.getElementById('new-mission-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('mission-name').value,
        description: document.getElementById('mission-description').value,
        mission_type: document.getElementById('mission-type').value,
        launch_date: document.getElementById('launch-date').value,
        status: document.getElementById('mission-status').value
    };
    
    try {
        const result = await fetchData('/api/missions/', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        showSuccess('Mission created successfully!', 'missions-status');
        hideMissionForm();
        loadMissions(); // Refresh the list
        
    } catch (error) {
        showError(`Failed to create mission: ${error.message}`, 'missions-status');
    }
});

async function deleteMission(missionId) {
    if (!confirm('Are you sure you want to delete this mission?')) {
        return;
    }
    
    try {
        await fetchData(`/api/missions/${missionId}`, {
            method: 'DELETE'
        });
        
        showSuccess('Mission deleted successfully!', 'missions-status');
        loadMissions(); // Refresh the list
        
    } catch (error) {
        showError(`Failed to delete mission: ${error.message}`, 'missions-status');
    }
}

function editMission(missionId) {
    // Find the mission in current missions
    const mission = currentMissions.find(m => m.id === missionId);
    if (!mission) {
        showError('Mission not found', 'missions-status');
        return;
    }
    
    // Populate the form with current values
    document.getElementById('mission-name').value = mission.name;
    document.getElementById('mission-description').value = mission.description || '';
    document.getElementById('mission-type').value = mission.mission_type || '';
    document.getElementById('launch-date').value = mission.launch_date || '';
    document.getElementById('mission-status').value = mission.status;
    
    // Show the form
    showCreateMissionForm();
    
    // Change form submit behavior to update instead of create
    const form = document.getElementById('new-mission-form');
    form.onsubmit = async function(e) {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('mission-name').value,
            description: document.getElementById('mission-description').value,
            mission_type: document.getElementById('mission-type').value,
            launch_date: document.getElementById('launch-date').value,
            status: document.getElementById('mission-status').value
        };
        
        try {
            await fetchData(`/api/missions/${missionId}`, {
                method: 'PUT',
                body: JSON.stringify(formData)
            });
            
            showSuccess('Mission updated successfully!', 'missions-status');
            hideMissionForm();
            loadMissions(); // Refresh the list
            
            // Reset form behavior back to create
            form.onsubmit = null;
            
        } catch (error) {
            showError(`Failed to update mission: ${error.message}`, 'missions-status');
        }
    };
}

function viewMissionData(missionId) {
    // Redirect to data page with mission filter
    window.location.href = `/data?mission=${missionId}`;
}

// Add status display element if it doesn't exist
document.addEventListener('DOMContentLoaded', function() {
    if (!document.getElementById('missions-status')) {
        const statusDiv = document.createElement('div');
        statusDiv.id = 'missions-status';
        statusDiv.className = 'status-display';
        document.querySelector('.container').appendChild(statusDiv);
    }
});