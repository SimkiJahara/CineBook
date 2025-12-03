let genres = [];
let editingEidr = null;

// document.addEventListener('DOMContentLoaded', async () => {
//     if (!localStorage.getItem('authToken')) {
//         alert('Admin access required');
//         window.location.href = 'login.html';
//         return;
//     }
//     await loadGenres();
//     await loadAllMovies();
// });

document.addEventListener('DOMContentLoaded', async () => {
    // TEMPORARY: Auto-login as admin for testing
    localStorage.setItem('authToken', 'fake-admin-token-12345');

    await loadGenres();
    await loadAllMovies();
});

async function loadGenres() {
    try {
        genres = await api.getGenres();
    } catch (e) {
        alert('Failed to load genres');
    }
}

async function loadAllMovies() {
    const grid = document.getElementById('adminMoviesGrid');
    try {
        const movies = await api.getMovies({ limit: 100 });
        grid.innerHTML = movies.map(m => `
            <div class="admin-movie-card">
                <img src="${m.posterurl || 'https://via.placeholder.com/300x450'}" 
                     alt="${m.title}" onerror="this.src='https://via.placeholder.com/300x450/333/fff?text=No+Poster'">
                <div class="admin-card-info">
                    <h3>${m.title}</h3>
                    <p><strong>EIDR:</strong> ${m.eidr}</p>
                    <p><strong>Released:</strong> ${m.releasedate || 'TBA'}</p>
                </div>
                <div class="admin-card-actions">
                    <button class="btn btn-primary" onclick="editMovie('${m.eidr}')">Edit</button>
                    <button class="btn btn-outline" onclick="deleteMovie('${m.eidr}', '${m.title}')">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (e) {
        grid.innerHTML = '<div class="error">Failed to load movies</div>';
    }
}

function openCreateModal() {
    editingEidr = null;
    document.getElementById('modalTitle').textContent = 'Add New Movie';
    document.getElementById('movieForm').reset();
    document.getElementById('eidr').disabled = false;
    renderGenreCheckboxes();
    document.getElementById('movieModal').style.display = 'flex';
}

async function editMovie(eidr) {
    try {
        const movie = await api.getMovie(eidr);
        editingEidr = eidr;

        document.getElementById('modalTitle').textContent = 'Edit Movie';
        document.getElementById('eidr').value = movie.eidr;
        document.getElementById('eidr').disabled = true;
        document.getElementById('title').value = movie.title;
        document.getElementById('posterurl').value = movie.posterurl || '';
        document.getElementById('trailerurl').value = movie.trailerurl || '';
        document.getElementById('lengthmin').value = movie.lengthmin || '';
        document.getElementById('rating').value = movie.rating || '';
        document.getElementById('releasedate').value = movie.releasedate || '';
        document.getElementById('language').value = movie.language || 'English';
        document.getElementById('description').value = movie.description || '';
        document.getElementById('director').value = movie.director || '';
        document.getElementById('cast').value = movie.cast?.join(', ') || '';

        renderGenreCheckboxes(movie.genres.map(g => g.id));
        document.getElementById('movieModal').style.display = 'flex';
    } catch (e) {
        alert('Failed to load movie');
    }
}

function renderGenreCheckboxes(selected = []) {
    const container = document.getElementById('genreCheckboxes');
    container.innerHTML = genres.map(g => `
        <label><input type="checkbox" value="${g.id}" ${selected.includes(g.id) ? 'checked' : ''}> ${g.name}</label>
    `).join('');
}

document.getElementById('movieForm').onsubmit = async (e) => {
    e.preventDefault();
    const formData = {
        eidr: document.getElementById('eidr').value.trim(),
        title: document.getElementById('title').value.trim(),
        posterurl: document.getElementById('posterurl').value || null,
        trailerurl: document.getElementById('trailerurl').value || null,
        lengthmin: parseInt(document.getElementById('lengthmin').value) || null,
        rating: document.getElementById('rating').value || null,
        releasedate: document.getElementById('releasedate').value || null,
        language: document.getElementById('language').value || 'English',
        description: document.getElementById('description').value || null,
        director: document.getElementById('director').value || null,
        genre_ids: Array.from(document.querySelectorAll('#genreCheckboxes input:checked')).map(c => parseInt(c.value)),
        cast: document.getElementById('cast').value.split(',').map(s => s.trim()).filter(Boolean)
    };

    try {
        if (editingEidr) {
            await api.updateMovie(editingEidr, formData);
            alert('Movie updated!');
        } else {
            await api.createMovie(formData);
            alert('Movie created!');
        }
        closeModal();
        loadAllMovies();
    } catch (e) {
        alert('Error: ' + e.message);
    }
};

async function deleteMovie(eidr, title) {
    if (!confirm(`Delete "${title}" permanently?`)) return;
    try {
        await api.deleteMovie(eidr);
        alert('Movie deleted');
        loadAllMovies();
    } catch (e) {
        alert('Error: ' + e.message);
    }
}

function closeModal() {
    document.getElementById('movieModal').style.display = 'none';
}

function logout() {
    localStorage.removeItem('authToken');
    window.location.href = 'login.html';
}

// Close modal when clicking outside
window.onclick = (e) => {
    const modal = document.getElementById('movieModal');
    if (e.target === modal) closeModal();
};