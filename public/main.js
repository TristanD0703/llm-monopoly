import * as State from './state-manager.js';
import * as UI from './ui-renderer.js';
import { BOARD_DATA } from './board-data.js';

const boardEl = document.getElementById('monopoly-board');
const bankEl = document.getElementById('bank-accounts');
const historyEl = document.getElementById('event-history');
const watcherEl = document.getElementById('watcher-count');
const turnCountEl = document.getElementById('turn-count');
const tooltipEl = document.getElementById('tooltip');
const propertyCardContainer = document.getElementById(
    'property-card-container',
);

const PLAYER_COLORS = [
    '#ff4b2b',
    '#3385ff',
    '#45ffc7',
    '#f9ff45',
    '#ff79c6',
    '#c3ff4d',
    '#ffa149',
    '#a58bff',
];

const PLAYER_ICONS = ['🚀', '🤖', '🕹️', '👾', '🐉', '🧠', '🎲', '⚡'];
const HISTORY_LIMIT = 250;
const OWNABLE_TYPES = new Set(['property', 'railroad', 'utility']);
const PROPERTY_GROUP_SUFFIXES = new Set([
    'brown',
    'light_blue',
    'pink',
    'orange',
    'red',
    'yellow',
    'green',
    'dark_blue',
    'railroad',
    'utility',
]);

const spaceIdsByName = new Map();
const ownableSpaceIdByName = new Map();
buildSpaceLookups();

function init() {
    // One-time board setup
    UI.initBoard(boardEl);

    // Initial Render
    updateUI(State.gameState);

    // Subscribe to state changes
    State.subscribe(updateUI);

    // Setup Board Interactivity
    setupBoardEvents();

    // Live WebSocket integration
    connectToGameServer();
}

function connectToGameServer() {
    if (typeof window.io !== 'function') {
        console.error(
            '[socket] window.io is not available. Did /socket.io/socket.io.js load?',
        );
        State.updateGameState((state) => {
            state.history.push({
                playerName: 'system',
                playerIcon: '⚠️',
                playerColor: '',
                message: 'Socket.IO client failed to load',
                timestamp: new Date().toLocaleTimeString(),
                reason: 'Missing /socket.io/socket.io.js',
            });
        });
        return;
    }

    const socket = window.io('/ws', {
        path: '/socket.io',
        transports: ['websocket', 'polling'],
    });

    socket.onAny((eventName, payload) => {
        console.log(`[socket:${eventName}]`, payload);
    });

    socket.on('connect', () => {
        console.log('[socket] connected');
        State.updateGameState((state) => {
            state.history.push({
                playerName: 'system',
                playerIcon: '🛰️',
                playerColor: '',
                message: 'connected to game server',
                timestamp: new Date().toLocaleTimeString(),
            });
            trimHistory(state);
        });
    });

    socket.on('game_state', (snapshot) => {
        if (!snapshot || typeof snapshot !== 'object') {
            console.warn('[socket] invalid game_state payload', snapshot);
            return;
        }

        hydrateFromGameState(snapshot);
    });

    socket.on('disconnect', (reason) => {
        console.log('[socket] disconnected', reason);
        State.updateGameState((state) => {
            state.usersWatching = 0;
            state.history.push({
                playerName: 'system',
                playerIcon: '🛰️',
                playerColor: '',
                message: 'disconnected from game server',
                timestamp: new Date().toLocaleTimeString(),
                reason,
            });
            trimHistory(state);
        });
    });

    socket.on('spectator_count', (payload) => {
        const count = Number(payload?.count);
        if (!Number.isFinite(count) || count < 0) {
            console.warn('[socket] invalid spectator_count payload', payload);
            return;
        }

        State.updateGameState((state) => {
            state.usersWatching = Math.floor(count);
        });
    });

    socket.on('connect_error', (error) => {
        console.error('[socket] connection error', error);
        State.updateGameState((state) => {
            state.history.push({
                playerName: 'system',
                playerIcon: '⚠️',
                playerColor: '',
                message: 'connection error',
                timestamp: new Date().toLocaleTimeString(),
                reason: error?.message || 'unknown connection error',
            });
            trimHistory(state);
        });
    });

    socket.on('move', (event) => {
        if (!event || typeof event !== 'object') {
            console.warn('[socket] ignored malformed move event', event);
            return;
        }
        handleMoveEvent(event);
    });
}

function updateUI(state) {
    UI.updateBoardOwnership(state.properties, state.players);
    UI.renderPropertyImprovements(state.properties);
    UI.renderMortgagedProperties(state.properties);
    UI.renderPlayers(boardEl, state.players);
    UI.renderBankAccounts(bankEl, state.players);
    UI.renderHistory(historyEl, state.history);
    watcherEl.innerText = state.usersWatching;
    turnCountEl.innerText = state.turnCount;
}

function setupBoardEvents() {
    boardEl.addEventListener('mouseover', (e) => {
        const space = e.target.closest('.space');
        const token = e.target.closest('.player-token');

        if (token) {
            showTooltip(e, `Player: ${token.dataset.name}`);
        } else if (space) {
            const id = space.id.replace('space-', '');
            const property = State.gameState.properties[id];
            if (property) {
                const owner = State.gameState.players.find(
                    (p) => p.id === property.ownerId,
                );
                showTooltip(e, owner ? `Owner: ${owner.name}` : 'Unowned');
            }
        }
    });

    boardEl.addEventListener('mouseout', hideTooltip);

    boardEl.addEventListener('click', (e) => {
        const space = e.target.closest('.space');
        const closeBtn = e.target.closest('#close-card');

        if (closeBtn) {
            propertyCardContainer.innerHTML = '';
            return;
        }

        if (space) {
            const id = parseInt(space.id.replace('space-', ''));
            UI.showPropertyCard(
                propertyCardContainer,
                id,
                State.gameState.properties[id],
            );
        }
    });
}

function showTooltip(e, text) {
    tooltipEl.innerText = text;
    tooltipEl.style.display = 'block';
    tooltipEl.style.left = `${e.pageX + 10}px`;
    tooltipEl.style.top = `${e.pageY + 10}px`;
}

function hideTooltip() {
    tooltipEl.style.display = 'none';
}

function handleMoveEvent(event) {
    State.updateGameState((state) => {
        const names = extractPlayerNames(event);
        if (names.length > 0) {
            syncPlayers(state, names);
        }

        applyGameStateSnapshot(state, event);
        applyActionSpecificStateUpdates(state, event);
        appendEventToHistory(state, event);
        trimHistory(state);
    });
}

function hydrateFromGameState(snapshot) {
    State.updateGameState((state) => {
        const names = extractPlayerNames({ game_state: snapshot });
        if (names.length > 0) {
            syncPlayers(state, names);
        }

        applyGameStateSnapshot(state, { game_state: snapshot });
    });
}

function extractPlayerNames(event) {
    const names = [];
    const moveData =
        event.data && typeof event.data === 'object' ? event.data : {};
    const snapshot =
        event.game_state && typeof event.game_state === 'object'
            ? event.game_state
            : {};

    if (Array.isArray(moveData.players)) {
        names.push(...moveData.players);
    }

    if (snapshot.player_banks && typeof snapshot.player_banks === 'object') {
        names.push(...Object.keys(snapshot.player_banks));
    }

    if (
        snapshot.player_locations &&
        typeof snapshot.player_locations === 'object'
    ) {
        names.push(...Object.keys(snapshot.player_locations));
    }

    if (
        snapshot.properties_owned &&
        typeof snapshot.properties_owned === 'object'
    ) {
        names.push(...Object.keys(snapshot.properties_owned));
    }

    const deduped = new Set();
    names.forEach((name) => {
        if (typeof name === 'string' && name.trim().length > 0) {
            deduped.add(name);
        }
    });

    return [...deduped];
}

function syncPlayers(state, names) {
    if (!Array.isArray(names) || names.length === 0) {
        return;
    }

    const existingPlayers = new Map(state.players.map((p) => [p.name, p]));
    state.players = names.map((name, index) => {
        const existing = existingPlayers.get(name);
        if (existing) {
            return { ...existing, id: index, name };
        }

        return {
            id: index,
            name,
            color: PLAYER_COLORS[index % PLAYER_COLORS.length],
            balance: 1500,
            position: 0,
            icon: PLAYER_ICONS[index % PLAYER_ICONS.length],
        };
    });
}

function ensurePlayer(state, name) {
    if (typeof name !== 'string' || name.trim().length === 0) {
        return null;
    }

    let player = state.players.find((p) => p.name === name);
    if (!player) {
        const index = state.players.length;
        player = {
            id: index,
            name,
            color: PLAYER_COLORS[index % PLAYER_COLORS.length],
            balance: 1500,
            position: 0,
            icon: PLAYER_ICONS[index % PLAYER_ICONS.length],
        };
        state.players.push(player);
    }

    return player;
}

function applyGameStateSnapshot(state, event) {
    const snapshot = event.game_state;
    if (!snapshot || typeof snapshot !== 'object') {
        return;
    }

    const turnCount = Number(snapshot.turn_count);
    if (Number.isFinite(turnCount) && turnCount >= 0) {
        state.turnCount = Math.trunc(turnCount);
    }

    if (snapshot.player_banks && typeof snapshot.player_banks === 'object') {
        Object.entries(snapshot.player_banks).forEach(([playerName, balance]) => {
            const player = ensurePlayer(state, playerName);
            if (player && typeof balance === 'number') {
                player.balance = balance;
            }
        });
    }

    const rollNumber = getRollNumber(event);
    const movedPlayerName =
        typeof event.player_name === 'string' ? event.player_name : '';

    if (
        snapshot.player_locations &&
        typeof snapshot.player_locations === 'object'
    ) {
        Object.entries(snapshot.player_locations).forEach(
            ([playerName, locationName]) => {
                const player = ensurePlayer(state, playerName);
                if (!player) {
                    return;
                }

                const rollHint =
                    playerName === movedPlayerName ? rollNumber : undefined;
                player.position = resolveSpaceId(
                    locationName,
                    player.position,
                    rollHint,
                );
            },
        );
    }

    if (
        snapshot.properties_owned &&
        typeof snapshot.properties_owned === 'object'
    ) {
        const nextProperties = {};
        Object.entries(snapshot.properties_owned).forEach(
            ([playerName, ownedList]) => {
                const player = ensurePlayer(state, playerName);
                if (!player || !Array.isArray(ownedList)) {
                    return;
                }

                ownedList.forEach((propertyName) => {
                    const spaceId = resolveOwnableSpaceId(propertyName);
                    if (spaceId === null) {
                        return;
                    }

                    nextProperties[spaceId] = {
                        ownerId: player.id,
                        houses: 0,
                        mortgaged: false,
                    };
                });
            },
        );

        if (
            snapshot.property_state &&
            typeof snapshot.property_state === 'object'
        ) {
            Object.entries(snapshot.property_state).forEach(
                ([propertyName, propertyState]) => {
                    const spaceId = resolveOwnableSpaceId(propertyName);
                    if (
                        spaceId === null ||
                        !propertyState ||
                        typeof propertyState !== 'object' ||
                        !nextProperties[spaceId]
                    ) {
                        return;
                    }

                    const houses = Number(propertyState.houses);
                    nextProperties[spaceId].houses = Number.isFinite(houses)
                        ? Math.max(0, Math.trunc(houses))
                        : 0;
                    nextProperties[spaceId].mortgaged =
                        propertyState.mortgaged === true;
                },
            );
        }

        state.properties = nextProperties;
    }
}

function applyActionSpecificStateUpdates(state, event) {
    const actionName =
        typeof event.action_name === 'string' ? event.action_name : '';
    const moveData =
        event.data && typeof event.data === 'object' ? event.data : {};

    if (actionName !== 'buy_houses' && actionName !== 'sell_houses') {
        return;
    }

    const propertyName = moveData.property_name;
    const count = Number(moveData.count);
    if (
        typeof propertyName !== 'string' ||
        propertyName.trim().length === 0 ||
        !Number.isFinite(count)
    ) {
        return;
    }

    const spaceId = resolveOwnableSpaceId(propertyName);
    if (spaceId === null) {
        return;
    }

    if (!state.properties[spaceId]) {
        const actor = ensurePlayer(state, event.player_name);
        state.properties[spaceId] = {
            ownerId: actor ? actor.id : -1,
            houses: 0,
            mortgaged: false,
        };
    }

    const currentHouses = state.properties[spaceId].houses || 0;
    const quantity = Math.abs(Math.trunc(count));
    const delta = actionName === 'buy_houses' ? quantity : -quantity;

    state.properties[spaceId].houses = Math.max(0, currentHouses + delta);
}

function appendEventToHistory(state, event) {
    const actorName =
        typeof event.player_name === 'string' ? event.player_name : 'system';
    const actorIsSystem = actorName.toLowerCase() === 'system';
    const actor = actorIsSystem ? null : ensurePlayer(state, actorName);

    state.history.push({
        playerName: actorName,
        playerIcon: actor ? actor.icon : '🛰️',
        playerColor: actor ? actor.color : '',
        message: buildEventMessage(event),
        timestamp: new Date().toLocaleTimeString(),
        reason: extractReason(event),
    });
}

function buildEventMessage(event) {
    const action = humanizeLabel(event.action_name || 'move');
    const moveData =
        event.data && typeof event.data === 'object' ? event.data : {};

    const summaryEntries = Object.entries(moveData);
    if (summaryEntries.length === 0) {
        return action;
    }

    const summary = summaryEntries
        .slice(0, 4)
        .map(([key, value]) => {
            return `${humanizeLabel(key)}=${formatValue(value)}`;
        })
        .join(', ');

    return `${action}: ${summary}`;
}

function extractReason(event) {
    const moveData =
        event.data && typeof event.data === 'object' ? event.data : {};
    const reasonCandidates = [
        event.reason,
        moveData.reason,
        event.explanation,
        moveData.explanation,
    ];

    for (const candidate of reasonCandidates) {
        if (typeof candidate === 'string' && candidate.trim().length > 0) {
            return candidate;
        }
    }

    return '';
}

function trimHistory(state) {
    if (state.history.length > HISTORY_LIMIT) {
        state.history.splice(0, state.history.length - HISTORY_LIMIT);
    }
}

function buildSpaceLookups() {
    BOARD_DATA.forEach((space) => {
        const normalized = normalizeLabel(space.name);
        pushLookup(spaceIdsByName, normalized, space.id);
        if (OWNABLE_TYPES.has(space.type) && !ownableSpaceIdByName.has(normalized)) {
            ownableSpaceIdByName.set(normalized, space.id);
        }
    });

    // Server game_state uses "Jail" for index 10.
    pushLookup(spaceIdsByName, normalizeLabel('jail'), 10);
}

function pushLookup(map, key, value) {
    if (!map.has(key)) {
        map.set(key, []);
    }

    const existing = map.get(key);
    if (!existing.includes(value)) {
        existing.push(value);
    }
}

function normalizeLabel(value) {
    return String(value || '')
        .toLowerCase()
        .replace(/&/g, ' and ')
        .replace(/[^a-z0-9]+/g, ' ')
        .trim();
}

function normalizePropertyName(value) {
    const raw = String(value || '');
    const parts = raw.split(' - ');
    if (parts.length > 1) {
        const suffix = normalizeLabel(parts[parts.length - 1]).replace(
            /\s+/g,
            '_',
        );
        if (PROPERTY_GROUP_SUFFIXES.has(suffix)) {
            return parts.slice(0, -1).join(' - ');
        }
    }
    return raw;
}

function resolveOwnableSpaceId(spaceName) {
    const normalized = normalizeLabel(normalizePropertyName(spaceName));
    if (ownableSpaceIdByName.has(normalized)) {
        return ownableSpaceIdByName.get(normalized);
    }

    const candidates = spaceIdsByName.get(normalized);
    if (!candidates || candidates.length === 0) {
        return null;
    }

    return candidates[0];
}

function resolveSpaceId(spaceName, previousPosition, rollNumber) {
    const normalized = normalizeLabel(normalizePropertyName(spaceName));
    const candidates = spaceIdsByName.get(normalized);
    if (!candidates || candidates.length === 0) {
        return typeof previousPosition === 'number' ? previousPosition : 0;
    }

    if (candidates.length === 1) {
        return candidates[0];
    }

    if (typeof previousPosition !== 'number') {
        return candidates[0];
    }

    if (typeof rollNumber === 'number') {
        const expected =
            (previousPosition + rollNumber + BOARD_DATA.length) %
            BOARD_DATA.length;
        if (candidates.includes(expected)) {
            return expected;
        }
    }

    if (candidates.includes(previousPosition)) {
        return previousPosition;
    }

    let bestId = candidates[0];
    let bestDistance = Number.POSITIVE_INFINITY;
    candidates.forEach((candidateId) => {
        const distance =
            (candidateId - previousPosition + BOARD_DATA.length) %
            BOARD_DATA.length;
        if (distance < bestDistance) {
            bestDistance = distance;
            bestId = candidateId;
        }
    });
    return bestId;
}

function getRollNumber(event) {
    if (event.action_name !== 'dice_roll') {
        return undefined;
    }

    const moveData =
        event.data && typeof event.data === 'object' ? event.data : {};
    const rollNumber = Number(moveData.roll_number);
    return Number.isFinite(rollNumber) ? rollNumber : undefined;
}

function humanizeLabel(value) {
    return String(value || '')
        .replace(/_/g, ' ')
        .trim();
}

function formatValue(value) {
    let text;
    if (Array.isArray(value)) {
        text = value.join(', ');
    } else if (value && typeof value === 'object') {
        text = JSON.stringify(value);
    } else {
        text = String(value);
    }

    return text.length > 120 ? `${text.slice(0, 117)}...` : text;
}

init();
