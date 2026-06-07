document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    lucide.createIcons();

    // DOM Elements
    const calcForm = document.getElementById('calcForm');
    const plateNumberInput = document.getElementById('plateNumber');
    const ownerNameInput = document.getElementById('ownerName');
    const lastServiceDateInput = document.getElementById('lastServiceDate');
    const currentOdometerInput = document.getElementById('currentOdometer');
    const dailyDistanceInput = document.getElementById('dailyDistance');
    const complaintsInput = document.getElementById('complaints');
    const symptomChips = document.getElementById('symptomChips');
    
    // Buttons
    const btnCalculate = document.getElementById('btnCalculate');
    const btnSaveTicket = document.getElementById('btnSaveTicket');
    const btnTrack = document.getElementById('btnTrack');
    const trackPlateInput = document.getElementById('trackPlateInput');
    
    // Placeholders & Containers
    const resultsPlaceholder = document.getElementById('resultsPlaceholder');
    const resultsContent = document.getElementById('resultsContent');
    const historySection = document.getElementById('historySection');
    const historyTimeline = document.getElementById('historyTimeline');
    
    // Outputs - Scheduler
    const oilProgressCircle = document.getElementById('oilProgressCircle');
    const oilLifePctText = document.getElementById('oilLifePct');
    const oilRemOdoText = document.getElementById('oilRemOdo');
    const oilRemDaysText = document.getElementById('oilRemDays');
    const oilTargetDateText = document.getElementById('oilTargetDate');
    
    const serviceProgressCircle = document.getElementById('serviceProgressCircle');
    const serviceLifePctText = document.getElementById('serviceLifePct');
    const serviceRemOdoText = document.getElementById('serviceRemOdo');
    const serviceRemDaysText = document.getElementById('serviceRemDays');
    const serviceTargetDateText = document.getElementById('serviceTargetDate');
    
    // Outputs - Diagnostics
    const overallStatusBadge = document.getElementById('overallStatusBadge');
    const diagTitleIcon = document.getElementById('diagTitleIcon');
    const totalRepairCostText = document.getElementById('totalRepairCost');
    const faultList = document.getElementById('faultList');
    
    // Outputs - History Header
    const histPlate = document.getElementById('histPlate');
    const histType = document.getElementById('histType');
    const histOwner = document.getElementById('histOwner');
    
    // Global variable to store active calculation
    let currentCalculation = null;

    // Set Max Date for Last Service Input to Today
    const todayStr = new Date().toISOString().split('T')[0];
    lastServiceDateInput.setAttribute('max', todayStr);
    // Set default last service date to 1 month ago
    const oneMonthAgo = new Date();
    oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
    lastServiceDateInput.value = oneMonthAgo.toISOString().split('T')[0];

    // Vehicle Type Toggle UI Styling
    const vehicleRadioButtons = document.querySelectorAll('input[name="vehicle_type"]');
    vehicleRadioButtons.forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.querySelectorAll('.vehicle-card').forEach(card => {
                card.classList.remove('active');
            });
            e.target.closest('.vehicle-card').classList.add('active');
        });
    });

    // Auto-uppercase & Formatting for Plate Numbers
    const formatPlateInput = (inputEl) => {
        inputEl.addEventListener('input', (e) => {
            let val = e.target.value.toUpperCase();
            e.target.value = val;
        });
    };
    formatPlateInput(plateNumberInput);
    formatPlateInput(trackPlateInput);

    // Quick Symptom Chips
    symptomChips.addEventListener('click', (e) => {
        const chip = e.target.closest('.chip');
        if (!chip) return;
        
        const symptomText = chip.getAttribute('data-text');
        let currentText = complaintsInput.value.trim();
        
        if (currentText === "") {
            complaintsInput.value = symptomText;
        } else {
            // Check if already ends with punctuation, if not add a comma
            if (/[.,!?]$/.test(currentText)) {
                complaintsInput.value = currentText + " " + symptomText;
            } else {
                complaintsInput.value = currentText + ", " + symptomText;
            }
        }
        complaintsInput.focus();
    });

    // Show Toast Notification
    const showToast = (message, type = 'info') => {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let iconName = 'info';
        if (type === 'success') iconName = 'check-circle';
        if (type === 'error') iconName = 'alert-triangle';
        
        toast.innerHTML = `
            <i data-lucide="${iconName}" class="toast-icon"></i>
            <span class="toast-text">${message}</span>
        `;
        
        container.appendChild(toast);
        lucide.createIcons();
        
        // Remove toast after 4 seconds
        setTimeout(() => {
            toast.classList.add('toast-out');
            toast.addEventListener('animationend', () => {
                toast.remove();
            });
        }, 3500);
    };

    // Animate Circular Progress
    const setRadialProgress = (circleEl, pctTextEl, percentage) => {
        const maxOffset = 345.5; // 2 * pi * r (r = 55)
        
        // Animate counter text
        let startVal = 0;
        const duration = 1000;
        const startTime = performance.now();
        
        // Color classification
        let strokeColor = 'var(--clr-safe)';
        let glowColor = 'var(--clr-safe-glow)';
        if (percentage < 20) {
            strokeColor = 'var(--clr-danger)';
            glowColor = 'var(--clr-danger-glow)';
        } else if (percentage < 60) {
            strokeColor = 'var(--clr-warning)';
            glowColor = 'var(--clr-warning-glow)';
        }
        
        circleEl.style.stroke = strokeColor;
        circleEl.style.filter = `drop-shadow(0 0 4px ${glowColor})`;

        const animate = (currentTime) => {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
            // Easing function outQuad
            const easeProgress = progress * (2 - progress);
            
            const currentPct = Math.round(easeProgress * percentage);
            pctTextEl.innerText = `${currentPct}%`;
            
            const offset = maxOffset - (easeProgress * percentage / 100) * maxOffset;
            circleEl.style.strokeDashoffset = offset;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    };

    // Render Calculation Results to UI
    const renderResults = (data) => {
        resultsPlaceholder.classList.add('hidden');
        resultsContent.classList.remove('hidden');
        
        const sched = data.scheduler;
        const diag = data.diagnostic;
        
        // 1. Render Oil Scheduler
        setRadialProgress(oilProgressCircle, oilLifePctText, sched.oil.life_percentage);
        oilRemOdoText.innerText = `${sched.oil.remaining_odometer.toLocaleString('id-ID')} km`;
        oilRemDaysText.innerText = `${sched.oil.remaining_days} hari`;
        oilTargetDateText.innerText = sched.oil.target_date;
        
        // 2. Render Service Scheduler
        setRadialProgress(serviceProgressCircle, serviceLifePctText, sched.service.life_percentage);
        serviceRemOdoText.innerText = `${sched.service.remaining_odometer.toLocaleString('id-ID')} km`;
        serviceRemDaysText.innerText = `${sched.service.remaining_days} hari`;
        serviceTargetDateText.innerText = sched.service.target_date;
        
        // 3. Render Diagnostics
        // Update overall badge
        overallStatusBadge.className = 'badge';
        let badgeClass = 'safe';
        let titleIcon = 'shield-check';
        let titleColor = 'var(--clr-safe)';
        
        if (diag.overall_status === 'Bahaya') {
            badgeClass = 'danger';
            titleIcon = 'alert-octagon';
            titleColor = 'var(--clr-danger)';
        } else if (diag.overall_status === 'Peringatan') {
            badgeClass = 'warning';
            titleIcon = 'alert-triangle';
            titleColor = 'var(--clr-warning)';
        }
        overallStatusBadge.classList.add(badgeClass);
        overallStatusBadge.innerText = diag.overall_status;
        
        diagTitleIcon.className = 'card-title-icon';
        diagTitleIcon.setAttribute('data-lucide', titleIcon);
        diagTitleIcon.style.color = titleColor;
        
        // Repair cost
        totalRepairCostText.innerText = `Rp ${diag.total_estimated_cost.toLocaleString('id-ID')}`;
        
        // Fault cards
        faultList.innerHTML = '';
        diag.detected_faults.forEach(fault => {
            const card = document.createElement('div');
            let severityClass = 'safe';
            if (fault.danger_level === 'Bahaya') severityClass = 'danger';
            if (fault.danger_level === 'Peringatan') severityClass = 'warning';
            
            card.className = `fault-card ${severityClass}`;
            card.innerHTML = `
                <div class="fault-card-header">
                    <div class="fault-name">${fault.name}</div>
                    <div class="fault-cost">${fault.cost_label}</div>
                </div>
                <div class="fault-recommendation">
                    <strong>Rekomendasi:</strong> ${fault.recommendation}
                </div>
            `;
            faultList.appendChild(card);
        });
        
        // Re-create icons for the diagnostic card
        lucide.createIcons();
        
        // Scroll to results on mobile viewports
        if (window.innerWidth <= 968) {
            resultsContent.scrollIntoView({ behavior: 'smooth' });
        }
    };

    // Calculate Form Submission Handler
    calcForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const vehicle_type = document.querySelector('input[name="vehicle_type"]:checked').value;
        const plate_number = plateNumberInput.value.trim();
        const owner_name = ownerNameInput.value.trim();
        const last_service_date = lastServiceDateInput.value;
        const current_odometer = parseInt(currentOdometerInput.value);
        const daily_distance = parseInt(dailyDistanceInput.value);
        const complaints = complaintsInput.value.trim();
        
        btnCalculate.disabled = true;
        btnCalculate.innerHTML = '<i data-lucide="loader-2" class="animate-spin"></i> Memproses...';
        lucide.createIcons();
        
        try {
            const response = await fetch('/api/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    vehicle_type,
                    last_service_date,
                    current_odometer,
                    daily_distance,
                    complaints
                })
            });
            
            if (!response.ok) throw new Error('API server returned an error');
            const data = await response.json();
            
            // Save results to active variable
            currentCalculation = {
                plate_number,
                owner_name,
                vehicle_type,
                last_service_date,
                current_odometer,
                daily_distance,
                complaints,
                scheduler_data: data.scheduler,
                diagnostic_data: data.diagnostic
            };
            
            renderResults(data);
            showToast('Analisis keluhan & penjadwalan berhasil dilakukan.', 'success');
            
        } catch (error) {
            console.error(error);
            showToast('Terjadi kesalahan saat memproses kalkulasi.', 'error');
        } finally {
            btnCalculate.disabled = false;
            btnCalculate.innerHTML = '<i data-lucide="wrench"></i> Hitung Jadwal & Diagnosis';
            lucide.createIcons();
        }
    });

    // Save Ticket Handler
    btnSaveTicket.addEventListener('click', async () => {
        if (!currentCalculation) {
            showToast('Tidak ada data analisis aktif untuk disimpan.', 'error');
            return;
        }
        
        btnSaveTicket.disabled = true;
        btnSaveTicket.innerHTML = '<i data-lucide="loader-2" class="animate-spin"></i> Menyimpan...';
        lucide.createIcons();
        
        try {
            const response = await fetch('/api/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentCalculation)
            });
            
            const result = await response.json();
            if (result.success) {
                showToast(result.message, 'success');
                
                // Immediately refresh history for this plate number!
                loadPlateHistory(currentCalculation.plate_number);
            } else {
                showToast(result.message || 'Gagal menyimpan tiket.', 'error');
            }
        } catch (error) {
            console.error(error);
            showToast('Terjadi kesalahan jaringan saat menyimpan tiket.', 'error');
        } finally {
            btnSaveTicket.disabled = false;
            btnSaveTicket.innerHTML = '<i data-lucide="save"></i> Simpan Laporan Ke Plat Nomor';
            lucide.createIcons();
        }
    });

    // Load Plate History Function
    const loadPlateHistory = async (plateNumber) => {
        if (!plateNumber) return;
        const cleanPlate = plateNumber.replace(/\s+/g, '').toUpperCase();
        
        try {
            const response = await fetch(`/api/track/${cleanPlate}`);
            const result = await response.json();
            
            if (result.success && result.history && result.history.length > 0) {
                // Show History Section
                historySection.classList.remove('hidden');
                
                const latest = result.history[0];
                
                // Populate history header meta
                histPlate.innerText = plateNumber.toUpperCase();
                histType.innerText = latest.vehicle_type === 'mobil' ? 'Mobil' : 'Motor';
                histOwner.innerText = latest.owner_name;
                
                // Render timeline
                historyTimeline.innerHTML = '';
                result.history.forEach((ticket, idx) => {
                    const item = document.createElement('div');
                    item.className = `timeline-item ${idx === 0 ? 'active' : ''}`;
                    
                    // Parse creation time
                    const createdDate = new Date(ticket.created_at + 'Z').toLocaleString('id-ID', {
                        day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
                    });
                    
                    let statusClass = 'safe';
                    if (ticket.diagnostic_results.overall_status === 'Bahaya') statusClass = 'danger';
                    if (ticket.diagnostic_results.overall_status === 'Peringatan') statusClass = 'warning';
                    
                    const costFormatted = `Rp ${ticket.estimated_cost.toLocaleString('id-ID')}`;
                    const complaintText = ticket.complaints ? ticket.complaints : '(Tanpa keluhan)';
                    
                    item.innerHTML = `
                        <div class="timeline-dot"></div>
                        <div class="timeline-content">
                            <div class="timeline-header">
                                <span class="timeline-date">${createdDate}</span>
                                <span class="timeline-odo">${ticket.current_odometer.toLocaleString('id-ID')} km</span>
                            </div>
                            <div class="timeline-complaint">${complaintText}</div>
                            <div class="timeline-footer">
                                <span class="timeline-status ${statusClass}">${ticket.diagnostic_results.overall_status}</span>
                                <span class="timeline-cost">${costFormatted}</span>
                            </div>
                        </div>
                    `;
                    
                    // Clicking on history timeline item loads its calculations/results back to the UI!
                    item.addEventListener('click', () => {
                        // Mark active class
                        document.querySelectorAll('.timeline-item').forEach(i => i.classList.remove('active'));
                        item.classList.add('active');
                        
                        // Render this historical ticket in results
                        const dummyCalculatedData = {
                            scheduler: {
                                vehicle_type: ticket.vehicle_type,
                                current_odometer: ticket.current_odometer,
                                daily_distance: ticket.daily_distance,
                                last_service_date: ticket.last_service_date,
                                oil: {
                                    target_odometer: ticket.next_oil_odometer,
                                    remaining_odometer: Math.max(0, ticket.next_oil_odometer - ticket.current_odometer),
                                    target_date: ticket.next_oil_date,
                                    // re-estimate days left or pull from database (we calculate it here)
                                    remaining_days: Math.max(0, Math.round((new Date(ticket.next_oil_date) - new Date()) / (1000*60*60*24))),
                                    // we can recalculate percentage
                                    life_percentage: calculateRemainingPercent(ticket.current_odometer, ticket.next_oil_odometer, ticket.vehicle_type, 'oil', ticket.last_service_date, ticket.next_oil_date)
                                },
                                service: {
                                    target_odometer: ticket.next_service_odometer,
                                    remaining_odometer: Math.max(0, ticket.next_service_odometer - ticket.current_odometer),
                                    target_date: ticket.next_service_date,
                                    remaining_days: Math.max(0, Math.round((new Date(ticket.next_service_date) - new Date()) / (1000*60*60*24))),
                                    life_percentage: calculateRemainingPercent(ticket.current_odometer, ticket.next_service_odometer, ticket.vehicle_type, 'service', ticket.last_service_date, ticket.next_service_date)
                                }
                            },
                            diagnostic: ticket.diagnostic_results
                        };
                        
                        // Populate active calculation
                        currentCalculation = {
                            plate_number: ticket.plate_number,
                            owner_name: ticket.owner_name,
                            vehicle_type: ticket.vehicle_type,
                            last_service_date: ticket.last_service_date,
                            current_odometer: ticket.current_odometer,
                            daily_distance: ticket.daily_distance,
                            complaints: ticket.complaints,
                            scheduler_data: dummyCalculatedData.scheduler,
                            diagnostic_data: dummyCalculatedData.diagnostic
                        };
                        
                        // Populate input form fields for easy re-runs!
                        populateFormFields(ticket);
                        
                        renderResults(dummyCalculatedData);
                        showToast(`Laporan tanggal ${createdDate} berhasil dimuat.`, 'success');
                    });
                    
                    historyTimeline.appendChild(item);
                });
                
                return true;
            } else {
                historySection.classList.add('hidden');
                return false;
            }
        } catch (error) {
            console.error(error);
            showToast('Gagal memuat riwayat plat nomor.', 'error');
            return false;
        }
    };

    // Calculate remaining percentage helper for historical items
    const calculateRemainingPercent = (currOdo, targetOdo, type, itemType, lastServDate, targetDateStr) => {
        let maxOdo = 3000;
        let maxDays = 90;
        if (type === 'mobil') {
            maxOdo = itemType === 'oil' ? 10000 : 20000;
            maxDays = itemType === 'oil' ? 180 : 360;
        } else {
            maxOdo = itemType === 'oil' ? 3000 : 6000;
            maxDays = itemType === 'oil' ? 90 : 180;
        }
        
        const remOdo = Math.max(0, targetOdo - currOdo);
        const odoPct = (remOdo / maxOdo) * 100;
        
        const today = new Date();
        const targetDate = new Date(targetDateStr);
        const remDays = Math.max(0, Math.round((targetDate - today) / (1000*60*60*24)));
        const timePct = (remDays / maxDays) * 100;
        
        return Math.max(0, Math.min(100, Math.min(odoPct, timePct)));
    };

    // Populate Form Fields Helper
    const populateFormFields = (ticket) => {
        // Set vehicle type radio
        document.querySelectorAll('input[name="vehicle_type"]').forEach(radio => {
            if (radio.value === ticket.vehicle_type) {
                radio.checked = true;
                radio.closest('.vehicle-card').classList.add('active');
            } else {
                radio.closest('.vehicle-card').classList.remove('active');
            }
        });
        
        plateNumberInput.value = ticket.plate_number;
        ownerNameInput.value = ticket.owner_name;
        lastServiceDateInput.value = ticket.last_service_date;
        currentOdometerInput.value = ticket.current_odometer;
        dailyDistanceInput.value = ticket.daily_distance;
        complaintsInput.value = ticket.complaints || '';
    };

    // Track Plate Button Click Handler
    btnTrack.addEventListener('click', async () => {
        const plate = trackPlateInput.value.trim();
        if (!plate) {
            showToast('Silakan masukkan nomor plat kendaraan terlebih dahulu.', 'error');
            return;
        }
        
        btnTrack.disabled = true;
        btnTrack.innerHTML = '<i data-lucide="loader-2" class="animate-spin"></i>';
        lucide.createIcons();
        
        const cleanPlate = plate.replace(/\s+/g, '').toUpperCase();
        const hasHistory = await loadPlateHistory(cleanPlate);
        
        if (hasHistory) {
            showToast(`Ditemukan riwayat untuk plat nomor ${plate.toUpperCase()}.`, 'success');
            // Auto click latest history item to load it
            const firstTimelineItem = historyTimeline.querySelector('.timeline-item');
            if (firstTimelineItem) firstTimelineItem.click();
        } else {
            showToast(`Riwayat untuk plat nomor ${plate.toUpperCase()} tidak ditemukan.`, 'error');
        }
        
        btnTrack.disabled = false;
        btnTrack.innerHTML = 'Track';
    });

    // Support hitting enter on search bar
    trackPlateInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            btnTrack.click();
        }
    });
});
