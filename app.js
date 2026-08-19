const API_URL = 'http://localhost:5000/api';
let authToken = localStorage.getItem('aquaverde_token');
let currentUser = null;

function getHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': authToken ? `Bearer ${authToken}` : ''
    };
}

function showLogin() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
    document.getElementById('dashboard').style.display = 'none';
}

function showRegister() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
    document.getElementById('dashboard').style.display = 'none';
}

function showDashboard() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    document.getElementById('auth-buttons').style.display = 'none';
    document.getElementById('user-info').style.display = 'flex';
}

async function register() {
    const name = document.getElementById('reg-name').value;
    const phone = document.getElementById('reg-phone').value;
    const password = document.getElementById('reg-password').value;
    const userType = document.getElementById('reg-type').value;

    if (!phone || !password) {
        alert('لطفاً شماره موبایل و رمز عبور را وارد کنید');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                full_name: name || 'کاربر',
                phone: phone,
                password: password,
                user_type: userType
            })
        });

        const data = await response.json();
        if (response.ok) {
            alert('✅ ثبت‌نام موفق! لطفاً وارد شوید.');
            showLogin();
            document.getElementById('login-phone').value = phone;
        } else {
            alert('❌ خطا: ' + data.error);
        }
    } catch (error) {
        alert('❌ خطا در ارتباط با سرور');
        console.error(error);
    }
}

async function login() {
    const phone = document.getElementById('login-phone').value;
    const password = document.getElementById('login-password').value;

    if (!phone || !password) {
        alert('لطفاً شماره موبایل و رمز عبور را وارد کنید');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, password })
        });

        const data = await response.json();
        if (response.ok) {
            authToken = data.token;
            currentUser = data;
            localStorage.setItem('aquaverde_token', authToken);
            document.getElementById('user-name').textContent = data.full_name || data.user_type;
            showDashboard();
            loadDashboard();
        } else {
            alert('❌ خطا: ' + data.error);
        }
    } catch (error) {
        alert('❌ خطا در ارتباط با سرور');
        console.error(error);
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('aquaverde_token');
    document.getElementById('auth-buttons').style.display = 'flex';
    document.getElementById('user-info').style.display = 'none';
    document.getElementById('dashboard').style.display = 'none';
    showLogin();
}

async function loadDashboard() {
    await loadProfile();
    await loadFarms();
    await loadMarketVWUs();
    await loadVWUCount();
    if (currentUser && currentUser.user_type === 'industry') {
        document.getElementById('esg-section').style.display = 'block';
        await loadESGReport();
    } else {
        document.getElementById('esg-section').style.display = 'none';
    }
}

async function loadProfile() {
    try {
        const response = await fetch(`${API_URL}/profile`, {
            headers: getHeaders()
        });
        const data = await response.json();
        if (response.ok) {
            document.getElementById('user-balance').textContent = data.balance.toLocaleString() + ' تومان';
            document.getElementById('farms-count').textContent = data.farms_count;
            currentUser = { ...currentUser, ...data };
        }
    } catch (error) {
        console.error('خطا در دریافت پروفایل:', error);
    }
}

async function loadFarms() {
    try {
        const response = await fetch(`${API_URL}/farms`, {
            headers: getHeaders()
        });
        const data = await response.json();
        const select = document.getElementById('vwu-farm-select');
        if (select) {
            select.innerHTML = '<option value="">انتخاب مزرعه...</option>';
            data.forEach(farm => {
                select.innerHTML += `<option value="${farm.id}">${farm.name} (${farm.area} هکتار - ${farm.crop_type || 'نامشخص'})</option>`;
            });
        }
    } catch (error) {
        console.error('خطا در دریافت مزارع:', error);
    }
}

async function loadVWUCount() {
    try {
        const response = await fetch(`${API_URL}/vwu/market`);
        const data = await response.json();
        document.getElementById('vwu-count').textContent = data.length;
    } catch (error) {
        console.error('خطا در دریافت تعداد VWU:', error);
    }
}

async function createFarm() {
    const name = document.getElementById('farm-name').value;
    const area = document.getElementById('farm-area').value;
    const crop = document.getElementById('farm-crop').value;
    const region = document.getElementById('farm-region').value;

    if (!name || !area) {
        alert('لطفاً نام و مساحت مزرعه را وارد کنید');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/farms`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                name: name,
                area: parseFloat(area),
                crop_type: crop,
                region: region
            })
        });
        const data = await response.json();
        if (response.ok) {
            alert('✅ مزرعه با موفقیت ثبت شد!');
            document.getElementById('farm-name').value = '';
            document.getElementById('farm-area').value = '';
            document.getElementById('farm-crop').value = '';
            document.getElementById('farm-region').value = '';
            loadFarms();
            loadProfile();
        } else {
            alert('❌ خطا: ' + data.error);
        }
    } catch (error) {
        alert('❌ خطا در ارتباط با سرور');
        console.error(error);
    }
}

async function createVWU() {
    const farmId = document.getElementById('vwu-farm-select').value;
    const waterSaved = document.getElementById('vwu-water-saved').value;
    const price = document.getElementById('vwu-price').value;
    const messageDiv = document.getElementById('vwu-message');

    if (!farmId) {
        messageDiv.style.display = 'block';
        messageDiv.style.background = '#fed7d7';
        messageDiv.style.color = '#c53030';
        messageDiv.innerHTML = '❌ لطفاً یک مزرعه انتخاب کنید.';
        return;
    }
    
    if (!waterSaved || parseFloat(waterSaved) <= 0) {
        messageDiv.style.display = 'block';
        messageDiv.style.background = '#fed7d7';
        messageDiv.style.color = '#c53030';
        messageDiv.innerHTML = '❌ میزان صرفه‌جویی باید بیشتر از صفر باشد.';
        return;
    }

    try {
        const response = await fetch(`${API_URL}/vwu`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                farm_id: parseInt(farmId),
                water_saved: parseFloat(waterSaved),
                price_per_unit: parseFloat(price) || 500
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageDiv.style.display = 'block';
            messageDiv.style.background = '#c6f6d5';
            messageDiv.style.color = '#276749';
            messageDiv.innerHTML = `✅ VWU با موفقیت ثبت شد! شماره سریال: ${data.batch_number} - منتظر تایید حسابرس باشید.`;
            document.getElementById('vwu-water-saved').value = '';
            document.getElementById('vwu-price').value = '500';
            loadMarketVWUs();
            loadVWUCount();
        } else {
            messageDiv.style.display = 'block';
            messageDiv.style.background = '#fed7d7';
            messageDiv.style.color = '#c53030';
            messageDiv.innerHTML = `❌ خطا: ${data.error}`;
        }
    } catch (error) {
        messageDiv.style.display = 'block';
        messageDiv.style.background = '#fed7d7';
        messageDiv.style.color = '#c53030';
        messageDiv.innerHTML = '❌ خطا در ارتباط با سرور';
        console.error(error);
    }
}

async function loadMarketVWUs() {
    try {
        const response = await fetch(`${API_URL}/vwu/market`);
        const data = await response.json();
        const container = document.getElementById('market-vwus');
        if (data.length === 0) {
            container.innerHTML = '<p style="color:#718096; text-align:center; padding:30px;">هیچ VWU برای فروش موجود نیست</p>';
            return;
        }
        container.innerHTML = data.map(vwu => `
            <div class="vwu-card">
                <h4>📦 ${vwu.batch_number}</h4>
                <p><strong>مزرعه:</strong> ${vwu.farm_name || 'نامشخص'}</p>
                <p><strong>💧 صرفه‌جویی:</strong> ${vwu.water_saved.toLocaleString()} مترمکعب</p>
                <p><strong>💰 قیمت هر واحد:</strong> ${vwu.price_per_unit.toLocaleString()} تومان</p>
                <p class="price"><strong>📊 قیمت کل:</strong> ${vwu.total_price.toLocaleString()} تومان</p>
                <p style="font-size:12px; color:#a0aec0;">ثبت شده در: ${new Date(vwu.created_at).toLocaleDateString('fa-IR')}</p>
                <button onclick="buyVWU(${vwu.id})">🛒 خرید</button>
            </div>
        `).join('');
    } catch (error) {
        console.error('خطا در دریافت بازار:', error);
        document.getElementById('market-vwus').innerHTML = '<p style="color:#e53e3e;">❌ خطا در بارگذاری بازار</p>';
    }
}

async function buyVWU(vwuId) {
    if (!authToken) {
        alert('لطفاً ابتدا وارد شوید');
        return;
    }
    if (!confirm('آیا از خرید این VWU مطمئن هستید؟')) return;
    try {
        const response = await fetch(`${API_URL}/vwu/buy`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ vwu_id: vwuId })
        });
        const data = await response.json();
        if (response.ok) {
            alert('✅ خرید با موفقیت انجام شد!');
            sendNotification('خرید شما با موفقیت انجام شد! VWU به حساب شما اضافه شد.');
            loadDashboard();
        } else {
            alert('❌ خطا: ' + data.error);
        }
    } catch (error) {
        alert('❌ خطا در ارتباط با سرور');
        console.error(error);
    }
}

async function loadESGReport() {
    if (!currentUser || currentUser.user_type !== 'industry') return;
    try {
        const response = await fetch(`${API_URL}/industry/esg-report`, {
            headers: getHeaders()
        });
        const data = await response.json();
        document.getElementById('total-bought').textContent = data.total_vwu_bought || 0;
        document.getElementById('co2-saved').textContent = (data.total_vwu_bought * 0.5).toLocaleString();
        document.getElementById('trees-saved').textContent = Math.floor(data.total_vwu_bought / 1000);
    } catch (error) {
        console.error('خطا در دریافت گزارش ESG:', error);
    }
}

function generateReport() {
    const messageDiv = document.getElementById('report-message');
    messageDiv.innerHTML = '🔄 در حال تولید گزارش...';
    setTimeout(() => {
        messageDiv.innerHTML = '✅ گزارش با موفقیت تولید شد. نسخه PDF به زودی در دسترس خواهد بود.';
    }, 2000);
}

function sendNotification(message) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('💧 آکواورد', {
            body: message,
            icon: 'https://aquaverde.ir/favicon.ico'
        });
    }
}

if ('Notification' in window) {
    Notification.requestPermission();
}

if (authToken) {
    fetch(`${API_URL}/profile`, { headers: getHeaders() })
        .then(res => {
            if (res.ok) return res.json();
            else {
                localStorage.removeItem('aquaverde_token');
                authToken = null;
                showLogin();
                throw new Error('توکن نامعتبر');
            }
        })
        .then(data => {
            currentUser = data;
            document.getElementById('user-name').textContent = data.full_name || data.user_type || 'کاربر';
            showDashboard();
            loadDashboard();
        })
        .catch(() => {});
} else {
    showLogin();
}