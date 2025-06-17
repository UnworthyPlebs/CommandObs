
// Import existing functions from obsApi.js
import { fetchScenes, switchScene, getcurrentScene } from './obsApi';

// Scene Dashboard JavaScript using existing API functions
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');
let currentScene = '';

async function loadScenes() {
    if (!token) {
        document.getElementById('status').innerHTML = 'Error: No token found';
        return;
    }

    try {
        // Use existing API functions
        const scenes = await fetchScenes(token);
        const current = await getcurrentScene(token);
        
        currentScene = current;

        // Render scenes
        renderScenes(scenes);
        document.getElementById('status').innerHTML = `Connected! Current scene: ${currentScene}`;
    } catch (error) {
        document.getElementById('status').innerHTML = `Error: ${error.message}`;
        console.error('Error loading scenes:', error);
    }
}

function renderScenes(scenes) {
    const sceneList = document.getElementById('scene-list');
    sceneList.innerHTML = '';

    scenes.forEach(scene => {
        const button = document.createElement('button');
        button.className = 'scene-button';
        button.textContent = scene.sceneName;
        
        if (scene.sceneName === currentScene) {
            button.classList.add('active');
        }

        button.onclick = () => handleSceneSwitch(scene.sceneName, button);
        sceneList.appendChild(button);
    });
}

async function handleSceneSwitch(sceneName, buttonElement) {
    if (sceneName === currentScene) return;

    try {
        // Use existing switchScene function
        const result = await switchScene(sceneName, token);

        if (result.success) {
            // Update UI
            document.querySelectorAll('.scene-button').forEach(btn => btn.classList.remove('active'));
            buttonElement.classList.add('active');
            currentScene = sceneName;
            document.getElementById('status').innerHTML = `Switched to: ${sceneName}`;
        } else {
            document.getElementById('status').innerHTML = `Failed to switch to: ${sceneName}`;
        }
    } catch (error) {
        document.getElementById('status').innerHTML = `Error switching scene: ${error.message}`;
    }
}

// Load scenes when page loads
document.addEventListener('DOMContentLoaded', loadScenes);