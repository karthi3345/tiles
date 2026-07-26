// Studio Mathri - Main JS

// Mobile menu
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileMenu = document.getElementById('mobile-menu');
const mobileMenuIcon = document.getElementById('mobile-menu-icon');

if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', function() {
        mobileMenu.classList.toggle('hidden');
        if (mobileMenuIcon) {
            mobileMenuIcon.setAttribute('icon', mobileMenu.classList.contains('hidden') ? 'lucide:menu' : 'lucide:x');
        }
    });
    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.add('hidden');
            if (mobileMenuIcon) mobileMenuIcon.setAttribute('icon', 'lucide:menu');
        });
    });
}

// Navbar scroll shadow
const navbar = document.querySelector('nav');
if (navbar) {
    window.addEventListener('scroll', function() {
        navbar.classList.toggle('shadow-sm', window.scrollY > 50);
    });
}

// Location Search (navbar + mobile)
function setupLocationSearch(inputId, resultsId) {
    const input = document.getElementById(inputId);
    const results = document.getElementById(resultsId);
    if (!input || !results) return;

    let debounceTimer;

    input.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const q = this.value.trim();
        if (q.length < 2) { results.classList.add('hidden'); return; }
        debounceTimer = setTimeout(() => {
            fetch('/api/location-search/?q=' + encodeURIComponent(q))
                .then(r => r.json())
                .then(data => {
                    if (!data.results || data.results.length === 0) {
                        results.innerHTML = '<div class="px-4 py-3 text-sm text-slate-400">No locations found</div>';
                    } else {
                        results.innerHTML = data.results.map(r => `
                            <a href="${r.path}" class="search-result-item">
                                <span class="sr-type sr-type-${r.type}">${r.type}</span>
                                <div class="min-w-0">
                                    <div class="text-sm font-medium text-slate-900 truncate">${r.name}</div>
                                    <div class="text-[10px] text-slate-400 truncate">${r.parent}</div>
                                </div>
                            </a>
                        `).join('');
                    }
                    results.classList.remove('hidden');
                })
                .catch(() => { results.classList.add('hidden'); });
        }, 300);
    });

    input.addEventListener('focus', function() {
        if (this.value.trim().length >= 2) results.classList.remove('hidden');
    });

    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !results.contains(e.target)) {
            results.classList.add('hidden');
        }
    });
}

setupLocationSearch('nav-search', 'nav-search-results');
setupLocationSearch('mobile-search', 'mobile-search-results');