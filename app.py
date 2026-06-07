from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import database
import diagnostic_engine

app = Flask(__name__)

# Initialize database
database.init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json or {}
    
    vehicle_type = data.get('vehicle_type', 'motor').lower()
    last_service_str = data.get('last_service_date', '')
    current_odometer = int(data.get('current_odometer', 0))
    daily_distance = int(data.get('daily_distance', 0))
    complaints = data.get('complaints', '')
    
    # Parse last service date
    try:
        last_service_date = datetime.strptime(last_service_str, '%Y-%m-%d')
    except ValueError:
        last_service_date = datetime.now()
        
    today = datetime.now()
    
    # Intervals definitions
    if vehicle_type == 'mobil':
        oil_odo_interval = 10000
        oil_time_days = 180 # 6 months
        service_odo_interval = 20000
        service_time_days = 360 # 12 months
    else: # motor
        oil_odo_interval = 3000
        oil_time_days = 90 # 3 months
        service_odo_interval = 6000
        service_time_days = 180 # 6 months
        
    # Calculate days since last service
    days_since_last = (today - last_service_date).days
    days_since_last = max(0, days_since_last)
    
    # Estimate odometer at last service
    estimated_odo_last = current_odometer - (days_since_last * daily_distance)
    estimated_odo_last = max(0, estimated_odo_last)
    
    # 1. Oil change scheduling
    target_odo_oil = estimated_odo_last + oil_odo_interval
    rem_odo_oil = target_odo_oil - current_odometer
    
    target_date_oil_time = last_service_date + timedelta(days=oil_time_days)
    rem_days_oil_time = (target_date_oil_time - today).days
    
    # Predict days left based on daily distance
    if daily_distance > 0:
        rem_days_oil_dist = max(0, rem_odo_oil) / daily_distance
    else:
        rem_days_oil_dist = 9999
        
    # Final remaining days is the minimum of time-based or distance-based
    rem_days_oil = min(rem_days_oil_time, rem_days_oil_dist)
    rem_days_oil_val = max(0, int(round(rem_days_oil)))
    target_date_oil = today + timedelta(days=rem_days_oil_val)
    
    # Oil Life Percentage
    oil_odo_pct = (max(0, rem_odo_oil) / oil_odo_interval) * 100
    oil_time_pct = (max(0, rem_days_oil_time) / oil_time_days) * 100
    oil_life_pct = max(0, min(100, min(oil_odo_pct, oil_time_pct)))
    
    # 2. General service scheduling
    target_odo_service = estimated_odo_last + service_odo_interval
    rem_odo_service = target_odo_service - current_odometer
    
    target_date_service_time = last_service_date + timedelta(days=service_time_days)
    rem_days_service_time = (target_date_service_time - today).days
    
    if daily_distance > 0:
        rem_days_service_dist = max(0, rem_odo_service) / daily_distance
    else:
        rem_days_service_dist = 9999
        
    rem_days_service = min(rem_days_service_time, rem_days_service_dist)
    rem_days_service_val = max(0, int(round(rem_days_service)))
    target_date_service = today + timedelta(days=rem_days_service_val)
    
    # Service Life Percentage
    service_odo_pct = (max(0, rem_odo_service) / service_odo_interval) * 100
    service_time_pct = (max(0, rem_days_service_time) / service_time_days) * 100
    service_life_pct = max(0, min(100, min(service_odo_pct, service_time_pct)))
    
    # 3. Diagnostics
    diagnostic_results = diagnostic_engine.diagnose_complaint(complaints, vehicle_type)
    
    result = {
        'scheduler': {
            'vehicle_type': vehicle_type,
            'current_odometer': current_odometer,
            'daily_distance': daily_distance,
            'last_service_date': last_service_str,
            'oil': {
                'target_odometer': int(target_odo_oil),
                'remaining_odometer': int(max(0, rem_odo_oil)),
                'target_date': target_date_oil.strftime('%Y-%m-%d'),
                'remaining_days': int(rem_days_oil_val),
                'life_percentage': int(round(oil_life_pct))
            },
            'service': {
                'target_odometer': int(target_odo_service),
                'remaining_odometer': int(max(0, rem_odo_service)),
                'target_date': target_date_service.strftime('%Y-%m-%d'),
                'remaining_days': int(rem_days_service_val),
                'life_percentage': int(round(service_life_pct))
            }
        },
        'diagnostic': diagnostic_results
    }
    
    return jsonify(result)

@app.route('/api/save', methods=['POST'])
def save():
    data = request.json or {}
    
    plate_number = data.get('plate_number', '')
    owner_name = data.get('owner_name', '')
    vehicle_type = data.get('vehicle_type', 'motor')
    last_service_date = data.get('last_service_date', '')
    current_odometer = int(data.get('current_odometer', 0))
    daily_distance = int(data.get('daily_distance', 0))
    complaints = data.get('complaints', '')
    
    scheduler_data = data.get('scheduler_data', {})
    diagnostic_data = data.get('diagnostic_data', {})
    
    # Extracted from calculated data
    next_oil_odometer = scheduler_data.get('oil', {}).get('target_odometer', 0)
    next_oil_date = scheduler_data.get('oil', {}).get('target_date', '')
    next_service_odometer = scheduler_data.get('service', {}).get('target_odometer', 0)
    next_service_date = scheduler_data.get('service', {}).get('target_date', '')
    estimated_cost = diagnostic_data.get('total_estimated_cost', 0)
    
    try:
        ticket_id = database.save_ticket(
            plate_number=plate_number,
            owner_name=owner_name,
            vehicle_type=vehicle_type,
            last_service_date=last_service_date,
            current_odometer=current_odometer,
            daily_distance=daily_distance,
            complaints=complaints,
            diagnostic_results=diagnostic_data,
            next_oil_odometer=next_oil_odometer,
            next_oil_date=next_oil_date,
            next_service_odometer=next_service_odometer,
            next_service_date=next_service_date,
            estimated_cost=estimated_cost
        )
        return jsonify({'success': True, 'ticket_id': ticket_id, 'message': 'Tiket laporan berhasil disimpan.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Gagal menyimpan data: {str(e)}'}), 500

@app.route('/api/track/<plate_number>', methods=['GET'])
def track(plate_number):
    try:
        history = database.get_history(plate_number)
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Gagal memuat riwayat: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
