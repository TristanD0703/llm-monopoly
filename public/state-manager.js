export const gameState = {
    players: [],
    properties: {}, // spaceId -> { ownerId, houses }
    history: [],
    usersWatching: 0,
};

const listeners = [];

export function subscribe(callback) {
    listeners.push(callback);
}

function notify() {
    listeners.forEach((cb) => cb(gameState));
}

export function updateGameState(mutator) {
    if (typeof mutator === 'function') {
        mutator(gameState);
        notify();
    }
}
