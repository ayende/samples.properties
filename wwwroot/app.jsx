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
                propertiesPromise.then((props) => props.flatMap(p => p.Units || [])),
                fetch(`${API_BASE}/servicerequests/status/Open${boundsQuery}`).then(r => r.json()),
                fetch(`${API_BASE}/debtitems/missing${boundsQuery}`).then(r => r.json())
            ]);

            setStats({
                totalProperties: properties.length,
                totalUnits: units.length,
                vacantUnits: units.filter(u => u.VacantFrom).length,
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
                        className={`w-full text-left px-4 py-3 rounded-xl mb-2 transition-smooth flex items-center gap-3 ${currentView === item.id
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
                                <div key={request.Id} className="bg-gray-900 rounded-lg p-4 border border-gray-600 hover:border-blue-500 transition-smooth">
                                    <div className="flex justify-between items-start">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-blue-400 font-medium">{request.Type}</span>
                                                <span className="text-gray-500 text-xs">•</span>
                                                <span className="text-gray-400 text-sm">{request.PropertyName}</span>
                                                <span className="text-gray-500 text-xs">•</span>
                                                <span className="text-gray-400 text-sm">Unit {request.UnitNumber}</span>
                                            </div>
                                            <p className="text-gray-300 text-sm mt-1">{request.Description}</p>
                                        </div>
                                        <span className="text-xs text-gray-500 ml-4 flex-shrink-0">{new Date(request.OpenedAt).toLocaleDateString()}</span>
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
                                    const dueDate = new Date(debt.DueDate);
                                    const now = new Date();
                                    const prevMonth = new Date(now.getFullYear(), now.getMonth(), 1);
                                    const isOverdue = dueDate < prevMonth;
                                    return (
                                        <tr key={debt.Id} className="border-b border-gray-700 hover:bg-gray-750">
                                            <td className="py-3 text-blue-400">{debt.PropertyName || 'N/A'}</td>
                                            <td className="py-3 text-blue-400">{debt.UnitNumber || 'N/A'}</td>
                                            <td className="py-3">
                                                {debt.Renters && debt.Renters.length > 0 ? debt.Renters.map(r => `${r.FirstName || ''} ${r.LastName || ''}`).join(', ') : 'N/A'}
                                            </td>
                                            <td className="py-3">{debt.Type || 'N/A'}</td>
                                            <td className={`py-3 ${isOverdue ? 'text-red-400' : 'text-gray-300'}`}>
                                                {dueDate.toLocaleDateString()}
                                            </td>
                                            <td className="py-3 text-right font-semibold">${debt.AmountDue ? Number(debt.AmountDue).toFixed(2) : '0.00'}</td>
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

                    // If bounds exceed world limits, send null (show all data)
                    if (sw.lng < -180 || sw.lng > 180 || ne.lng < -180 || ne.lng > 180 ||
                        sw.lat < -90 || sw.lat > 90 || ne.lat < -90 || ne.lat > 90) {
                        onBoundsChange(null);
                        return;
                    }

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
            if (prop.Latitude != null && prop.Longitude != null) {
                const marker = L.marker([prop.Latitude, prop.Longitude]).addTo(mapInstanceRef.current);
                marker.bindPopup(`<strong>${prop.Name || 'Unknown'}</strong><br/>${prop.Address || 'N/A'}<br/>Units: ${prop.TotalUnits || 0}`);
            }
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
            await fetch(`${API_BASE}/servicerequests/status/${requestId}`, {
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
                        className={`px-4 py-2 rounded-lg transition-smooth ${filterStatus === status
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
                                    <tr key={request.Id} className="border-t border-gray-700 hover:bg-gray-750">
                                        <td className="p-4 text-blue-400 font-medium">{request.Type}</td>
                                        <td className="p-4">{request.Description}</td>
                                        <td className="p-4">
                                            <span className={`px-3 py-1 rounded-full text-sm ${request.Status === 'Open' ? 'bg-yellow-900 text-yellow-300' :
                                                request.Status === 'Closed' ? 'bg-green-900 text-green-300' :
                                                    'bg-blue-900 text-blue-300'
                                                }`}>
                                                {request.Status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-gray-400">{new Date(request.OpenedAt).toLocaleDateString()}</td>
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
                            <p className="text-lg font-medium">{selectedrequest.Type}</p>
                        </div>
                        <div>
                            <label className="text-gray-400 text-sm">Description</label>
                            <p className="text-lg">{selectedrequest.Description}</p>
                        </div>
                        <div>
                            <label className="text-gray-400 text-sm">Current Status</label>
                            <p className="text-lg font-medium text-blue-400">{selectedrequest.Status}</p>
                        </div>
                        <div>
                            <label className="text-gray-400 text-sm">Opened At</label>
                            <p className="text-lg">{new Date(selectedRequest.OpenedAt).toLocaleString()}</p>
                        </div>
                    </div>
                    <div>
                        <label className="text-gray-400 text-sm mb-2 block">Update Status</label>
                        <div className="flex gap-2 flex-wrap">
                            {statuses.map(status => (
                                <button
                                    key={status}
                                    onClick={() => updateStatus(selectedRequest.Id, status)}
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
    const [utilityData, setUtilityData] = useState(null);
    const [weekOffset, setWeekOffset] = useState(0);
    const [viewMode, setViewMode] = useState('weekly'); // 'weekly' or 'hourly'

    // Initialize from URL on mount
    useEffect(() => {
        loadProperties();
    }, []);

    // Restore state from URL when properties are loaded
    useEffect(() => {
        if (properties.length > 0) {
            const params = new URLSearchParams(window.location.search);
            const urlView = params.get('view');
            const urlPropertyId = params.get('property');
            const urlUnitId = params.get('unit');

            if (urlPropertyId) {
                const property = properties.find(p => p.Id === urlPropertyId);
                if (property) {
                    setSelectedProperty(property);
                    setUnits((property && property.Units) ? property.Units : []);

                    if (urlUnitId && property.Units) {
                        const unit = property.Units.find(u => u.Id === urlUnitId);
                        if (unit) {
                            setSelectedUnit(unit);
                            loadLeases(unit.Id);
                            loadUtilityData(unit.Id, 0, 'weekly');
                            setView('leases');
                            return;
                        }
                    }

                    if (urlView === 'units') {
                        setView('units');
                        return;
                    }
                }
            }

            if (urlView) {
                setView(urlView);
            }
        }
    }, [properties]);

    // Update URL when state changes
    useEffect(() => {
        const params = new URLSearchParams();
        params.set('view', view);

        if (selectedProperty) {
            params.set('property', selectedproperty.Id);
        }

        if (selectedUnit) {
            params.set('unit', selectedunit.Id);
        }

        const newUrl = `${window.location.pathname}?${params.toString()}`;
        window.history.pushState(null, '', newUrl);
    }, [view, selectedProperty, selectedUnit]);

    // Handle browser back/forward buttons
    useEffect(() => {
        const handlePopState = () => {
            const params = new URLSearchParams(window.location.search);
            const urlView = params.get('view') || 'properties';
            const urlPropertyId = params.get('property');
            const urlUnitId = params.get('unit');

            setView(urlView);

            if (urlPropertyId && properties.length > 0) {
                const property = properties.find(p => p.Id === urlPropertyId);
                if (property) {
                    setSelectedProperty(property);
                    setUnits((property && property.Units) ? property.Units : []);

                    if (urlUnitId && property.Units) {
                        const unit = property.Units.find(u => u.Id === urlUnitId);
                        if (unit) {
                            setSelectedUnit(unit);
                            loadLeases(unit.Id);
                            loadUtilityData(unit.Id, 0, 'weekly');
                        } else {
                            setSelectedUnit(null);
                        }
                    } else {
                        setSelectedUnit(null);
                    }
                } else {
                    setSelectedProperty(null);
                    setSelectedUnit(null);
                }
            } else {
                setSelectedProperty(null);
                setSelectedUnit(null);
            }
        };

        window.addEventListener('popstate', handlePopState);
        return () => window.removeEventListener('popstate', handlePopState);
    }, [properties]);

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
            const prop = properties.find(p => p.Id === propertyId);
            setUnits((prop && prop.Units) ? prop.Units : []);
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
        setSelectedUnit(null); // Clear unit when selecting new property
        loadUnits(property.Id);
        setView('units');
    };

    const selectUnit = (unit) => {
        setSelectedUnit(unit);
        loadLeases(unit.Id);
        loadUtilityData(unit.Id, 0, 'weekly');
        setWeekOffset(0);
        setViewMode('weekly');
        setView('leases');
    };

    const loadUtilityData = async (unitId, offset, mode) => {
        try {
            let startDate, endDate;
            const now = new Date();

            if (mode === 'hourly') {
                // Show 48 hours of data
                endDate = new Date(now.getTime() - (offset * 24 * 60 * 60 * 1000));
                startDate = new Date(endDate.getTime() - (48 * 60 * 60 * 1000));
            } else {
                // Show 6 weeks of data
                endDate = new Date(now.getTime() - (offset * 7 * 24 * 60 * 60 * 1000));
                startDate = new Date(endDate.getTime() - (6 * 7 * 24 * 60 * 60 * 1000));
            }

            const response = await fetch(
                `${API_BASE}/utilityusage/unit/${unitId}?from=${startDate.toISOString()}&to=${endDate.toISOString()}`
            );
            const data = await response.json();
            setUtilityData(data);
        } catch (error) {
            console.error('Failed to load utility data:', error);
        }
    };

    const navigateWeek = (direction) => {
        const newOffset = weekOffset + direction;
        setWeekOffset(newOffset);
        if (selectedUnit) {
            loadUtilityData(selectedunit.Id, newOffset, viewMode);
        }
    };

    const toggleViewMode = () => {
        const newMode = viewMode === 'weekly' ? 'hourly' : 'weekly';
        setViewMode(newMode);
        setWeekOffset(0);
        if (selectedUnit) {
            loadUtilityData(selectedunit.Id, 0, newMode);
        }
    };

    return (
        <div>
            <h2 className="text-3xl font-bold mb-8 text-blue-400">Property Management</h2>

            <div className="mb-6 flex gap-4">
                <button
                    onClick={() => setView('properties')}
                    className={`px-4 py-2 rounded-lg transition-smooth ${view === 'properties' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                        }`}
                >
                    Properties
                </button>
                {selectedProperty && (
                    <button
                        onClick={() => setView('units')}
                        className={`px-4 py-2 rounded-lg transition-smooth ${view === 'units' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                            }`}
                    >
                        Units - {selectedproperty.Name}
                    </button>
                )}
                {selectedUnit && (
                    <button
                        onClick={() => setView('leases')}
                        className={`px-4 py-2 rounded-lg transition-smooth ${view === 'leases' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                            }`}
                    >
                        Lease - Unit {selectedUnit.UnitNumber}
                    </button>
                )}
            </div>

            {view === 'properties' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {properties.map(property => (
                        <div
                            key={property.Id}
                            onClick={() => selectProperty(property)}
                            className="bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-700 cursor-pointer transition-smooth hover:border-blue-500 hover:shadow-xl"
                        >
                            <h3 className="text-xl font-bold text-blue-400 mb-2">{property.Name}</h3>
                            <p className="text-gray-300 mb-4">{property.Address}</p>
                            <div className="flex justify-between text-sm text-gray-400">
                                <span>Units: {property.TotalUnits || 0}</span>
                                {property.Latitude != null && property.Longitude != null && (
                                    <span>📍 {Number(property.Latitude).toFixed(2)}, {Number(property.Longitude).toFixed(2)}</span>
                                )}
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
                                <tr key={unit.Id} className="border-t border-gray-700 hover:bg-gray-750">
                                    <td className="p-4 text-blue-400 font-medium">{unit.UnitNumber}</td>
                                    <td className="p-4">
                                        {unit.VacantFrom ? (
                                            <span className="px-3 py-1 rounded-full text-sm bg-red-900 text-red-300">Vacant</span>
                                        ) : (
                                            <span className="px-3 py-1 rounded-full text-sm bg-green-900 text-green-300">Occupied</span>
                                        )}
                                    </td>
                                    <td className="p-4 text-gray-400">
                                        {unit.VacantFrom ? new Date(unit.VacantFrom).toLocaleDateString() : 'N/A'}
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
                            <div key={lease.Id} className="bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-700">
                                <h3 className="text-xl font-bold text-blue-400 mb-4">Active Lease</h3>
                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    <div>
                                        <label className="text-gray-400 text-sm">Lease Amount</label>
                                        <p className="text-2xl font-bold text-green-400">${lease.LeaseAmount?.toFixed(2) || '0.00'}/mo</p>
                                    </div>
                                    <div>
                                        <label className="text-gray-400 text-sm">Status</label>
                                        <p className="text-lg">
                                            {lease.IsActive ? (
                                                <span className="text-green-400">Active</span>
                                            ) : (
                                                <span className="text-red-400">Expired</span>
                                            )}
                                        </p>
                                    </div>
                                    <div>
                                        <label className="text-gray-400 text-sm">Start Date</label>
                                        <p className="text-lg">{new Date(lease.StartDate).toLocaleDateString()}</p>
                                    </div>
                                    <div>
                                        <label className="text-gray-400 text-sm">End Date</label>
                                        <p className="text-lg">{new Date(lease.EndDate).toLocaleDateString()}</p>
                                    </div>
                                    <div>
                                        <label className="text-gray-400 text-sm">Power Rate</label>
                                        <p className="text-lg">${lease.PowerUnitPrice?.toFixed(3) || '0.120'}/kWh</p>
                                    </div>
                                    <div>
                                        <label className="text-gray-400 text-sm">Water Rate</label>
                                        <p className="text-lg">${lease.WaterUnitPrice?.toFixed(3) || '0.005'}/gal</p>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}

                    {utilityData && (
                        <div className="bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-700">
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="text-xl font-bold text-blue-400">
                                    Utility Usage - {viewMode === 'hourly' ? 'Past 48 Hours' : 'Past 6 Weeks'}
                                </h3>
                                <div className="flex gap-2">
                                    <button
                                        onClick={toggleViewMode}
                                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-smooth"
                                    >
                                        {viewMode === 'hourly' ? '📅 Weekly View' : '🔍 Hourly View'}
                                    </button>
                                    <button
                                        onClick={() => navigateWeek(1)}
                                        className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-smooth"
                                    >
                                        ← Previous
                                    </button>
                                    <button
                                        onClick={() => navigateWeek(-1)}
                                        disabled={weekOffset === 0}
                                        className={`px-4 py-2 rounded-lg transition-smooth ${weekOffset === 0
                                            ? 'bg-gray-900 text-gray-600 cursor-not-allowed'
                                            : 'bg-gray-700 hover:bg-gray-600'
                                            }`}
                                    >
                                        Next →
                                    </button>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <h4 className="text-lg font-semibold text-yellow-400 mb-3">⚡ Electricity Usage</h4>
                                    {utilityData.powerUsage && utilityData.powerUsage.length > 0 ? (
                                        <div className="space-y-2">
                                            <div className="bg-gray-900 rounded-lg p-4">
                                                <p className="text-gray-400 text-sm mb-2">Total Usage {viewMode === 'hourly' ? '(48h)' : '(6 weeks)'}</p>
                                                <p className="text-3xl font-bold text-yellow-400">
                                                    {utilityData.powerUsage.reduce((sum, entry) => sum + (entry.value || 0), 0).toFixed(2)} kWh
                                                </p>
                                                {viewMode === 'hourly' && (
                                                    <p className="text-sm text-gray-500 mt-1">
                                                        Avg: {(utilityData.powerUsage.reduce((sum, entry) => sum + (entry.value || 0), 0) / utilityData.powerUsage.length).toFixed(2)} kWh/hr
                                                    </p>
                                                )}
                                            </div>
                                            <div className="bg-gray-900 rounded-lg p-4">
                                                <p className="text-gray-400 text-sm mb-3">Usage Graph</p>
                                                <div className="flex items-end justify-between gap-1" style={{ height: '128px' }}>
                                                    {(() => {
                                                        const validEntries = utilityData.powerUsage.filter(e => e.value != null);
                                                        if (validEntries.length === 0) return <p className="text-gray-500 text-sm">No data</p>;
                                                        const maxValue = Math.max(...validEntries.map(e => e.value));
                                                        const step = viewMode === 'hourly' ? 4 : Math.ceil(validEntries.length / 20);
                                                        return validEntries.filter((_, i) => i % step === 0).map((entry, idx) => {
                                                            const heightPx = Math.max((entry.value / maxValue) * 120, 4);
                                                            return (
                                                                <div key={idx} className="flex-1 group relative">
                                                                    <div
                                                                        className="w-full bg-gradient-to-t from-yellow-600 to-yellow-400 rounded-t transition-all hover:from-yellow-500 hover:to-yellow-300"
                                                                        style={{ height: `${heightPx}px` }}
                                                                    ></div>
                                                                    <div className="absolute -top-8 hidden group-hover:block bg-gray-800 text-xs px-2 py-1 rounded shadow-lg whitespace-nowrap z-10">
                                                                        <div className="text-yellow-400 font-bold">{entry.value.toFixed(2)} kWh</div>
                                                                        <div className="text-gray-400">{new Date(entry.timestamp).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: viewMode === 'hourly' ? 'numeric' : undefined })}</div>
                                                                    </div>
                                                                </div>
                                                            );
                                                        });
                                                    })()}
                                                </div>
                                            </div>
                                            <div className="bg-gray-900 rounded-lg p-4 max-h-64 overflow-y-auto">
                                                <p className="text-gray-400 text-sm mb-2">{viewMode === 'hourly' ? 'Hourly Breakdown' : 'Daily Breakdown'}</p>
                                                <div className="space-y-1">
                                                    {utilityData.powerUsage.filter(e => e.value != null).slice().reverse().map((entry, idx) => (
                                                        <div key={idx} className="flex justify-between text-sm">
                                                            <span className="text-gray-400">
                                                                {viewMode === 'hourly'
                                                                    ? new Date(entry.timestamp).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
                                                                    : new Date(entry.timestamp).toLocaleDateString()
                                                                }
                                                            </span>
                                                            <span className="text-yellow-300 font-medium">{entry.value.toFixed(2)} kWh</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    ) : (
                                        <p className="text-gray-400">No power usage data available</p>
                                    )}
                                </div>

                                <div>
                                    <h4 className="text-lg font-semibold text-blue-400 mb-3">💧 Water Usage</h4>
                                    {utilityData.waterUsage && utilityData.waterUsage.length > 0 ? (
                                        <div className="space-y-2">
                                            <div className="bg-gray-900 rounded-lg p-4">
                                                <p className="text-gray-400 text-sm mb-2">Total Usage {viewMode === 'hourly' ? '(48h)' : '(6 weeks)'}</p>
                                                <p className="text-3xl font-bold text-blue-400">
                                                    {utilityData.waterUsage.reduce((sum, entry) => sum + (entry.value || 0), 0).toFixed(2)} gal
                                                </p>
                                                {viewMode === 'hourly' && (
                                                    <p className="text-sm text-gray-500 mt-1">
                                                        Avg: {(utilityData.waterUsage.reduce((sum, entry) => sum + (entry.value || 0), 0) / utilityData.waterUsage.length).toFixed(2)} gal/hr
                                                    </p>
                                                )}
                                            </div>
                                            <div className="bg-gray-900 rounded-lg p-4">
                                                <p className="text-gray-400 text-sm mb-3">Usage Graph</p>
                                                <div className="flex items-end justify-between gap-1" style={{ height: '128px' }}>
                                                    {(() => {
                                                        const validEntries = utilityData.waterUsage.filter(e => e.value != null);
                                                        if (validEntries.length === 0) return <p className="text-gray-500 text-sm">No data</p>;
                                                        const maxValue = Math.max(...validEntries.map(e => e.value));
                                                        const step = viewMode === 'hourly' ? 4 : Math.ceil(validEntries.length / 20);
                                                        return validEntries.filter((_, i) => i % step === 0).map((entry, idx) => {
                                                            const heightPx = Math.max((entry.value / maxValue) * 120, 4);
                                                            return (
                                                                <div key={idx} className="flex-1 group relative">
                                                                    <div
                                                                        className="w-full bg-gradient-to-t from-blue-600 to-blue-400 rounded-t transition-all hover:from-blue-500 hover:to-blue-300"
                                                                        style={{ height: `${heightPx}px` }}
                                                                    ></div>
                                                                    <div className="absolute -top-8 hidden group-hover:block bg-gray-800 text-xs px-2 py-1 rounded shadow-lg whitespace-nowrap z-10">
                                                                        <div className="text-blue-400 font-bold">{entry.value.toFixed(2)} gal</div>
                                                                        <div className="text-gray-400">{new Date(entry.timestamp).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: viewMode === 'hourly' ? 'numeric' : undefined })}</div>
                                                                    </div>
                                                                </div>
                                                            );
                                                        });
                                                    })()}
                                                </div>
                                            </div>
                                            <div className="bg-gray-900 rounded-lg p-4 max-h-64 overflow-y-auto">
                                                <p className="text-gray-400 text-sm mb-2">{viewMode === 'hourly' ? 'Hourly Breakdown' : 'Daily Breakdown'}</p>
                                                <div className="space-y-1">
                                                    {utilityData.waterUsage.filter(e => e.value != null).slice().reverse().map((entry, idx) => (
                                                        <div key={idx} className="flex justify-between text-sm">
                                                            <span className="text-gray-400">
                                                                {viewMode === 'hourly'
                                                                    ? new Date(entry.timestamp).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
                                                                    : new Date(entry.timestamp).toLocaleDateString()
                                                                }
                                                            </span>
                                                            <span className="text-blue-300 font-medium">{entry.value.toFixed(2)} gal</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    ) : (
                                        <p className="text-gray-400">No water usage data available</p>
                                    )}
                                </div>
                            </div>
                        </div>
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

