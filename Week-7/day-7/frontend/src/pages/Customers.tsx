import { useEffect, useState } from 'react';
import { Mail, Phone, Clock, FileText, Plus } from 'lucide-react';
import { api } from '../services/api';
import './Customers.css';

export function Customers() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<any>(null);
  const [interactions, setInteractions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const data = await api.getCustomers();
      setCustomers(data);
      if (data.length > 0) {
        handleSelectCustomer(data[0]);
      }
      setLoading(false);
    }
    load();
  }, []);

  const handleSelectCustomer = async (customer: any) => {
    setSelectedCustomer(customer);
    const ints = await api.getCustomerInteractions(customer.id);
    setInteractions(ints);
  };

  if (loading) return <div className="loading-state">Loading customers...</div>;

  return (
    <div className="customers-page animate-fade-in">
      <div className="customers-sidebar glass-card">
        <div className="sidebar-header">
          <h2>Customers</h2>
          <div className="search-box">
            <input type="text" placeholder="Search customers..." />
          </div>
        </div>
        <div className="customers-list">
          {customers.map((c) => (
            <div 
              key={c.id} 
              className={`customer-list-item ${selectedCustomer?.id === c.id ? 'active' : ''}`}
              onClick={() => handleSelectCustomer(c)}
            >
              <div className="customer-avatar">
                {c.name.charAt(0)}
              </div>
              <div className="customer-list-info">
                <h4>{c.name}</h4>
                <span className={`status-dot ${c.status === 'Hot' ? 'dot-red' : 'dot-blue'}`}></span>
                <span className="customer-status">{c.status} Lead</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedCustomer && (
        <div className="customer-details glass-card">
          <div className="details-header">
            <div className="header-info">
              <div className="customer-avatar large">{selectedCustomer.name.charAt(0)}</div>
              <div>
                <h2>{selectedCustomer.name}</h2>
                <div className="contact-info">
                  <span><Phone size={14} /> {selectedCustomer.phone}</span>
                  <span><Mail size={14} /> {selectedCustomer.email}</span>
                </div>
              </div>
            </div>
            <div className="header-actions">
              <button className="btn btn-primary"><Plus size={16} /> New Interaction</button>
            </div>
          </div>

          <div className="details-content">
            <div className="info-cards">
              <div className="info-card">
                <h5>Lead Score</h5>
                <div className="score-ring">
                  <svg viewBox="0 0 36 36" className="circular-chart">
                    <path className="circle-bg"
                      d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path className="circle"
                      strokeDasharray={`${selectedCustomer.leadScore}, 100`}
                      d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <text x="18" y="20.35" className="percentage">{selectedCustomer.leadScore}</text>
                  </svg>
                </div>
              </div>
              <div className="info-card">
                <h5>Preferences</h5>
                <div className="preferences-tags">
                  {selectedCustomer.preferences.map((p: string) => (
                    <span key={p} className="badge badge-primary">{p}</span>
                  ))}
                </div>
                <h5 style={{marginTop: '1rem'}}>Budget</h5>
                <p>Rs. {(selectedCustomer.budget / 10000000).toFixed(2)} Crore</p>
              </div>
            </div>

            <div className="interactions-timeline">
              <h3><Clock size={18} /> Recent Interactions</h3>
              {interactions.length > 0 ? (
                <ul className="timeline">
                  {interactions.map(int => (
                    <li key={int.id} className="timeline-item">
                      <div className="timeline-icon"><FileText size={14} /></div>
                      <div className="timeline-content">
                        <h4>{int.type}</h4>
                        <p>{int.summary}</p>
                        <span className="time">{new Date(int.date).toLocaleString()}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="no-data">No interactions logged yet.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
