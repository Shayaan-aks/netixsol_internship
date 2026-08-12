import { Bell, Search, User } from 'lucide-react';
import './Topbar.css';

export function Topbar() {
  return (
    <header className="topbar glass animate-fade-in">
      <div className="search-bar">
        <Search size={18} className="search-icon" />
        <input type="text" placeholder="Search properties, customers, appointments..." />
      </div>

      <div className="topbar-actions">
        <button className="action-btn">
          <Bell size={20} />
          <span className="notification-dot"></span>
        </button>
        <div className="user-profile">
          <div className="avatar">
            <User size={20} />
          </div>
          <div className="user-info">
            <span className="user-name">Admin User</span>
            <span className="user-role">Real Estate Agent</span>
          </div>
        </div>
      </div>
    </header>
  );
}
