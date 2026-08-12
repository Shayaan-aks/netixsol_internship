import { useEffect, useState } from 'react';
import { Search, MapPin, Bed, Bath, Square } from 'lucide-react';
import { api } from '../services/api';
import './Properties.css';

export function Properties() {
  const [properties, setProperties] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadProperties();
  }, []);

  async function loadProperties(query?: string) {
    setLoading(true);
    const data = await api.searchProperties(query);
    setProperties(data);
    setLoading(false);
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadProperties(search);
  };

  const formatPrice = (price: number) => {
    if (price >= 10000000) return `Rs. ${(price / 10000000).toFixed(2)} Crore`;
    if (price >= 100000) return `Rs. ${(price / 100000).toFixed(2)} Lac`;
    return `Rs. ${price.toLocaleString()}`;
  };

  return (
    <div className="properties-page animate-fade-in">
      <div className="page-header">
        <h1>Properties Inventory</h1>
        <form className="property-search" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Search by location, title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" className="btn btn-primary">
            <Search size={18} /> Search
          </button>
        </form>
      </div>

      {loading ? (
        <div className="loading-state">Loading properties...</div>
      ) : (
        <div className="properties-grid">
          {properties.map((prop) => (
            <div key={prop.id} className="property-card glass-card">
              <div className="property-image">
                <img src={prop.image} alt={prop.title} />
                <span className={`status-badge ${prop.status === 'Available' ? 'badge-success' : 'badge-danger'}`}>
                  {prop.status}
                </span>
              </div>
              <div className="property-content">
                <h2 className="property-price">{formatPrice(prop.price)}</h2>
                <h3 className="property-title">{prop.title}</h3>
                <p className="property-location"><MapPin size={14} /> {prop.location}</p>
                
                <div className="property-features">
                  <div className="feature"><Bed size={16} /> <span>{prop.beds} Beds</span></div>
                  <div className="feature"><Bath size={16} /> <span>{prop.baths} Baths</span></div>
                  <div className="feature"><Square size={16} /> <span>{prop.area}</span></div>
                </div>
                
                <div className="property-actions">
                  <button className="btn btn-primary w-full">View Details</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
