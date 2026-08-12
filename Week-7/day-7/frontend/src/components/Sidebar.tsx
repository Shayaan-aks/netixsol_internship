import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Home, Users, Calendar, MessageSquare, Settings } from 'lucide-react';
import './Sidebar.css';

export function Sidebar() {
  const navItems = [
    { path: '/', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
    { path: '/properties', icon: <Home size={20} />, label: 'Properties' },
    { path: '/customers', icon: <Users size={20} />, label: 'Customers' },
    { path: '/appointments', icon: <Calendar size={20} />, label: 'Appointments' },
    { path: '/chat', icon: <MessageSquare size={20} />, label: 'Zara AI' },
  ];

  return (
    <aside className="sidebar glass animate-fade-in">
      <div className="sidebar-logo">
        <div className="logo-icon flex items-center justify-center">
          <Home size={24} color="white" />
        </div>
        <h2>NetixSol CRM</h2>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-group-label">Menu</div>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button className="nav-item">
          <Settings size={20} />
          <span>Settings</span>
        </button>
      </div>
    </aside>
  );
}
