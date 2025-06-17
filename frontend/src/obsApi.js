const BASE_URL = 'http://localhost:5000'

export async function fetchScenes(token){
    try{
        const response = await fetch(`/api/obs/scenes?token=${token}`);

        if (!response.ok){
            const errorData = await response.json();
            throw new Error(`Failed to fetch scenes: ${response.status}`);
        }

        const data = await response.json();
        return data.scenes || data;

    }catch (error) {
        console.error('Failed to fetch scenes:', error);
        throw error;
    }
    
}

export async function switchScene(sceneName, token){
    try {
        const request = await fetch(`/api/obs/scenes/${sceneName}?token=${token}`, {
            method: 'POST', 
            headers:  {
                'Content-Type': 'application/json'
            }
        })
        if (!request.ok){
            const errorDetails = await request.text();
            throw new Error(`Failed to switch scenes: ${request.status} - ${errorDetails}`);
        }
        return await request.json();
    }catch (error) {
        console.error('Error switching scene:', error);
        return `Error: ${error.message || error}`;
    }

}

export async function getDebugInfo(){
    let response;
    try{
        let response = await fetch('/api/debug');
        if(!response.ok){
            throw new Error(`Error: ${response.status}`);
        }
        return response.json();
    }catch{
        return 'Error: unknown';
    }
}

export async function getcurrentScene(token) {
    try{
        const response = await fetch(`/api/current_scene?token=${token}`);
        if (!response.ok){
            throw new Error(`Error: ${response.status}`);
        }
        const data = await response.json();
        return data.current_scene;
    } catch (error) {
        console.error('Error getting scene:', error);
        return `Error: ${error.message || error}`;
    }
}

export async function navigateSignup(){
    try{
        window.location.href = '/signup';
    }catch(error){
        console.error('Failed nav', error);
    }
}

export async function navigateLogin() {
    try{
        console.log('attempt');
        window.location.href = '/login';
    }catch(error){
        console.error('Failed nav', error);
    }
}

export async function get_instances() {
        try{
            const request = await fetch('/api/renderInstances');
            const data = await request.json()
            return data
        }catch (error){
            console.error(error);
        }
    }

export async function addInstance() {
    try{
        console.log('attempt');
        window.location.href = '/api/server_instances';
    }catch(error){
        console.error('Failed nav', error);
    }
}

export async function navigateQuick() {
    try{
        console.log('attempt');
        window.location.href = '/api/quickConnect';
    }catch(error){
        console.error('Failed nav', error);
    }
}

export async function sessionData() {
    try{
        const urlParams = new URLSearchParams(window.location.search)
        const token = urlParams.get('token')
        if (!token){
            throw new Error('No token found in URL')
        }  

        const request = await fetch(`/api/quickSession?token=${token}`)
        const data = await request.json()
        return data
    }catch (error){
        console.error(error)
        return {connected: false, scenes: [], error: error.message}
    }
}
