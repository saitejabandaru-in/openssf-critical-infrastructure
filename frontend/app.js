// OpenSSF Criticality Score Parameter Definitions
const PARAM_CONFIGS = {
    created_since: { weight: 1.0, max: 120, alpha: 1.0, inverted: false, label: "Project Age (Months)" },
    updated_since: { weight: 1.0, max: 120, alpha: 1.0, inverted: true, label: "Inactivity (Months)" },
    contributor_count: { weight: 2.0, max: 5000, alpha: 0.001, inverted: false, label: "Contributors" },
    org_count: { weight: 1.0, max: 10, alpha: 0.1, inverted: false, label: "Organizations" },
    commit_frequency: { weight: 1.0, max: 1000, alpha: 0.01, inverted: false, label: "Commits / Week" },
    recent_releases_count: { weight: 0.5, max: 26, alpha: 0.1, inverted: false, label: "Releases (Yearly)" },
    updated_issues_count: { weight: 0.5, max: 5000, alpha: 0.001, inverted: false, label: "Updated Issues" },
    closed_issues_count: { weight: 0.5, max: 5000, alpha: 0.001, inverted: false, label: "Closed Issues" },
    comment_frequency: { weight: 1.0, max: 15, alpha: 0.1, inverted: false, label: "Comments / Issue" },
    dependents_count: { weight: 2.0, max: 500000, alpha: 0.00001, inverted: false, label: "Dependents Count" }
};

// Initial Default Metrics State
let currentMetrics = {
    created_since: 48,
    updated_since: 0.5,
    contributor_count: 85,
    org_count: 8,
    commit_frequency: 18.5,
    recent_releases_count: 12,
    updated_issues_count: 320,
    closed_issues_count: 290,
    comment_frequency: 5.2,
    dependents_count: 2400
};

const CRITICAL_THRESHOLD = 0.400;
let radarChartInstance = null;

// Pure Math Score Calculation Function
function calculateCriticalityScore(metrics) {
    let totalScore = 0.0;
    let totalWeight = 0.0;
    const normScores = {};

    for (const [key, p] of Object.entries(PARAM_CONFIGS)) {
        let val = Math.max(0, Math.min(metrics[key] || 0, p.max));
        let num = Math.log(1.0 + p.alpha * val);
        let den = Math.log(1.0 + p.alpha * p.max);
        
        let norm = den > 0 ? (num / den) : 0;
        if (p.inverted) norm = 1.0 - norm;

        normScores[key] = norm;
        totalScore += p.weight * norm;
        totalWeight += p.weight;
    }

    const finalScore = totalWeight > 0 ? (totalScore / totalWeight) : 0;
    return { score: finalScore, normScores };
}

// Initialize Application UI
document.addEventListener('DOMContentLoaded', () => {
    initSliders();
    initRadarChart();
    initEventListeners();
    updateDashboard();
});

function initSliders() {
    const container = document.getElementById('slidersContainer');
    container.innerHTML = '';

    for (const [key, p] of Object.entries(PARAM_CONFIGS)) {
        const item = document.createElement('div');
        item.className = 'control-item';
        
        item.innerHTML = `
            <div class="control-header">
                <span class="control-title">${p.label}</span>
                <span class="control-value" id="val-${key}">${currentMetrics[key]}</span>
            </div>
            <input type="range" class="slider-bar" id="slider-${key}" 
                min="0" max="${p.max}" step="${p.max > 100 ? (p.max > 1000 ? 50 : 5) : 0.5}" 
                value="${currentMetrics[key]}">
        `;

        container.appendChild(item);

        const sliderInput = item.querySelector(`#slider-${key}`);
        sliderInput.addEventListener('input', (e) => {
            currentMetrics[key] = parseFloat(e.target.value);
            document.getElementById(`val-${key}`).textContent = currentMetrics[key];
            updateDashboard();
        });

        p.sliderRef = sliderInput;
        p.valRef = document.getElementById(`val-${key}`);
    }
}

function initRadarChart() {
    const ctx = document.getElementById('radarChart').getContext('2d');
    const labels = Object.values(PARAM_CONFIGS).map(p => p.label.split(' ')[0]);

    radarChartInstance = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Current Repository',
                    data: new Array(10).fill(0),
                    backgroundColor: 'rgba(56, 189, 248, 0.25)',
                    borderColor: '#38bdf8',
                    borderWidth: 2,
                    pointBackgroundColor: '#38bdf8'
                },
                {
                    label: 'Critical Baseline (0.400)',
                    data: [0.5, 0.95, 0.45, 0.7, 0.4, 0.5, 0.4, 0.4, 0.5, 0.4],
                    backgroundColor: 'rgba(74, 222, 128, 0.1)',
                    borderColor: '#4ade80',
                    borderWidth: 1.5,
                    borderDash: [4, 4],
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    grid: { color: 'rgba(255, 255, 255, 0.08)' },
                    pointLabels: { color: '#94a3b8', font: { size: 10 } },
                    ticks: { display: false, min: 0, max: 1 }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#f1f5f9', font: { size: 11 } }
                }
            }
        }
    });
}

function updateDashboard() {
    const { score, normScores } = calculateCriticalityScore(currentMetrics);
    
    // Update Score Gauge
    const scoreDisplay = document.getElementById('scoreDisplay');
    scoreDisplay.textContent = score.toFixed(3);

    const circ = 251.3; // Total arc length of gauge
    const offset = circ - (score * circ);
    const gaugeFill = document.getElementById('gaugeFill');
    gaugeFill.style.strokeDashoffset = offset;

    // Update Status Badge & Color Glow
    const statusBadge = document.getElementById('statusBadge');
    if (score >= CRITICAL_THRESHOLD) {
        gaugeFill.style.stroke = '#4ade80'; // Green
        statusBadge.style.color = '#4ade80';
        statusBadge.style.background = 'rgba(74, 222, 128, 0.15)';
        statusBadge.style.border = '1px solid rgba(74, 222, 128, 0.4)';
        statusBadge.textContent = 'Critical Infrastructure ✓';
    } else if (score >= 0.250) {
        gaugeFill.style.stroke = '#facc15'; // Amber
        statusBadge.style.color = '#facc15';
        statusBadge.style.background = 'rgba(250, 204, 21, 0.15)';
        statusBadge.style.border = '1px solid rgba(250, 204, 21, 0.4)';
        statusBadge.textContent = 'Elevated Importance';
    } else {
        gaugeFill.style.stroke = '#f87171'; // Red
        statusBadge.style.color = '#f87171';
        statusBadge.style.background = 'rgba(248, 113, 113, 0.15)';
        statusBadge.style.border = '1px solid rgba(248, 113, 113, 0.4)';
        statusBadge.textContent = 'Standard Project';
    }

    // Update Radar Chart Data
    if (radarChartInstance) {
        const normValues = Object.keys(PARAM_CONFIGS).map(k => normScores[k]);
        radarChartInstance.data.datasets[0].data = normValues;
        radarChartInstance.update();
    }

    // Update Recommendations List
    updateRecommendations(score);
}

function updateRecommendations(score) {
    const list = document.getElementById('recommendationsList');
    list.innerHTML = '';

    const recs = [];
    if (currentMetrics.contributor_count < 30) {
        recs.push("Increase maintainer diversity: Aim for 30+ distinct contributors across multiple organizations.");
    }
    if (currentMetrics.commit_frequency < 10) {
        recs.push("Accelerate commit cadence: Regular weekly commits boost commit_frequency scores log-scale.");
    }
    if (currentMetrics.recent_releases_count < 6) {
        recs.push("Publish frequent semantic releases: Aim for monthly or bi-weekly versioned releases.");
    }
    if (currentMetrics.dependents_count < 1000) {
        recs.push("Expand downstream package adoption: Register package distributions to increase dependents_count.");
    }
    if (score >= CRITICAL_THRESHOLD) {
        recs.unshift("✓ Meets OpenSSF Critical Infrastructure benchmarks ($\text{Score} \\ge 0.400$)!");
    }

    recs.slice(0, 4).forEach(text => {
        const li = document.createElement('li');
        li.textContent = text;
        list.appendChild(li);
    });
}

function initEventListeners() {
    // Reset Button
    document.getElementById('resetBtn').addEventListener('click', () => {
        currentMetrics = {
            created_since: 12, updated_since: 2, contributor_count: 5, org_count: 1,
            commit_frequency: 2, recent_releases_count: 1, updated_issues_count: 20,
            closed_issues_count: 15, comment_frequency: 2, dependents_count: 50
        };
        syncSlidersUI();
    });

    // Elevate to 0.400+ Target Optimizer
    document.getElementById('optimizeBtn').addEventListener('click', () => {
        currentMetrics = {
            created_since: 60, updated_since: 0, contributor_count: 150, org_count: 10,
            commit_frequency: 25, recent_releases_count: 12, updated_issues_count: 500,
            closed_issues_count: 450, comment_frequency: 6.5, dependents_count: 5000
        };
        syncSlidersUI();
    });

    // Preset Pills
    document.querySelectorAll('.pill').forEach(pill => {
        pill.addEventListener('click', (e) => {
            const repoPath = e.target.dataset.repo;
            document.getElementById('repoSearchInput').value = repoPath;
            fetchGitHubRepo(repoPath);
        });
    });

    // Search Button
    document.getElementById('searchBtn').addEventListener('click', () => {
        const query = document.getElementById('repoSearchInput').value.trim();
        if (query) fetchGitHubRepo(query);
    });
}

function syncSlidersUI() {
    for (const [key, p] of Object.entries(PARAM_CONFIGS)) {
        if (p.sliderRef) p.sliderRef.value = currentMetrics[key];
        if (p.valRef) p.valRef.textContent = currentMetrics[key];
    }
    updateDashboard();
}

// Live GitHub Repository Fetcher
async function fetchGitHubRepo(repoPath) {
    const searchBtn = document.getElementById('searchBtn');
    searchBtn.textContent = "Analyzing...";
    searchBtn.disabled = true;

    try {
        // Try calling local backend API first, if available
        let res = await fetch(`http://localhost:8000/api/v1/analyze/${repoPath}`).catch(() => null);

        if (res && res.ok) {
            const data = await res.json();
            currentMetrics = data.metrics;
            showMetaBar(data.stars, data.forks, data.open_issues);
            syncSlidersUI();
        } else {
            // Direct Browser GitHub REST API Query
            const ghRes = await fetch(`https://api.github.com/repos/${repoPath}`);
            if (!ghRes.ok) throw new Error(`Repository '${repoPath}' not found on GitHub.`);

            const data = await ghRes.json();
            
            // Map live metrics
            const createdDate = new Date(data.created_at);
            const pushedDate = new Date(data.pushed_at);
            const now = new Date();

            const ageMonths = Math.max(1, (now - createdDate) / (1000 * 3600 * 24 * 30.4375));
            const inactivityMonths = Math.max(0, (now - pushedDate) / (1000 * 3600 * 24 * 30.4375));

            const stars = data.stargazers_count || 0;
            const forks = data.forks_count || 0;
            const openIssues = data.open_issues_count || 0;

            const estContribs = Math.max(2, Math.min(5000, Math.floor(forks * 0.15 + stars * 0.02 + 5)));
            const estOrgs = Math.max(1, Math.min(10, Math.floor(estContribs * 0.15 + 1)));

            currentMetrics = {
                created_since: Math.round(ageMonths),
                updated_since: Math.round(inactivityMonths * 10) / 10,
                contributor_count: estContribs,
                org_count: estOrgs,
                commit_frequency: Math.round((estContribs * 0.6 + forks * 0.05) * 10) / 10,
                recent_releases_count: Math.min(26, Math.floor(stars / 200) + 4),
                updated_issues_count: Math.max(openIssues, Math.floor(stars * 0.1)),
                closed_issues_count: Math.floor(openIssues * 0.8),
                comment_frequency: 4.5,
                dependents_count: Math.floor(Math.pow(forks, 1.3) * 2 + stars * 1.5)
            };

            showMetaBar(stars, forks, openIssues);
            syncSlidersUI();
        }
    } catch (err) {
        alert(err.message || "Failed to analyze repository.");
    } finally {
        searchBtn.textContent = "Analyze Repository";
        searchBtn.disabled = false;
    }
}

function showMetaBar(stars, forks, openIssues) {
    const metaBar = document.getElementById('repoMetaBar');
    metaBar.style.display = 'flex';
    document.getElementById('metaStars').textContent = stars.toLocaleString();
    document.getElementById('metaForks').textContent = forks.toLocaleString();
    document.getElementById('metaIssues').textContent = openIssues.toLocaleString();
}
