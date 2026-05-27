document.addEventListener('DOMContentLoaded', () => {
    const runsContainer = document.getElementById('runs-container');

    // Fetch the runs data
    fetch('data/runs.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(runs => {
            runsContainer.innerHTML = ''; // Clear loading text
            
            if (runs.length === 0) {
                runsContainer.innerHTML = '<p class="loading">Aucune course trouvée.</p>';
                return;
            }

            // Sort runs by date (newest first)
            runs.sort((a, b) => new Date(b.date) - new Date(a.date));

            runs.forEach((run, index) => {
                const card = document.createElement('div');
                card.className = 'run-card';
                card.style.animationDelay = `${index * 0.1}s`;

                // Format the date (e.g. 15 Octobre 2023)
                const dateObj = new Date(run.date);
                const formattedDate = dateObj.toLocaleDateString('fr-FR', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                });

                card.innerHTML = `
                    <div class="run-header">
                        <div class="run-title">${run.event_name}</div>
                        <div class="run-date">${formattedDate}</div>
                    </div>
                    <div class="run-stats">
                        <div class="stat">
                            <span class="stat-label">Distance</span>
                            <span class="stat-value">${run.distance}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Temps</span>
                            <span class="stat-value">${run.time}</span>
                        </div>
                    </div>
                    ${run.url ? `<a href="${run.url}" target="_blank" class="run-source">Voir sur ${run.source} ↗</a>` : `<div class="run-source">Source: ${run.source}</div>`}
                `;

                runsContainer.appendChild(card);
            });
        })
        .catch(error => {
            console.error('Error fetching runs:', error);
            runsContainer.innerHTML = '<p class="loading">Erreur lors du chargement des courses. Veuillez réessayer plus tard.</p>';
        });
});
