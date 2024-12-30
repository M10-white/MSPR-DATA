const API_URL = 'http://localhost:5000/api';

export async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_URL}/${endpoint}`);
        if (!response.ok) throw new Error('Erreur API');
        return await response.json();
    } catch (error) {
        console.error(error);
    }
}
