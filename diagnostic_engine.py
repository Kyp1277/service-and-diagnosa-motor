import re

# Rule-based diagnostics database
DIAGNOSTIC_RULES = [
    {
        "id": "rem_aus",
        "name": "Kampas Rem Aus / Kerusakan Sistem Rem",
        "keywords": ["rem", "decit", "pakem", "ciet", "mencicit", "seret", "bunyi decit"],
        "danger_level": "Bahaya",
        "recommendation": "Segera lakukan pemeriksaan ketebalan kampas rem. Ganti kampas rem depan/belakang jika sudah tipis, dan periksa kondisi piringan cakram.",
        "cost": {
            "motor": {"min": 75000, "max": 150000, "label": "Rp 75.000 - Rp 150.000"},
            "mobil": {"min": 350000, "max": 750000, "label": "Rp 350.000 - Rp 750.000"}
        }
    },
    {
        "id": "mesin_overheat",
        "name": "Mesin Overheat / Masalah Sistem Pendingin",
        "keywords": ["panas", "overheat", "temperatur", "radiator", "coolant", "mendidih", "suhu"],
        "danger_level": "Bahaya",
        "recommendation": "Periksa volume air radiator (coolant) di tangki cadangan. Cari kebocoran pada selang radiator atau kerusakan pada kipas radiator dan termostat.",
        "cost": {
            "motor": {"min": 100000, "max": 250000, "label": "Rp 100.000 - Rp 250.000"},
            "mobil": {"min": 450000, "max": 1200000, "label": "Rp 450.000 - Rp 1.200.000"}
        }
    },
    {
        "id": "ring_piston_aus",
        "name": "Piston / Ring Piston Aus (Mesin Ngebul)",
        "keywords": ["asap", "ngebul", "bul", "putih", "knalpot", "kebul"],
        "danger_level": "Bahaya",
        "recommendation": "Knalpot berasap putih/hitam menandakan oli ikut terbakar atau pembakaran tidak sempurna. Perlu pemeriksaan ring piston, seal klep, atau blok silinder. Kemungkinan memerlukan overhaul mesin.",
        "cost": {
            "motor": {"min": 600000, "max": 1500000, "label": "Rp 600.000 - Rp 1.500.000"},
            "mobil": {"min": 4000000, "max": 8000000, "label": "Rp 4.000.000 - Rp 8.000.000"}
        }
    },
    {
        "id": "aki_lemah",
        "name": "Aki Lemah / Sistem Pengisian Bermasalah",
        "keywords": ["aki", "starter", "stater", "tekor", "cetrek", "hidup", "mati total", "dinamo", "accu"],
        "danger_level": "Peringatan",
        "recommendation": "Periksa tegangan aki menggunakan voltmeter. Jika di bawah 12V, lakukan pengisian daya atau ganti aki baru. Periksa juga dinamo starter dan alternator pengisian.",
        "cost": {
            "motor": {"min": 200000, "max": 350000, "label": "Rp 200.000 - Rp 350.000"},
            "mobil": {"min": 900000, "max": 1800000, "label": "Rp 900.000 - Rp 1.800.000"}
        }
    },
    {
        "id": "suspensi_aus",
        "name": "Shockbreaker / Suspensi Aus",
        "keywords": ["suspensi", "shock", "shockbreaker", "goyang", "jedug", "keras", "oleng", "bushing", "stabilizer"],
        "danger_level": "Peringatan",
        "recommendation": "Periksa kebocoran oli pada as shockbreaker. Jika suspensi terasa keras atau bergoyang berlebih, lakukan penggantian shockbreaker atau bushing karet yang aus.",
        "cost": {
            "motor": {"min": 250000, "max": 600000, "label": "Rp 250.000 - Rp 600.000"},
            "mobil": {"min": 1500000, "max": 3500000, "label": "Rp 1.500.000 - Rp 3.500.000"}
        }
    },
    {
        "id": "oli_bocor",
        "name": "Kebocoran Oli Mesin",
        "keywords": ["tetes", "bocor", "rembes", "basah", "lantai", "paking", "seal"],
        "danger_level": "Peringatan",
        "recommendation": "Identifikasi sumber kebocoran oli (apakah dari paking kopling, seal magnet, atau baut pembuangan). Ganti seal atau paking yang rusak untuk mencegah kehabisan oli mesin.",
        "cost": {
            "motor": {"min": 100000, "max": 250000, "label": "Rp 100.000 - Rp 250.000"},
            "mobil": {"min": 600000, "max": 1500000, "label": "Rp 600.000 - Rp 1.500.000"}
        }
    },
    {
        "id": "kopling_aus",
        "name": "Kampas Kopling Aus / Transmisi Selip",
        "keywords": ["kopling", "transmisi", "selip", "slip", "gigi", "pindah", "loss", "ngeden"],
        "danger_level": "Peringatan",
        "recommendation": "Jika mesin meraung tapi kecepatan tidak bertambah (kopling selip), segera ganti kampas kopling. Periksa juga kabel kopling atau oli transmisi.",
        "cost": {
            "motor": {"min": 200000, "max": 450000, "label": "Rp 200.000 - Rp 450.000"},
            "mobil": {"min": 1800000, "max": 4000000, "label": "Rp 1.800.000 - Rp 4.000.000"}
        }
    },
    {
        "id": "kemudi_oleng",
        "name": "Masalah Kemudi & Kaki-kaki (Setir Getar/Oleng)",
        "keywords": ["setir", "getar", "melayang", "oleng", "spoor", "balancing", "kemudi", "roda", "komstir"],
        "danger_level": "Peringatan",
        "recommendation": "Untuk mobil, lakukan spooring dan balancing roda. Periksa kondisi tie rod, ball joint, dan kelurusan roda. Untuk motor, periksa segitiga kemudi dan komstir.",
        "cost": {
            "motor": {"min": 100000, "max": 300000, "label": "Rp 100.000 - Rp 300.000"},
            "mobil": {"min": 250000, "max": 600000, "label": "Rp 250.000 - Rp 600.000"}
        }
    },
    {
        "id": "kelistrikan_lampu",
        "name": "Sistem Penerangan / Sekring Putus",
        "keywords": ["lampu", "redup", "mati", "bohlam", "sekring", "fiting", "konslet"],
        "danger_level": "Peringatan",
        "recommendation": "Periksa kondisi bohlam lampu dan kotak sekring. Jika sekring putus, ganti dengan kapasitas yang sesuai. Periksa perkabelan jika ada indikasi korsleting.",
        "cost": {
            "motor": {"min": 30000, "max": 100000, "label": "Rp 30.000 - Rp 100.000"},
            "mobil": {"min": 100000, "max": 300000, "label": "Rp 100.000 - Rp 300.000"}
        }
    },
    {
        "id": "mesin_brebet",
        "name": "Mesin Brebet / Busi Kotor",
        "keywords": ["brebet", "pincang", "busi", "langsam", "karburator", "injeksi", "nyendat", "mampet", "kasar"],
        "danger_level": "Peringatan",
        "recommendation": "Lakukan tune-up mesin, bersihkan/ganti busi yang kotor, serta bersihkan karburator atau injektor dari sumbatan kotoran dan air.",
        "cost": {
            "motor": {"min": 50000, "max": 150000, "label": "Rp 50.000 - Rp 150.000"},
            "mobil": {"min": 300000, "max": 800000, "label": "Rp 300.000 - Rp 800.000"}
        }
    }
]

def diagnose_complaint(complaint_text, vehicle_type):
    """
    Diagnose vehicle health based on text complaints.
    
    Parameters:
    - complaint_text (str): Free-text input from user
    - vehicle_type (str): 'mobil' or 'motor'
    
    Returns:
    - dict: {
        'detected_faults': list of dicts,
        'overall_status': 'Aman' | 'Peringatan' | 'Bahaya',
        'total_estimated_cost': int (sum of max costs or range)
      }
    """
    # Standardize vehicle type
    v_type = vehicle_type.lower()
    if v_type not in ['mobil', 'motor']:
        v_type = 'motor' # default fallback
        
    if not complaint_text or not complaint_text.strip():
        return {
            'detected_faults': [{
                'id': 'normal',
                'name': 'Kendaraan Normal',
                'danger_level': 'Aman',
                'recommendation': 'Tidak ada keluhan kritis yang dilaporkan. Kendaraan Anda dalam kondisi normal berdasarkan keluhan. Lakukan servis rutin tepat waktu untuk menjaga performa tetap optimal.',
                'cost_label': 'Rp 0',
                'cost_min': 0,
                'cost_max': 0
            }],
            'overall_status': 'Aman',
            'total_estimated_cost': 0
        }
        
    # Normalize text (lowercase, strip punctuation)
    norm_text = complaint_text.lower()
    norm_text = re.sub(r'[^\w\s]', ' ', norm_text)
    words = norm_text.split()
    
    detected_faults = []
    
    for rule in DIAGNOSTIC_RULES:
        # Check if any keyword matches as substring or exact word
        match_found = False
        for kw in rule['keywords']:
            # We match keywords as substrings, e.g. "rem" in "rem terasa blong"
            if kw in norm_text:
                match_found = True
                break
                
        if match_found:
            cost_info = rule['cost'][v_type]
            detected_faults.append({
                'id': rule['id'],
                'name': rule['name'],
                'danger_level': rule['danger_level'],
                'recommendation': rule['recommendation'],
                'cost_label': cost_info['label'],
                'cost_min': cost_info['min'],
                'cost_max': cost_info['max']
            })
            
    # If no specific matches but user entered text
    if not detected_faults:
        general_cost = 150000 if v_type == 'mobil' else 50000
        detected_faults.append({
            'id': 'general_check',
            'name': 'Pemeriksaan Umum (Gejala Tidak Spesifik)',
            'danger_level': 'Aman',
            'recommendation': 'Keluhan tidak teridentifikasi secara spesifik oleh sistem. Disarankan membawa kendaraan ke bengkel untuk pemeriksaan menyeluruh oleh mekanik (inspeksi kelistrikan, OBD scanner, atau test drive).',
            'cost_label': f"Rp {general_cost:,}".replace(',', '.'),
            'cost_min': general_cost,
            'cost_max': general_cost
        })
        
    # Determine overall status
    # Order of severity: Bahaya > Peringatan > Aman
    statuses = [f['danger_level'] for f in detected_faults]
    if 'Bahaya' in statuses:
        overall_status = 'Bahaya'
    elif 'Peringatan' in statuses:
        overall_status = 'Peringatan'
    else:
        overall_status = 'Aman'
        
    # Calculate sum of maximum costs for repair estimation
    total_cost = sum(f['cost_max'] for f in detected_faults)
    
    return {
        'detected_faults': detected_faults,
        'overall_status': overall_status,
        'total_estimated_cost': total_cost
    }

if __name__ == '__main__':
    # Test cases
    test_1 = diagnose_complaint("rem bunyi mendecit dan kurang pakem", "motor")
    print("Test 1 (Motor Rem):", test_1['overall_status'], [f['name'] for f in test_1['detected_faults']], test_1['total_estimated_cost'])
    
    test_2 = diagnose_complaint("mesin overheat dan keluar asap dari knalpot", "mobil")
    print("Test 2 (Mobil Overheat + Asap):", test_2['overall_status'], [f['name'] for f in test_2['detected_faults']], test_2['total_estimated_cost'])
    
    test_3 = diagnose_complaint("ada suara jedug jedug di ban belakang", "mobil")
    print("Test 3 (Mobil Suspensi/Kemudi):", test_3['overall_status'], [f['name'] for f in test_3['detected_faults']], test_3['total_estimated_cost'])
    
    test_4 = diagnose_complaint("", "motor")
    print("Test 4 (Empty):", test_4['overall_status'], [f['name'] for f in test_4['detected_faults']], test_4['total_estimated_cost'])
    
    test_5 = diagnose_complaint("mesin bersin bersin dan goyang", "motor")
    print("Test 5 (Unknown):", test_5['overall_status'], [f['name'] for f in test_5['detected_faults']], test_5['total_estimated_cost'])
