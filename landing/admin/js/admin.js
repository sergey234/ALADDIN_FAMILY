/**
 * Admin Dashboard - JavaScript
 * Работа с API и управление dashboard
 */

// API Configuration
const API_BASE = window.location.origin;
const ADMIN_KEY = localStorage.getItem('adminKey');

// API Helper Functions
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    'X-Admin-Key': ADMIN_KEY,
    ...options.headers
  };
  
  console.log(`📡 API Request: ${url}`, { headers: { 'X-Admin-Key': ADMIN_KEY ? '***' : 'MISSING' } });
  
  try {
    const response = await fetch(url, {
      ...options,
      headers
    });
    
    console.log(`📥 API Response: ${response.status} ${response.statusText}`);
    
    if (response.status === 401) {
      // Неавторизован - перенаправляем на страницу входа
      console.error('❌ Unauthorized - redirecting to login');
      localStorage.removeItem('adminKey');
      window.location.href = 'login.html';
      return null;
    }
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ API Error ${response.status}:`, errorText);
      throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
    }
    
    const data = await response.json();
    console.log(`✅ API Success:`, data);
    return data;
  } catch (error) {
    console.error('❌ API Error:', error);
    // Не пробрасываем ошибку дальше, возвращаем null чтобы не ломать UI
    return null;
  }
}

// Load System Metrics
async function loadSystemMetrics() {
  try {
    console.log('🔄 Loading system metrics...');
    const data = await apiRequest('/api/admin/metrics/system');
    if (!data) {
      console.warn('⚠️ No system metrics data received');
      return;
    }
    
    console.log('📊 System metrics data:', data);
    
    // Сохраняем для графиков
    window.lastSystemData = data;
    
    // Update CPU
    const cpuCard = document.getElementById('metric-cpu');
    if (cpuCard && data.cpu) {
      cpuCard.querySelector('.metric-value').textContent = `${data.cpu.percent.toFixed(1)}%`;
      cpuCard.querySelector('.metric-progress-bar').style.width = `${data.cpu.percent}%`;
    }
    
    // Update RAM
    const ramCard = document.getElementById('metric-ram');
    if (ramCard && data.ram) {
      const usedPercent = data.ram.percent;
      ramCard.querySelector('.metric-value').textContent = `${data.ram.used_gb.toFixed(1)} GB`;
      ramCard.querySelector('.metric-label').textContent = `из ${data.ram.total_gb.toFixed(1)} GB (${usedPercent.toFixed(1)}%)`;
      ramCard.querySelector('.metric-progress-bar').style.width = `${usedPercent}%`;
    }
    
    // Update Disk
    const diskCard = document.getElementById('metric-disk');
    if (diskCard && data.disk) {
      const usedPercent = data.disk.percent;
      diskCard.querySelector('.metric-value').textContent = `${data.disk.used_gb.toFixed(1)} GB`;
      diskCard.querySelector('.metric-label').textContent = `из ${data.disk.total_gb.toFixed(1)} GB (${usedPercent.toFixed(1)}%)`;
      diskCard.querySelector('.metric-progress-bar').style.width = `${usedPercent}%`;
    }
    
    // Update Network
    const networkCard = document.getElementById('metric-network');
    if (networkCard && data.network) {
      networkCard.querySelector('.metric-value').textContent = `${data.network.recv_mb.toFixed(1)} MB`;
      networkCard.querySelector('.metric-label').textContent = `Получено / ${data.network.sent_mb.toFixed(1)} MB отправлено`;
    }
    
    console.log('✅ System metrics loaded:', data);
  } catch (error) {
    console.error('❌ Error loading system metrics:', error);
  }
}

// Load Users Metrics
async function loadUsersMetrics() {
  try {
    const data = await apiRequest('/api/admin/metrics/users');
    if (!data) return;
    
    const usersCard = document.getElementById('metric-users');
    if (usersCard) {
      usersCard.querySelector('.metric-value').textContent = data.total_users || 0;
      usersCard.querySelector('.metric-label').textContent = `Активных пользователей`;
    }
    
    const subscriptionsCard = document.getElementById('metric-subscriptions');
    if (subscriptionsCard) {
      subscriptionsCard.querySelector('.metric-value').textContent = data.active_subscriptions || 0;
      subscriptionsCard.querySelector('.metric-label').textContent = `Активных подписок`;
    }
    
    const codesCard = document.getElementById('metric-codes');
    if (codesCard) {
      codesCard.querySelector('.metric-value').textContent = data.activated_codes || 0;
      codesCard.querySelector('.metric-label').textContent = `Активированных кодов`;
    }
    
    console.log('✅ Users metrics loaded:', data);
  } catch (error) {
    console.error('❌ Error loading users metrics:', error);
  }
}

// Load Threats Metrics
async function loadThreatsMetrics() {
  try {
    const data = await apiRequest('/api/admin/metrics/threats');
    if (!data) return;
    
    const threatsCard = document.getElementById('metric-threats');
    if (threatsCard) {
      threatsCard.querySelector('.metric-value').textContent = data.total_threats || 0;
      threatsCard.querySelector('.metric-label').textContent = `Всего заблокировано`;
    }
    
    const threats24hCard = document.getElementById('metric-threats-24h');
    if (threats24hCard) {
      threats24hCard.querySelector('.metric-value').textContent = data.threats_24h || 0;
      threats24hCard.querySelector('.metric-label').textContent = `За последние 24 часа`;
    }
    
    // Update threats table
    await updateThreatsTable();
    
    console.log('✅ Threats metrics loaded:', data);
  } catch (error) {
    console.error('❌ Error loading threats metrics:', error);
  }
}

// Update Users Table
async function updateUsersTable() {
  try {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;
    
    const data = await apiRequest('/api/admin/metrics/users');
    if (!data) {
      tbody.innerHTML = '<tr><td colspan="4" class="table-loading">Нет данных</td></tr>';
      return;
    }
    
    // Показываем метрики в таблице (упрощенная версия)
    // TODO: В будущем добавить endpoint для списка пользователей
    if (data.total_users === 0 && data.active_subscriptions === 0) {
      tbody.innerHTML = '<tr><td colspan="4" class="table-empty">Нет пользователей</td></tr>';
      return;
    }
    
    tbody.innerHTML = `
      <tr>
        <td>1</td>
        <td>Всего пользователей</td>
        <td>${data.active_subscriptions || 0}</td>
        <td><span class="status-badge status-active">Активен</span></td>
      </tr>
      <tr>
        <td>2</td>
        <td>Активных подписок</td>
        <td>${data.active_subscriptions || 0}</td>
        <td><span class="status-badge status-active">Активен</span></td>
      </tr>
      <tr>
        <td>3</td>
        <td>Активированных кодов</td>
        <td>${data.activated_codes || 0}</td>
        <td><span class="status-badge status-active">Активен</span></td>
      </tr>
      <tr>
        <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 20px; font-size: 12px;">
          Всего пользователей: ${data.total_users || 0} | Новых за 7 дней: ${data.new_users_7d || 0}
        </td>
      </tr>
    `;
  } catch (error) {
    console.error('❌ Error updating users table:', error);
    const tbody = document.getElementById('usersTableBody');
    if (tbody) {
      tbody.innerHTML = '<tr><td colspan="4" class="table-error">Ошибка загрузки данных: ' + error.message + '</td></tr>';
    }
  }
}

// Update Threats Table
async function updateThreatsTable() {
  try {
    const tbody = document.getElementById('threatsTableBody');
    if (!tbody) return;
    
    // Пробуем использовать admin endpoint
    let data = await apiRequest('/api/admin/threats/list?limit=5');
    
    if (data && data.threats && data.threats.length > 0) {
      tbody.innerHTML = data.threats.map((threat, index) => `
        <tr>
          <td>${threat.name || 'Неизвестно'}</td>
          <td><strong>${threat.count || 0}</strong></td>
          <td><span class="category-badge">${threat.category_name || threat.category || 'other'}</span></td>
        </tr>
      `).join('');
      return;
    }
    
    // Fallback на публичный endpoint
    const response = await fetch('/api/dashboard/public/top-threats');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const publicData = await response.json();
    if (!publicData || !publicData.items) {
      tbody.innerHTML = '<tr><td colspan="3" class="table-empty">Нет данных</td></tr>';
      return;
    }
    
    if (publicData.items.length === 0) {
      tbody.innerHTML = '<tr><td colspan="3" class="table-empty">Нет угроз</td></tr>';
      return;
    }
    
    tbody.innerHTML = publicData.items.map((threat, index) => `
      <tr>
        <td>${threat.name || 'Неизвестно'}</td>
        <td><strong>${threat.count || 0}</strong></td>
        <td><span class="category-badge">${threat.category || 'other'}</span></td>
      </tr>
    `).join('');
  } catch (error) {
    console.error('❌ Error updating threats table:', error);
    const tbody = document.getElementById('threatsTableBody');
    if (tbody) {
      tbody.innerHTML = '<tr><td colspan="3" class="table-error">Ошибка загрузки данных: ' + error.message + '</td></tr>';
    }
  }
}

// Charts
let systemChart = null;
let usersChart = null;

// Initialize Charts
function initCharts() {
  // System Metrics Chart
  const systemCtx = document.getElementById('systemChart');
  if (systemCtx) {
    systemChart = new Chart(systemCtx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          {
            label: 'CPU %',
            data: [],
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4
          },
          {
            label: 'RAM %',
            data: [],
            borderColor: 'rgb(16, 185, 129)',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4
          },
          {
            label: 'Disk %',
            data: [],
            borderColor: 'rgb(245, 158, 11)',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#e4e7eb'
            }
          }
        },
        scales: {
          x: {
            ticks: { color: '#9ca3af' },
            grid: { color: '#2d3748' }
          },
          y: {
            ticks: { color: '#9ca3af' },
            grid: { color: '#2d3748' },
            beginAtZero: true,
            max: 100
          }
        }
      }
    });
  }
  
  // Users Growth Chart
  const usersCtx = document.getElementById('usersChart');
  if (usersCtx) {
    usersChart = new Chart(usersCtx, {
      type: 'bar',
      data: {
        labels: [],
        datasets: [{
          label: 'Пользователи',
          data: [],
          backgroundColor: 'rgba(59, 130, 246, 0.5)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#e4e7eb'
            }
          }
        },
        scales: {
          x: {
            ticks: { color: '#9ca3af' },
            grid: { color: '#2d3748' }
          },
          y: {
            ticks: { color: '#9ca3af' },
            grid: { color: '#2d3748' },
            beginAtZero: true
          }
        }
      }
    });
  }
}

// Update Charts
function updateCharts(systemData, usersData) {
  console.log('📊 Updating charts:', { systemData: !!systemData, usersData: !!usersData });
  
  if (systemChart && systemData) {
    const now = new Date();
    const timeLabel = now.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    
    // Добавляем новые данные
    systemChart.data.labels.push(timeLabel);
    systemChart.data.datasets[0].data.push(systemData.cpu?.percent || 0);
    systemChart.data.datasets[1].data.push(systemData.ram?.percent || 0);
    systemChart.data.datasets[2].data.push(systemData.disk?.percent || 0);
    
    // Ограничиваем до 24 точек (24 часа)
    if (systemChart.data.labels.length > 24) {
      systemChart.data.labels.shift();
      systemChart.data.datasets.forEach(dataset => dataset.data.shift());
    }
    
    systemChart.update('none');
    console.log('✅ System chart updated');
  } else if (systemChart) {
    console.warn('⚠️ System chart exists but no data');
  } else {
    console.warn('⚠️ System chart not initialized');
  }
  
  if (usersChart && usersData) {
    // Обновляем график пользователей (упрощенная версия)
    usersChart.data.labels = ['Всего', 'Подписки', 'Коды'];
    usersChart.data.datasets[0].data = [
      usersData.total_users || 0,
      usersData.active_subscriptions || 0,
      usersData.activated_codes || 0
    ];
    usersChart.update();
    console.log('✅ Users chart updated');
  } else if (usersChart) {
    console.warn('⚠️ Users chart exists but no data');
  } else {
    console.warn('⚠️ Users chart not initialized');
  }
}

// Load All Metrics
async function loadAllMetrics() {
  try {
    console.log('🔄 Loading all metrics...');
    
    const [systemData, usersData, threatsData] = await Promise.all([
      apiRequest('/api/admin/metrics/system').catch(err => {
        console.error('❌ Error loading system metrics:', err);
        return null;
      }),
      apiRequest('/api/admin/metrics/users').catch(err => {
        console.error('❌ Error loading users metrics:', err);
        return null;
      }),
      apiRequest('/api/admin/metrics/threats').catch(err => {
        console.error('❌ Error loading threats metrics:', err);
        return null;
      })
    ]);
    
    console.log('📊 Data loaded:', {
      system: !!systemData,
      users: !!usersData,
      threats: !!threatsData
    });
    
    if (systemData) {
      await loadSystemMetrics();
      updateCharts(systemData, usersData);
    }
    if (usersData) {
      await loadUsersMetrics();
      await updateUsersTable();
      if (!systemData) {
        updateCharts(null, usersData);
      }
    }
    if (threatsData) {
      await loadThreatsMetrics();
      await updateThreatsTable();
    }
    
    console.log('✅ All metrics loaded');
  } catch (error) {
    console.error('❌ Error loading all metrics:', error);
  }
}

// Logout
function logout() {
  if (confirm('Вы уверены, что хотите выйти?')) {
    localStorage.removeItem('adminKey');
    window.location.href = 'login.html';
  }
}

// Initialize Dashboard
function initDashboard() {
  // Check authentication
  if (!ADMIN_KEY) {
    window.location.href = 'login.html';
    return;
  }
  
  // Initialize charts
  initCharts();
  
  // Load metrics on page load
  loadAllMetrics();
  
  // Auto-refresh every 30 seconds
  setInterval(loadAllMetrics, 30000);
  
  // Setup logout button
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }
}

// Export functions
window.adminAPI = {
  apiRequest,
  loadSystemMetrics,
  loadUsersMetrics,
  loadThreatsMetrics,
  loadAllMetrics,
  updateUsersTable,
  updateThreatsTable,
  initCharts,
  updateCharts,
  logout,
  initDashboard
};

