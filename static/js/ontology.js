/**
 * AML Analytics — Ontology & Knowledge Graph Explorer Interactive Engine
 * Handles vis.js graph visualization, zoom controls, entity filtering,
 * node search, and deep forensic entity inspection.
 */

let network = null;
let graphNodesDataSet = null;
let graphEdgesDataSet = null;
let currentRawNodes = [];
let currentRawEdges = [];
let allOntologyClasses = [];

document.addEventListener('DOMContentLoaded', function() {
    loadOntologyClasses();
    loadKnowledgeGraph();

    // Event Listeners for Controls
    document.getElementById('btn-reload-graph').addEventListener('click', () => loadKnowledgeGraph());
    document.getElementById('select-graph-limit').addEventListener('change', () => loadKnowledgeGraph());
    document.getElementById('filter-entity-type').addEventListener('change', () => loadKnowledgeGraph());

    document.getElementById('btn-zoom-in').addEventListener('click', zoomIn);
    document.getElementById('btn-zoom-out').addEventListener('click', zoomOut);
    document.getElementById('btn-fit-graph').addEventListener('click', fitGraph);

    // Search node inside knowledge graph
    const searchNodeInput = document.getElementById('graph-search-node');
    searchNodeInput.addEventListener('input', function(e) {
        searchGraphNode(e.target.value);
    });

    // Search ontology classes
    const classSearchInput = document.getElementById('class-search-input');
    classSearchInput.addEventListener('input', function(e) {
        filterOntologyClasses(e.target.value);
    });
});

/**
 * Loads ontology classes from backend and renders structured hierarchy
 */
function loadOntologyClasses() {
    fetch('/api/ontology/classes')
        .then(r => r.json())
        .then(data => {
            allOntologyClasses = data.classes || [];
            document.getElementById('classes-count-badge').innerText = `${allOntologyClasses.length} Classes`;
            renderOntologyClasses(allOntologyClasses);
        })
        .catch(err => {
            console.error('Failed to load ontology classes:', err);
            document.getElementById('ontology-classes-list').innerHTML = `
                <div class="text-danger small p-3 text-center">
                    <i class="fa-solid fa-triangle-exclamation me-1"></i> Failed to load ontology taxonomy.
                </div>
            `;
        });
}

function renderOntologyClasses(classes) {
    const list = document.getElementById('ontology-classes-list');
    list.innerHTML = '';

    if (!classes.length) {
        list.innerHTML = '<div class="text-secondary small text-center py-4">No matching ontology classes found.</div>';
        return;
    }

    classes.forEach(c => {
        const isSubclass = c.parent && c.parent !== 'owl:Thing';
        const iconClass = getIconForClass(c.name);
        const badgeColor = getColorBadgeForClass(c.name);

        const card = document.createElement('div');
        card.className = `ontology-class-card ${isSubclass ? 'ontology-tree-item' : ''}`;
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="fw-bold ${badgeColor} small d-flex align-items-center gap-2">
                    <i class="${iconClass}"></i> ${c.name}
                </span>
                <span class="badge ${isSubclass ? 'bg-secondary' : 'badge-blue'}" style="font-size: 0.65rem;">
                    ${isSubclass ? 'subClassOf ' + c.parent : 'Base Class'}
                </span>
            </div>
            <div class="text-secondary" style="font-size: 0.76rem; line-height: 1.3;">
                ${c.description}
            </div>
        `;
        list.appendChild(card);
    });
}

function filterOntologyClasses(query) {
    if (!query) {
        renderOntologyClasses(allOntologyClasses);
        return;
    }
    const q = query.toLowerCase();
    const filtered = allOntologyClasses.filter(c => 
        c.name.toLowerCase().includes(q) || 
        c.description.toLowerCase().includes(q) ||
        (c.parent && c.parent.toLowerCase().includes(q))
    );
    renderOntologyClasses(filtered);
}

function getIconForClass(name) {
    const map = {
        'Customer': 'fa-solid fa-user',
        'ShellEntity': 'fa-solid fa-building-shield',
        'Account': 'fa-solid fa-building-columns',
        'Transaction': 'fa-solid fa-money-bill-transfer',
        'SuspiciousTransaction': 'fa-solid fa-triangle-exclamation text-danger',
        'NormalTransaction': 'fa-solid fa-circle-check text-success',
        'Alert': 'fa-solid fa-bell text-danger',
        'RiskLevel': 'fa-solid fa-gauge',
        'LowRisk': 'fa-solid fa-shield-heart text-success',
        'MediumRisk': 'fa-solid fa-triangle-exclamation text-warning',
        'HighRisk': 'fa-solid fa-skull-crossbones text-danger',
        'Country': 'fa-solid fa-globe',
        'HighRiskCountry': 'fa-solid fa-plane-slash text-danger',
        'TransactionPattern': 'fa-solid fa-shuffle',
        'SmurfingPattern': 'fa-solid fa-layer-group',
        'LayeringPattern': 'fa-solid fa-network-wired',
        'CircularTransactionPattern': 'fa-solid fa-arrows-spin',
        'RapidTransferPattern': 'fa-solid fa-bolt',
        'CrossBorderPattern': 'fa-solid fa-earth-americas'
    };
    return map[name] || 'fa-solid fa-cube';
}

function getColorBadgeForClass(name) {
    if (name.includes('Suspicious') || name.includes('HighRisk') || name === 'Alert' || name.includes('Shell')) return 'text-danger';
    if (name.includes('Pattern')) return 'text-purple';
    if (name.includes('Risk') || name.includes('Medium')) return 'text-warning';
    if (name === 'Account') return 'text-cyan-accent';
    if (name === 'Customer') return 'text-primary';
    if (name.includes('Normal') || name.includes('Low')) return 'text-success';
    return 'text-light';
}

/**
 * Loads knowledge graph data and initializes Vis.js network
 */
function loadKnowledgeGraph() {
    const limit = document.getElementById('select-graph-limit').value || 60;
    const entityType = document.getElementById('filter-entity-type').value || 'All';

    const overlay = document.getElementById('graph-loading-overlay');
    if (overlay) overlay.classList.remove('d-none');

    let url = `/api/ontology/graph?limit=${limit}`;
    if (entityType && entityType !== 'All') {
        url += `&entity_type=${encodeURIComponent(entityType)}`;
    }

    fetch(url)
        .then(r => r.json())
        .then(graphData => {
            if (overlay) overlay.classList.add('d-none');

            currentRawNodes = graphData.nodes || [];
            currentRawEdges = graphData.edges || [];

            document.getElementById('graph-node-count-badge').innerHTML = `
                <i class="fa-solid fa-circle-nodes text-cyan"></i> ${currentRawNodes.length} Nodes &bull; ${currentRawEdges.length} Edges
            `;

            initVisNetwork(currentRawNodes, currentRawEdges);
        })
        .catch(err => {
            if (overlay) overlay.classList.add('d-none');
            console.error('Failed to load knowledge graph:', err);
        });
}

function initVisNetwork(nodes, edges) {
    const container = document.getElementById('mynetwork');

    // Official suggested colors
    const groupColors = {
        'Customer': { background: '#1677FF', border: '#4096ff', highlight: '#69b1ff' },
        'Account': { background: '#12D5EA', border: '#5cdbd3', highlight: '#87e8de' },
        'Transaction': { background: '#18C98B', border: '#52c41a', highlight: '#95de64' },
        'SuspiciousTransaction': { background: '#FF526A', border: '#ff7875', highlight: '#ffa39e' },
        'Alert': { background: '#FF526A', border: '#ff4d4f', highlight: '#ffa39e' },
        'RiskLevel': { background: '#F5A623', border: '#ffa940', highlight: '#ffd591' },
        'Pattern': { background: '#A78BFA', border: '#b37feb', highlight: '#d3adf7' },
        'Country': { background: '#6366F1', border: '#85a5ff', highlight: '#adc6ff' },
        'HighRiskCountry': { background: '#991B1B', border: '#cf1322', highlight: '#ff4d4f' }
    };

    const formattedNodes = nodes.map(n => {
        const theme = groupColors[n.group] || { background: '#1677FF', border: '#4096ff', highlight: '#69b1ff' };
        return {
            id: n.id,
            label: n.label,
            title: n.title,
            color: {
                background: theme.background,
                border: theme.border,
                highlight: {
                    background: theme.highlight,
                    border: '#FFFFFF'
                }
            },
            font: { color: '#F4F7FF', size: 11, face: 'Plus Jakarta Sans', strokeWidth: 2, strokeColor: '#070D19' },
            shape: n.group === 'Alert' ? 'triangle' : (n.group === 'Pattern' ? 'hexagon' : 'dot'),
            size: n.value || (n.group === 'Customer' ? 22 : 14),
            properties: n.properties || {}
        };
    });

    graphNodesDataSet = new vis.DataSet(formattedNodes);
    graphEdgesDataSet = new vis.DataSet(edges.map(e => ({
        ...e,
        font: { color: '#93A4BD', size: 9, align: 'middle', background: '#070D19', strokeWidth: 0 },
        color: { color: e.color || '#223650', highlight: '#12D5EA' },
        smooth: { type: 'continuous' }
    })));

    const data = {
        nodes: graphNodesDataSet,
        edges: graphEdgesDataSet
    };

    const options = {
        nodes: {
            borderWidth: 2,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.5)', size: 8 }
        },
        edges: {
            arrows: { to: { enabled: true, scaleFactor: 0.7 } },
            width: 1.5,
            selectionWidth: 2.5
        },
        physics: {
            barnesHut: {
                gravitationalConstant: -4000,
                centralGravity: 0.35,
                springLength: 105,
                springConstant: 0.04
            },
            stabilization: { iterations: 120 }
        },
        interaction: {
            hover: true,
            tooltipDelay: 150,
            zoomView: true,
            dragView: true
        }
    };

    network = new vis.Network(container, data, options);

    // Node selection / click listener
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const nodeData = formattedNodes.find(n => n.id === nodeId);
            if (nodeData) {
                renderNodeDetails(nodeData, params.edges);
            }
        }
    });
}

/**
 * Renders rich details inside the Node Details Panel
 */
function renderNodeDetails(node, connectedEdgeIds) {
    const panel = document.getElementById('node-detail-panel');
    const content = document.getElementById('node-detail-content');
    const props = node.properties || {};

    let propsHtml = '';
    for (const [key, val] of Object.entries(props)) {
        if (key === 'entity_id' || key === 'name' || key === 'type') continue;
        const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        propsHtml += `
            <div class="col-sm-6 col-md-4 mb-2">
                <div class="p-2 rounded" style="background: rgba(7, 13, 25, 0.6); border: 1px solid var(--border-color);">
                    <div class="text-muted" style="font-size: 0.68rem; text-transform: uppercase;">${formattedKey}</div>
                    <div class="text-white fw-semibold small text-truncate" title="${val}">${val}</div>
                </div>
            </div>
        `;
    }

    // Find connected nodes
    const connectedEdges = currentRawEdges.filter(e => e.from === node.id || e.to === node.id);
    let connectedNodesHtml = '';
    connectedEdges.slice(0, 8).forEach(edge => {
        const isOutgoing = edge.from === node.id;
        const partnerId = isOutgoing ? edge.to : edge.from;
        const partnerNode = currentRawNodes.find(n => n.id === partnerId);
        const partnerLabel = partnerNode ? partnerNode.label : partnerId;

        connectedNodesHtml += `
            <span class="badge bg-dark border border-secondary text-secondary me-1 mb-1 p-1" style="font-size: 0.72rem; cursor: pointer;" onclick="focusOnNode('${partnerId}')">
                <i class="fa-solid fa-arrow-${isOutgoing ? 'right text-cyan' : 'left text-primary'} me-1"></i>
                <span class="text-white">${edge.label}</span> &rarr; ${partnerLabel}
            </span>
        `;
    });

    content.innerHTML = `
        <div class="row g-3">
            <div class="col-md-7">
                <div class="d-flex align-items-center gap-2 mb-2">
                    <span class="badge badge-blue px-2 py-1">${props.type || node.label}</span>
                    <h5 class="fw-bold text-white mb-0">${props.name || node.label}</h5>
                    <code class="small ms-auto">${props.entity_id || node.id}</code>
                </div>

                <div class="text-secondary small mb-3">
                    <i class="fa-solid fa-code text-cyan me-1"></i> RDF URI: <code>${props.rdf_uri || 'mld:' + node.id}</code>
                </div>

                <div class="row g-2">
                    ${propsHtml || '<div class="text-muted small">No additional data properties.</div>'}
                </div>
            </div>

            <div class="col-md-5 border-start border-secondary ps-md-3">
                <div class="fw-bold text-light small mb-2">
                    <i class="fa-solid fa-circle-nodes text-warning me-1"></i> Connected Triples (${connectedEdges.length})
                </div>
                <div class="d-flex flex-wrap mb-3" style="max-height: 140px; overflow-y: auto;">
                    ${connectedNodesHtml || '<span class="text-muted small">No connected relations.</span>'}
                </div>

                <button class="btn btn-sm btn-glass-cyan w-100" onclick="focusOnNode('${node.id}')">
                    <i class="fa-solid fa-crosshairs me-1"></i> Center & Focus in Graph
                </button>
            </div>
        </div>
    `;
}

function focusOnNode(nodeId) {
    if (!network) return;
    network.focus(nodeId, {
        scale: 1.3,
        animation: { duration: 600, easingFunction: 'easeInOutQuad' }
    });
    network.selectNodes([nodeId]);
}

function searchGraphNode(query) {
    if (!query || !network) return;
    const q = query.toLowerCase().trim();
    const match = currentRawNodes.find(n => 
        n.label.toLowerCase().includes(q) || 
        n.id.toLowerCase().includes(q) ||
        (n.properties && n.properties.entity_id && n.properties.entity_id.toLowerCase().includes(q))
    );

    if (match) {
        focusOnNode(match.id);
        const formattedNode = graphNodesDataSet.get(match.id);
        if (formattedNode) {
            renderNodeDetails(formattedNode, []);
        }
    }
}

function zoomIn() {
    if (!network) return;
    const currentScale = network.getScale();
    network.moveTo({ scale: currentScale * 1.3, animation: true });
}

function zoomOut() {
    if (!network) return;
    const currentScale = network.getScale();
    network.moveTo({ scale: currentScale * 0.7, animation: true });
}

function fitGraph() {
    if (!network) return;
    network.fit({ animation: { duration: 500 } });
}
