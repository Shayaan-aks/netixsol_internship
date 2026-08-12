import { useEffect, useState } from 'react';
import { Calendar as CalendarIcon, Clock, User, Plus } from 'lucide-react';
import { api } from '../services/api';
import './Appointments.css';

export function Appointments() {
  const [appointments, setAppointments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const data = await api.getAppointments();
      setAppointments(data);
      setLoading(false);
    }
    load();
  }, []);

  return (
    <div className="appointments-page animate-fade-in">
      <div className="page-header">
        <h1>Appointments</h1>
        <button className="btn btn-primary"><Plus size={18} /> Book Appointment</button>
      </div>

      <div className="calendar-view glass-card">
        {loading ? (
          <div className="loading-state">Loading calendar...</div>
        ) : (
          <div className="appointments-list">
            <div className="timeline-header">Upcoming Meetings</div>
            {appointments.map(apt => (
              <div key={apt.id} className="appointment-card glass">
                <div className="apt-time-badge">
                  <Clock size={16} />
                  <span>{apt.time}</span>
                </div>
                <div className="apt-details">
                  <h3>Meeting with {apt.customerName}</h3>
                  <div className="apt-meta">
                    <span><CalendarIcon size={14} /> {apt.date}</span>
                    <span><User size={14} /> {apt.customerPhone}</span>
                  </div>
                </div>
                <div className={`apt-status badge ${apt.status === 'Confirmed' ? 'badge-success' : 'badge-warning'}`}>
                  {apt.status}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
