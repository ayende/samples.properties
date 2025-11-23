const { useState, useEffect } = React;

const API_BASE = '/api';

function App() {
    const [currentView, setCurrentView] = useState('dashboard');
    const [boundsWkt, setBoundsWkt] = useState(null); 
    const [stats, setStats] = useState({
        totalProperties: 0,
        totalUnits: 0,
        vacantUnits: 0,
        openRequests: 0,
        missingDebts: 0
    });

    useEffect(() => {
        loadDashboardStats();
    }, [boundsWkt]);

    const loadDashboardStats = async () => {
        try {
            const boundsQuery = boundsWkt ? `?boundsWkt=${encodeURIComponent(boundsWkt)}` : '';

            const propertiesPromise = fetch(`${API_BASE}/properties${boundsQuery}`).then(r => r.json());
            const [properties, units, requests, debts] = await Promise.all([
                propertiesPromise,
                propertiesPromise.then((props) => props.flatMap(p => p.units || [])),
                fetch(`${API_BASE}/servicerequests/status/Open${boundsQuery}`).then(r => r.json()),
                fetch(`${API_BASE}/debtitems/missing${boundsQuery}`).then(r => r.json())
            ]);

            setStats({
                totalProperties: properties.length,
                totalUnits: units.length,
                vacantUnits: units.filter(u => u.vacantFrom).length,
                openRequests: requests.length,
                missingDebts: debts.length
            });
        } catch (error) {
            console.error('Failed to load dashboard stats:', error);
        }
    };

    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar currentView={currentView} setCurrentView={setCurrentView} />
            <main className="flex-1 overflow-y-auto p-8">
                {currentView === 'dashboard' && <Dashboard stats={stats} boundsWkt={boundsWkt} onBoundsWktChange={setBoundsWkt} />}
                {currentView === 'requests' && <ServiceRequests />}
                {currentView === 'management' && <Management />}
            </main>
        </div>
    );
}

function Sidebar({ currentView, setCurrentView }) {
    const menuItems = [
        { id: 'dashboard', name: 'Dashboard', icon: '📊' },
        { id: 'requests', name: 'Service Requests', icon: '🔧' },
        { id: 'management', name: 'Property Management', icon: '🏢' }
    ];

    return (
        <aside className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
            <div className="p-6 border-b border-gray-700">
                <h1 className="text-2xl font-bold text-blue-400">PropertySphere</h1>
                <p className="text-sm text-gray-400 mt-1">Management Portal</p>
            </div>
            <nav className="flex-1 p-4">
                {menuItems.map(item => (
                    <button
                        key={item.id}
                        onClick={() => setCurrentView(item.id)}
                        className={`w-full text-left px-4 py-3 rounded-xl mb-2 transition-smooth flex items-center gap-3 ${
                            currentView === item.id
                                ? 'bg-blue-600 text-white shadow-lg'
                                : 'text-gray-300 hover:bg-gray-700'
                        }`}
                    >
                        <span className="text-xl">{item.icon}</span>
                        <span className="font-medium">{item.name}</span>
                    </button>
                ))}
            </nav>
        </aside>
    );
}

function Dashboard({ stats, boundsWkt, onBoundsWktChange }) {
    const [recentRequests, setRecentRequests] = useState([]);
    const [missingDebts, setMissingDebts] = useState([]);
    const [properties, setProperties] = useState([]);

    useEffect(() => {
        loadDashboardData();
    }, [boundsWkt]);

    const loadDashboardData = async () => {
        try {
            const boundsQuery = boundsWkt ? `?boundsWkt=${encodeURIComponent(boundsWkt)}` : '';

            const [requests, debts, props] = await Promise.all([
                fetch(`${API_BASE}/servicerequests/status/Open${boundsQuery}`).then(r => r.json()),
                fetch(`${API_BASE}/debtitems/missing${boundsQuery}`).then(r => r.json()),
                fetch(`${API_BASE}/properties${boundsQuery}`).then(r => r.json())
            ]);

            setRecentRequests(requests.slice(0, 5));
            setMissingDebts(debts.slice(0, 5));
            setProperties(props);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    };

    const handleBoundsWktChange = (wkt) => {
        onBoundsWktChange(wkt);
    };

    return (
        <div>
            <h2 className="text-3xl font-bold mb-8 text-blue-400">Dashboard</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
                <StatCard title="Total Properties" value={stats.totalProperties} icon="🏢" />
                <StatCard title="Total Units" value={stats.totalUnits} icon="🏠" />
                <StatCard title="Vacant Units" value={stats.vacantUnits} icon="🔓" />
                <StatCard title="Open Requests" value={stats.openRequests} icon="🔧" color="text-yellow-400" />
                <StatCard title="Missing Payments" value={stats.missingDebts} icon="💰" color="text-red-400" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <div className="bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-700">
                    <h3 className="text-xl font-semibold mb-4 text-blue-400">
                        Property Locations
                        {boundsWkt && <span className="text-sm text-gray-400 ml-2">(Filtered by map view)</span>}
                    </h3>
                    <div className="bg-gray-900 rounded-lg h-64 border border-gray-600">
                        <PropertyMap properties={properties} onBoundsChange={handleBoundsWktChange} />
                    </div>
                </div>

                <div className="bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-700">
                    <h3 className="text-xl font-semibold mb-4 text-blue-400">Recent Open Service Requests</h3>
                    <div className="space-y-3">
                        {recentRequests.length === 0 ? (
                            <p className="text-gray-400 text-center py-8">No open service requests</p>
                        ) : (
                            recentRequests.map(request => (
                                <div key={request.id} className="bg-gray-900 rounded-lg p-4 border border-gray-600 hover:border-blue-500 transition-smooth">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <span className="text-blue-400 font-medium">{request.type}</span>
                                            <p className="text-gray-300 text-sm mt-1">{request.description}</p>
                                        </div>
                                        <span className="text-xs text-gray-500">{new Date(request.openedAt).toLocaleDateString()}</span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>

            <div className="bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-700">
                <h3 className="text-xl font-semibold mb-4 text-red-400">Missing Payments</h3>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="text-left border-b border-gray-700">
                                <th className="pb-3 text-gray-400 font-medium">Property</th>
                                <th className="pb-3 text-gray-400 font-medium">Unit</th>
                                <th className="pb-3 text-gray-400 font-medium">Renter(s)</th>
                                <th className="pb-3 text-gray-400 font-medium">Type</th>
                                <th className="pb-3 text-gray-400 font-medium">Due Date</th>
                                <th className="pb-3 text-gray-400 font-medium text-right">Amount Due</th>
                            </tr>
                        </thead>
                        <tbody>
                            {missingDebts.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="text-center py-8 text-gray-400">No missing payments</td>
                                </tr>
                            ) : (
                                missingDebts.map(debt => {
                                    const dueDate = new Date(debt.dueDate);
                                    const now = new Date();
                                    const prevMonth = new Date(now.getFullYear(), now.getMonth(), 1);
                                    const isOverdue = dueDate < prevMonth;
                                    return (
                                        <tr key={debt.id} className="border-b border-gray-700 hover:bg-gray-750">
                                            <td className="py-3 text-blue-400">{debt.propertyName || 'N/A'}</td>
                                            <td className="py-3 text-blue-400">{debt.unitNumber || 'N/A'}</td>
                                            <td className="py-3">
                                                {debt.renters?.map(r => `${r.firstName} ${r.lastName}`).join(', ') || 'N/A'}
                                            </td>
                                            <td className="py-3">{debt.type}</td>
                                            <td className={`py-3 ${isOverdue ? 'text-red-400' : 'text-gray-300'}`}>
                                                {dueDate.toLocaleDateString()}
                                            </td>
                                            <td className="py-3 text-right font-semibold">${debt.amountDue.toFixed(2)}</td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

function StatCard({ title, value, icon, color = 'text-blue-400' }) {
    return (
        <div className="bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-700 transition-smooth hover:shadow-xl hover:border-blue-500">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-gray-400 text-sm">{title}</p>
                    <p className={`text-3xl font-bold mt-2 ${color}`}>{value}</p>
                </div>
                <div className="text-4xl">{icon}</div>
            </div>
        </div>
    );
}


function PropertyMap({ properties, onBoundsChange }) {
    const mapRef = React.useRef(null);
    const mapInstanceRef = React.useRef(null);

    
    useEffect(() => {
        if (!mapRef.current) return;

        // Initialize map only once
        if (!mapInstanceRef.current) {
            const map = L.map(mapRef.current).setView([37.8, -96], 3); // USA view
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(map);

            // Emit bounds on map movement
            const emitBounds = () => {
                if (onBoundsChange) {
                    const bounds = map.getBounds();
                    const sw = bounds.getSouthWest();
                    const ne = bounds.getNorthEast();
                    // Rectangle polygon WKT (lon lat order, counterclockwise, closed)
                    const wkt = `POLYGON ((${sw.lng} ${sw.lat}, ${ne.lng} ${sw.lat}, ${ne.lng} ${ne.lat}, ${sw.lng} ${ne.lat}, ${sw.lng} ${sw.lat}))`;
                    onBoundsChange(wkt);
                }
            };
            
            map.on('moveend', emitBounds);
            map.on('zoomend', emitBounds);
            // Emit initial bounds after a brief delay to allow map to fully initialize
            setTimeout(emitBounds, 100);

            mapInstanceRef.current = map;
        }

        // Clear existing markers
        mapInstanceRef.current.eachLayer((layer) => {
            if (layer instanceof L.Marker) {
                mapInstanceRef.current.removeLayer(layer);
            }
        });

        // Add markers for each property
        properties.forEach(prop => {
            const marker = L.marker([prop.latitude, prop.longitude]).addTo(mapInstanceRef.current);
            marker.bindPopup(`<strong>${prop.name}</strong><br/>${prop.address}<br/>Units: ${prop.totalUnits}`);
        });
    }, [properties]);
    
    // Cleanup only on unmount
    useEffect(() => {
        return () => {
            if (mapInstanceRef.current) {
                mapInstanceRef.current.remove();
                mapInstanceRef.current = null;
            }
        };
    }, []);

    return <div id="property-map" ref={mapRef} style={{ height: '100%', borderRadius: '0.5rem' }} />;
}

function ServiceRequests() {
    const [requests, setRequests] = useState([]);
    const [filterStatus, setFilterStatus] = useState('Open');
    const [selectedRequest, setSelectedRequest] = useState(null);

    useEffect(() => {
        loadRequests();
    }, [filterStatus]);

    const loadRequests = async () => {
        try {
            const data = await fetch(`${API_BASE}/servicerequests/status/${filterStatus}`).then(r => r.json());
            setRequests(data);
        } catch (error) {
            console.error('Failed to load requests:', error);
        }
    };

    const updateStatus = async (requestId, newStatus) => {
        try {
            await fetch(`${API_BASE}/servicerequests/${requestId}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            loadRequests();
            setSelectedRequest(null);
        } catch (error) {
            console.error('Failed to update status:', error);
        }
    };

    const statuses = ['Open', 'Scheduled', 'In Progress', 'Closed', 'Canceled'];

    return (
        <div>
            <h2 className="text-3xl font-bold mb-8 text-blue-400">Service Requests</h2>
            
            <div className="mb-6 flex gap-4">
                {statuses.map(status => (
                    <button
                        key={status}
                        onClick={() => setFilterStatus(status)}
                        className={`px-4 py-2 rounded-lg transition-smooth ${
                            filterStatus === status
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                        }`}
                    >
                        {status}
                    </button>
                ))}
            </div>

            <div className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-750">
                            <tr className="text-left">
                                <th className="p-4 text-gray-400 font-medium">Type</th>
                                <th className="p-4 text-gray-400 font-medium">Description</th>
                                <th className="p-4 text-gray-400 font-medium">Status</th>
                                <th className="p-4 text-gray-400 font-medium">Opened</th>
                                <th className="p-4 text-gray-400 font-medium">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {requests.length === 0 ? (
                                <tr>
                                    <td colSpan="5" className="text-center py-8 text-gray-400">No requests found</td>
                                </tr>
                            ) : (
                                requests.map(request => (
                                    <tr key={request.id} className="border-t border-gray-700 hover:bg-gray-750">
                                        <td className="p-4 text-blue-400 font-medium">{request.type}</td>
                                        <td className="p-4">{request.description}</td>
                                        <td className="p-4">
                                            <span className={`px-3 py-1 rounded-full text-sm ${
                                                request.status === 'Open' ? 'bg-yellow-900 text-yellow-300' :
                                                request.status === 'Closed' ? 'bg-green-900 text-green-300' :
                                                'bg-blue-900 text-blue-300'
                                            }`}>
                                                {request.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-gray-400">{new Date(request.openedAt).toLocaleDateString()}</td>
                                        <td className="p-4">
                                            <button
                                                onClick={() => setSelectedRequest(request)}
                                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-smooth"
                                            >
                                                View
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {selectedRequest && (
                <Modal onClose={() => setSelectedRequest(null)}>
                    <h3 className="text-2xl font-bold mb-4 text-blue-400">Service Request Details</h3>
                    <div className="space-y-4 mb-6">
                        <div>
                            <label className="text-gray-400 text-sm">Type</label>
                            <p className="text-lg font-medium">{selectedRequest.type}</p>
                        </div>
                        <div>
                            <label className="text-gray-400 text-sm">Description</label>
                            <p className="text-lg">{selectedRequest.description}</p>
                        </div>
                        <div>
                            <label className="text-gray-400 text-sm">Current Status</label>
                            <p className="text-lg font-medium text-blue-400">{selectedRequest.status}</p>
                        </div>
                        <div>
                            <label className="text-gray-400 text-sm">Opened At</label>
                            <p className="text-lg">{new Date(selectedRequest.openedAt).toLocaleString()}</p>
                        </div>
                    </div>
                    <div>
                        <label className="text-gray-400 text-sm mb-2 block">Update Status</label>
                        <div className="flex gap-2 flex-wrap">
                            {statuses.map(status => (
                                <button
                                    key={status}
                                    onClick={() => updateStatus(selectedRequest.id, status)}
                                    className="px-4 py-2 bg-gray-700 hover:bg-blue-600 rounded-lg transition-smooth"
                                >
                                    {status}
                                </button>
                            ))}
                        </div>
                    </div>
                </Modal>
            )}
        </div>
    );
}

function Management() {
    const [properties, setProperties] = useState([]);
    const [selectedProperty, setSelectedProperty] = useState(null);
    const [units, setUnits] = useState([]);
    const [selectedUnit, setSelectedUnit] = useState(null);
    const [leases, setLeases] = useState([]);
    const [debts, setDebts] = useState([]);
    const [view, setView] = useState('properties');

    useEffect(() => {
        loadProperties();
    }, []);

    const loadProperties = async () => {
        try {
            const data = await fetch(`${API_BASE}/properties`).then(r => r.json());
            setProperties(data);
        } catch (error) {
            console.error('Failed to load properties:', error);
        }
    };

    const loadUnits = async (propertyId) => {
        try {
            const prop = properties.find(p => p.id === propertyId);
            setUnits((prop && prop.units) ? prop.units : []);
        } catch (error) {
            console.error('Failed to load units:', error);
        }
    };

    const loadLeases = async (unitId) => {
        try {
            const lease = await fetch(`${API_BASE}/leases/by-unit/${unitId}`).then(r => r.json()).catch(() => null);
            setLeases(lease ? [lease] : []);
        } catch (error) {
            console.error('Failed to load leases:', error);
        }
    };

    const selectProperty = (property) => {
        setSelectedProperty(property);
        loadUnits(property.id);
        setView('units');
    };

    const selectUnit = (unit) => {
        setSelectedUnit(unit);
        loadLeases(unit.id);
        setView('leases');
    };

    return (
        <div>
            <h2 className="text-3xl font-bold mb-8 text-blue-400">Property Management</h2>

            <div className="mb-6 flex gap-4">
                <button
                    onClick={() => setView('properties')}
                    className={`px-4 py-2 rounded-lg transition-smooth ${
                        view === 'properties' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    }`}
                >
                    Properties
                </button>
                {selectedProperty && (
                    <button
                        onClick={() => setView('units')}
                        className={`px-4 py-2 rounded-lg transition-smooth ${
                            view === 'units' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                        }`}
                    >
                        Units - {selectedProperty.name}
                    </button>
                )}
                {selectedUnit && (
                    <button
                        onClick={() => setView('leases')}
                        className={`px-4 py-2 rounded-lg transition-smooth ${
                            view === 'leases' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                        }`}
                    >
                        Lease - Unit {selectedUnit.unitNumber}
                    </button>
                )}
            </div>

            {view === 'properties' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {properties.map(property => (
                        <div
                            key={property.id}
                            onClick={() => selectProperty(property)}
                            className="bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-700 cursor-pointer transition-smooth hover:border-blue-500 hover:shadow-xl"
                        >
                            <h3 className="text-xl font-bold text-blue-400 mb-2">{property.name}</h3>
                            <p className="text-gray-300 mb-4">{property.address}</p>
                            <div className="flex justify-between text-sm text-gray-400">
                                <span>Units: {property.totalUnits}</span>
                                <span>📍 {property.latitude.toFixed(2)}, {property.longitude.toFixed(2)}</span>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {view === 'units' && (
                <div className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-gray-750">
                            <tr className="text-left">
                                <th className="p-4 text-gray-400 font-medium">Unit Number</th>
                                <th className="p-4 text-gray-400 font-medium">Status</th>
                                <th className="p-4 text-gray-400 font-medium">Vacant Since</th>
                                <th className="p-4 text-gray-400 font-medium">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {units.map(unit => (
                                <tr key={unit.id} className="border-t border-gray-700 hover:bg-gray-750">
                                    <td className="p-4 text-blue-400 font-medium">{unit.unitNumber}</td>
                                    <td className="p-4">
                                        {unit.vacantFrom ? (
                                            <span className="px-3 py-1 rounded-full text-sm bg-red-900 text-red-300">Vacant</span>
                                        ) : (
                                            <span className="px-3 py-1 rounded-full text-sm bg-green-900 text-green-300">Occupied</span>
                                        )}
                                    </td>
                                    <td className="p-4 text-gray-400">
                                        {unit.vacantFrom ? new Date(unit.vacantFrom).toLocaleDateString() : 'N/A'}
                                    </td>
                                    <td className="p-4">
                                        <button
                                            onClick={() => selectUnit(unit)}
                                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-smooth"
                                        >
                                            Manage
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {view === 'leases' && (
                <div className="space-y-6">
                    {leases.length === 0 ? (
                        <div className="bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-700 text-center">
                            <p className="text-gray-400 text-lg">No active lease for this unit</p>
                        </div>
                    ) : (
                        leases.map(lease => (
                            <div key={lease.id} className="bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-700">
                                <h3 className="text-xl font-bold text-blue-400 mb-4">Active Lease</h3>
                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    <div>
                                        <label className="text-gray-400 text-sm">Lease Amount</label>
                                        <p className="text-2xl font-bold text-green-400">${lease.leaseAmount.toFixed(2)}/mo</p>
                                    </div>
                                    <div>
                                        <label className="text-gray-400 text-sm">Status</label>
                                        <p className="text-lg">
                                            {lease.isActive ? (
                                                <span className="text-green-400">Active</span>
                                            ) : (
                                                <span className="text-red-400">Expired</span>
                                            )}
                                        </p>
                                    </div>
                                    <div>
                                        <label className="text-gray-400 text-sm">Start Date</label>
                                        <p className="text-lg">{new Date(lease.startDate).toLocaleDateString()}</p>
                                    </div>
                                    <div>
                                        <label className="text-gray-400 text-sm">End Date</label>
                                        <p className="text-lg">{new Date(lease.endDate).toLocaleDateString()}</p>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}

function Modal({ onClose, children }) {
    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
            <div
                className="bg-gray-800 rounded-xl shadow-2xl p-8 max-w-2xl w-full mx-4 border border-gray-700"
                onClick={e => e.stopPropagation()}
            >
                {children}
                <button
                    onClick={onClose}
                    className="mt-6 px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-smooth"
                >
                    Close
                </button>
            </div>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));
