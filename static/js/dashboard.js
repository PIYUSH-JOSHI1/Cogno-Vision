class Dashboard {
    constructor() {
        this.charts = {};
        this.initializeDashboard();
    }
    
    async initializeDashboard() {
        try {
            const response = await fetch('/dashboard/data');
            const data = await response.json();
            
            if (data.success) {
                this.updateStatistics(data.statistics);
                this.createReadingProgressChart(data.reading_progress);
                this.createGameScoresChart(data.game_scores);
                this.displayRecommendations(data.recommendations);
                this.displayRecentActivity(data.recent_activities);
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }
    
    updateStatistics(stats) {
        document.getElementById('totalSessions').textContent = stats.total_sessions;
        document.getElementById('totalTime').textContent = `${stats.total_time_minutes} min`;
        document.getElementById('avgReadingSpeed').textContent = `${stats.avg_reading_speed} wpm`;
        document.getElementById('weeklyProgress').textContent = `${stats.total_sessions} sessions`;
    }
    
    createReadingProgressChart(data) {
        const ctx = document.getElementById('readingProgressChart').getContext('2d');
        
        this.charts.readingProgress = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => new Date(item.date).toLocaleDateString()),
                datasets: [
                    {
                        label: 'Reading Speed (WPM)',
                        data: data.map(item => item.avg_speed),
                        borderColor: '#4A90E2',
                        backgroundColor: 'rgba(74, 144, 226, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Accuracy (%)',
                        data: data.map(item => item.avg_accuracy),
                        borderColor: '#7ED321',
                        backgroundColor: 'rgba(126, 211, 33, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Reading Speed (WPM)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Accuracy (%)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Reading Progress Over Time'
                    }
                }
            }
        });
    }
    
    createGameScoresChart(data) {
        const ctx = document.getElementById('gameScoresChart').getContext('2d');
        
        this.charts.gameScores = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.game),
                datasets: [{
                    label: 'Average Score',
                    data: data.map(item => item.avg_score),
                    backgroundColor: [
                        'rgba(74, 144, 226, 0.8)',
                        'rgba(126, 211, 33, 0.8)',
                        'rgba(245, 166, 35, 0.8)',
                        'rgba(208, 2, 27, 0.8)',
                        'rgba(156, 39, 176, 0.8)'
                    ],
                    borderColor: [
                        '#4A90E2',
                        '#7ED321',
                        '#F5A623',
                        '#D0021B',
                        '#9C27B0'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Average Score'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Games'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Game Performance'
                    }
                }
            }
        });
    }
    
    displayRecommendations(recommendations) {
        const container = document.getElementById('recommendations');
        
        if (recommendations.length === 0) {
            container.innerHTML = '<p class="text-gray-500 italic">Great job! Keep up the good work!</p>';
            return;
        }
        
        let html = '';
        recommendations.forEach(rec => {
            const icon = rec.type === 'reading' ? '📖' : rec.type === 'games' ? '🎮' : '🚀';
            html += `
                <div class="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-400">
                    <div class="flex items-start">
                        <div class="text-2xl mr-3">${icon}</div>
                        <div>
                            <h4 class="font-semibold text-blue-800">${rec.title}</h4>
                            <p class="text-blue-600 text-sm mt-1">${rec.description}</p>
                            <button class="mt-2 text-blue-700 hover:text-blue-900 text-sm font-medium">
                                ${rec.action} →
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    displayRecentActivity(activities) {
        const container = document.getElementById('recentActivity');
        
        if (activities.length === 0) {
            container.innerHTML = '<p class="text-gray-500 italic">No recent activity</p>';
            return;
        }
        
        let html = '';
        activities.forEach(activity => {
            const icon = activity.activity_type === 'reading' ? '📖' : 
                        activity.activity_type === 'game' ? '🎮' : '🔄';
            const date = new Date(activity.created_at).toLocaleDateString();
            const time = new Date(activity.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            html += `
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div class="flex items-center">
                        <span class="text-xl mr-3">${icon}</span>
                        <div>
                            <p class="font-medium">${activity.activity_name}</p>
                            <p class="text-sm text-gray-600">${date} at ${time}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        ${activity.score ? `<p class="font-semibold">${Math.round(activity.score)}</p>` : ''}
                        ${activity.reading_speed ? `<p class="text-sm text-gray-600">${Math.round(activity.reading_speed)} wpm</p>` : ''}
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});
