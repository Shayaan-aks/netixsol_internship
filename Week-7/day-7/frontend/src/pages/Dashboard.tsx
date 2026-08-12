import { useEffect, useState } from 'react';
import { TrendingUp, Users, Home, Calendar } from 'lucide-react';
import { api } from '../services/api';
import './Dashboard.css';

export function Dashboard() {
  const [stats, setStats] = useState({
    properties: 0,
    customers: 0,
    appointments: 0
  });

  useEffect(() => {
    async function loadData() {
      const [props, custs, apts] = await Promise.all([
        api.searchProperties(),
        api.getCustomers(),
        api.getAppointments()
      ]);
      setStats({
        properties: props.length,
        customers: custs.length,
        appointments: apts.length
      });
    }
    loadData();
  }, []);

  return (
    <div className="dashboard animate-fade-in">
      <div className="dashboard-header">
        <h1>Welcome Back, Admin</h1>
        <p>Here is what's happening with your real estate business today.</p>
      </div>

      <div className="kpi-grid">
        <div className="kpi-card glass-card">
          <div className="kpi-icon icon-blue"><Home size={24} /></div>
          <div className="kpi-info">
            <h3>Total Properties</h3>
            <h2>{stats.properties}</h2>
          </div>
          <div className="kpi-trend positive"><TrendingUp size={16} /> +12% this month</div>
        </div>

        <div className="kpi-card glass-card">
          <div className="kpi-icon icon-purple"><Users size={24} /></div>
          <div className="kpi-info">
            <h3>Active Leads</h3>
            <h2>{stats.customers}</h2>
          </div>
          <div className="kpi-trend positive"><TrendingUp size={16} /> +5% this month</div>
        </div>

        <div className="kpi-card glass-card">
          <div className="kpi-icon icon-green"><Calendar size={24} /></div>
          <div className="kpi-info">
            <h3>Appointments</h3>
            <h2>{stats.appointments}</h2>
          </div>
          <div className="kpi-trend"><TrendingUp size={16} /> +2% this week</div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="recent-activity glass-card">
          <div className="section-header">
            <h3>Recent Activity</h3>
            <button className="btn btn-outline">View All</button>
          </div>
          <ul className="activity-list">
            <li className="activity-item">
              <div className="activity-dot dot-blue"></div>
              <div className="activity-details">
                <p><strong>Ali Raza</strong> viewed <em>Luxury Villa in DHA Phase 6</em></p>
                <span>2 hours ago</span>
              </div>
            </li>
            <li className="activity-item">
              <div className="activity-dot dot-green"></div>
              <div className="activity-details">
                <p><strong>Sara Khan</strong> scheduled an appointment</p>
                <span>5 hours ago</span>
              </div>
            </li>
            <li className="activity-item">
              <div className="activity-dot dot-purple"></div>
              <div className="activity-details">
                <p>Zara AI successfully answered 15 queries today.</p>
                <span>Today</span>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
