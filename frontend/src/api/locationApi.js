// src/api/locationApi.js

const API_BASE_URL = "http://127.0.0.1:8000" ;

//get cities
export async function fetchCities(){
    const response = await fetch(`${API_BASE_URL}/cities/`);

    const data = await response.json()

    return data ;
}

//create new cities
export async function createCity(name) {
    const response = await fetch(`${API_BASE_URL}/cities/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ name }),
    });

    const data = await response.json();
    return data;
}
