import { BOARD_DATA } from './board-data.js';

export function initBoard(container) {
    container.querySelectorAll('.space').forEach(s => s.remove());
    
    BOARD_DATA.forEach(space => {
        const spaceEl = document.createElement('div');
        spaceEl.className = `space ${getSide(space.id)} ${space.group}`;
        spaceEl.id = `space-${space.id}`;
        spaceEl.style.gridArea = getGridArea(space.id);
        
        if (space.type === 'property') {
            const colorBar = document.createElement('div');
            colorBar.className = `space-color-bar ${space.group}`;
            spaceEl.appendChild(colorBar);
        }

        const contentEl = document.createElement('div');
        contentEl.className = 'space-content';

        const nameEl = document.createElement('div');
        nameEl.className = 'space-name';
        nameEl.innerText = space.name;
        contentEl.appendChild(nameEl);

        const iconHtml = getIconForSpace(space);
        if (iconHtml) {
            const iconWrapper = document.createElement('div');
            iconWrapper.innerHTML = iconHtml;
            contentEl.appendChild(iconWrapper.firstChild);
        }

        spaceEl.appendChild(contentEl);

        container.appendChild(spaceEl);
    });
}

function getIconForSpace(space) {
    const iconById = {
        0: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="12" cy="12" r="10" fill="#1fb25a"/>
                <path d="M6 12h9l-2.8-2.8 1.4-1.4L19 13l-5.4 5.2-1.4-1.4L15 14H6z" fill="#fff"/>
            </svg>`,
        2: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="3" y="7" width="18" height="12" rx="2" fill="#0072bb"/>
                <rect x="6" y="5" width="12" height="4" rx="1.2" fill="#3aa4e8"/>
                <rect x="10" y="11" width="4" height="6" rx="0.8" fill="#e6f5ff"/>
                <text x="18.2" y="18.2" font-size="5" font-weight="700" fill="#fff" text-anchor="middle" font-family="Montserrat">1</text>
            </svg>`,
        4: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="5" y="3" width="14" height="18" rx="1.5" fill="#2f2f35"/>
                <path d="M8 8h8M8 11h8M8 14h5" stroke="#d0d0d0" stroke-width="1.3" stroke-linecap="round"/>
                <circle cx="15.5" cy="17" r="2.2" fill="#fef200"/>
                <text x="15.5" y="18.1" font-size="3" font-weight="700" fill="#000" text-anchor="middle" font-family="Montserrat">$</text>
            </svg>`,
        5: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="4" y="6" width="16" height="9" rx="2" fill="#333"/>
                <rect x="6" y="8" width="6" height="3" fill="#f6f6f6"/>
                <circle cx="8" cy="17.5" r="1.8" fill="#111"/><circle cx="16" cy="17.5" r="1.8" fill="#111"/>
                <text x="12" y="14.2" font-size="4.5" font-weight="700" fill="#fff" text-anchor="middle" font-family="Montserrat">R</text>
            </svg>`,
        7: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="4" y="5" width="16" height="14" rx="2" fill="#f7941d"/>
                <path d="M8 8h8v2H8zM8 12h5v2H8z" fill="#fff" opacity="0.9"/>
                <text x="16.8" y="17.8" font-size="6" font-weight="700" fill="#fff" text-anchor="middle" font-family="Montserrat">?</text>
                <text x="6.8" y="17.8" font-size="4.2" font-weight="700" fill="#fff" text-anchor="middle" font-family="Montserrat">1</text>
            </svg>`,
        10: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="3" y="4" width="18" height="16" rx="1.5" fill="#202028"/>
                <path d="M7 4v16M11 4v16M15 4v16M19 4v16" stroke="#8e9299" stroke-width="1.2"/>
                <text x="12" y="13.8" font-size="5.5" font-weight="700" fill="#fef200" text-anchor="middle" font-family="Montserrat">JV</text>
            </svg>`,
        12: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M424.5 355.1C449 329.2 464 294.4 464 256C464 176.5 399.5 112 320 112C240.5 112 176 176.5 176 256C176 294.4 191 329.2 215.5 355.1C236.8 377.5 260.4 409.1 268.8 448L371.2 448C379.6 409 403.2 377.5 424.5 355.1zM459.3 388.1C435.7 413 416 443.4 416 477.7L416 496C416 540.2 380.2 576 336 576L304 576C259.8 576 224 540.2 224 496L224 477.7C224 443.4 204.3 413 180.7 388.1C148 353.7 128 307.2 128 256C128 150 214 64 320 64C426 64 512 150 512 256C512 307.2 492 353.7 459.3 388.1zM272 248C272 261.3 261.3 272 248 272C234.7 272 224 261.3 224 248C224 199.4 263.4 160 312 160C325.3 160 336 170.7 336 184C336 197.3 325.3 208 312 208C289.9 208 272 225.9 272 248z"/></svg>`,
        15: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="4" y="6" width="16" height="9" rx="2" fill="#333"/>
                <rect x="6" y="8" width="6" height="3" fill="#f6f6f6"/>
                <circle cx="8" cy="17.5" r="1.8" fill="#111"/><circle cx="16" cy="17.5" r="1.8" fill="#111"/>
                <text x="12" y="14.2" font-size="4.5" font-weight="700" fill="#fff" text-anchor="middle" font-family="Montserrat">P</text>
            </svg>`,
        17: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="3" y="7" width="18" height="12" rx="2" fill="#0072bb"/>
                <rect x="6" y="5" width="12" height="4" rx="1.2" fill="#3aa4e8"/>
                <rect x="10" y="11" width="4" height="6" rx="0.8" fill="#e6f5ff"/>
                <text x="18.2" y="18.2" font-size="5" font-weight="700" fill="#fff" text-anchor="middle" font-family="Montserrat">2</text>
            </svg>`,
        20: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="12" cy="12" r="9" fill="#ed1b24"/>
                <circle cx="12" cy="12" r="4.2" fill="none" stroke="#fff" stroke-width="1.5"/>
                <path d="M12 3v5M12 16v5M3 12h5M16 12h5M5.6 5.6l3.4 3.4M15 15l3.4 3.4M18.4 5.6 15 9M9 15l-3.4 3.4" stroke="#fff" stroke-width="1.2" stroke-linecap="round"/>
            </svg>`,
        22: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="4" y="5" width="16" height="14" rx="2" fill="#f7941d"/>
                <path d="M8 8h8v2H8zM8 12h5v2H8z" fill="#fff" opacity="0.9"/>
                <text x="16.8" y="17.8" font-size="6" font-weight="700" fill="#fff" text-anchor="middle" font-family="Montserrat">?</text>
                <text x="6.8" y="17.8" font-size="4.2" font-weight="700" fill="#fff" text-anchor="middle" font-family="Montserrat">2</text>
            </svg>`,
        25: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="4" y="6" width="16" height="9" rx="2" fill="#333"/>
                <rect x="6" y="8" width="6" height="3" fill="#f6f6f6"/>
                <circle cx="8" cy="17.5" r="1.8" fill="#111"/><circle cx="16" cy="17.5" r="1.8" fill="#111"/>
                <text x="12" y="14.2" font-size="4.5" font-weight="700" fill="#fff" text-anchor="middle" font-family="Montserrat">B</text>
            </svg>`,
        28: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M5 8h8a3 3 0 0 1 3 3v1h3v2h-3v1h-2v-4a1 1 0 0 0-1-1H5z" fill="#0072bb"/>
                <path d="M8 5h2v3H8z" fill="#8fd0ff"/>
                <path d="M17 16c0 1.7-1.2 3-2.8 3S11.5 17.7 11.5 16c0-1.4 2.7-4.4 2.7-4.4S17 14.6 17 16z" fill="#3aa4e8"/>
            </svg>`,
        30: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Pro v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2026 Fonticons, Inc.--><path d="M128 64C92.7 64 64 92.7 64 128L64 512C64 547.3 92.7 576 128 576L329.2 576C316.7 561.3 306 545.2 297.4 528L207.9 528L207.9 448C207.9 430.3 222.2 416 239.9 416L271.9 416L271.9 389.3C271.9 371.2 278 354.1 288.5 340.5C288.1 339.1 287.9 337.6 287.9 336L287.9 304C287.9 295.2 295.1 288 303.9 288L335.9 288C344.7 288 351.9 295.2 351.9 304L351.9 305L438.6 276.1C441.7 275.1 444.8 274.3 447.9 273.6L448 128C448 92.7 419.3 64 384 64L128 64zM160 176C160 167.2 167.2 160 176 160L208 160C216.8 160 224 167.2 224 176L224 208C224 216.8 216.8 224 208 224L176 224C167.2 224 160 216.8 160 208L160 176zM304 160L336 160C344.8 160 352 167.2 352 176L352 208C352 216.8 344.8 224 336 224L304 224C295.2 224 288 216.8 288 208L288 176C288 167.2 295.2 160 304 160zM160 304C160 295.2 167.2 288 176 288L208 288C216.8 288 224 295.2 224 304L224 336C224 344.8 216.8 352 208 352L176 352C167.2 352 160 344.8 160 336L160 304zM477.3 552.5L464 558.8L464 370.7L560 402.7L560 422.3C560 478.1 527.8 528.8 477.3 552.6zM453.9 323.5L341.9 360.8C328.8 365.2 320 377.4 320 391.2L320 422.3C320 496.7 363 564.4 430.2 596L448.7 604.7C453.5 606.9 458.7 608.1 463.9 608.1C469.1 608.1 474.4 606.9 479.1 604.7L497.6 596C565 564.3 608 496.6 608 422.2L608 391.1C608 377.3 599.2 365.1 586.1 360.7L474.1 323.4C467.5 321.2 460.4 321.2 453.9 323.4z"/></svg>`,
        33: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="3" y="7" width="18" height="12" rx="2" fill="#0072bb"/>
                <rect x="6" y="5" width="12" height="4" rx="1.2" fill="#3aa4e8"/>
                <rect x="10" y="11" width="4" height="6" rx="0.8" fill="#e6f5ff"/>
                <text x="18.2" y="18.2" font-size="5" font-weight="700" fill="#fff" text-anchor="middle" font-family="Montserrat">3</text>
            </svg>`,
        35: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="4" y="6" width="16" height="9" rx="2" fill="#333"/>
                <rect x="6" y="8" width="6" height="3" fill="#f6f6f6"/>
                <circle cx="8" cy="17.5" r="1.8" fill="#111"/><circle cx="16" cy="17.5" r="1.8" fill="#111"/>
                <text x="12" y="14.2" font-size="4.5" font-weight="700" fill="#fff" text-anchor="middle" font-family="Montserrat">S</text>
            </svg>`,
        36: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="4" y="5" width="16" height="14" rx="2" fill="#f7941d"/>
                <path d="M8 8h8v2H8zM8 12h5v2H8z" fill="#fff" opacity="0.9"/>
                <text x="16.8" y="17.8" font-size="6" font-weight="700" fill="#fff" text-anchor="middle" font-family="Montserrat">?</text>
                <text x="6.8" y="17.8" font-size="4.2" font-weight="700" fill="#fff" text-anchor="middle" font-family="Montserrat">3</text>
            </svg>`,
        38: `<svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 3 4 11l8 10 8-10z" fill="#111"/>
                <path d="M12 6 7 11l5 6 5-6z" fill="#fef200"/>
                <text x="12" y="13.4" font-size="5.8" font-weight="700" fill="#111" text-anchor="middle" font-family="Montserrat">$</text>
            </svg>`,
    };

    const svg = iconById[space.id] || '';

    if (svg) {
        return `<div class="space-icon">${svg}</div>`;
    }
    return '';
}

export function updateBoardOwnership(properties, players) {
    // Reset glows
    document.querySelectorAll('.space').forEach(spaceEl => {
        spaceEl.classList.remove('owner-glow');
        spaceEl.style.color = '';
    });

    Object.entries(properties).forEach(([spaceId, data]) => {
        const spaceEl = document.getElementById(`space-${spaceId}`);
        const owner = players.find(p => p.id === data.ownerId);
        if (spaceEl && owner) {
            spaceEl.style.color = owner.color;
            spaceEl.classList.add('owner-glow');
        }
    });
}

function getSide(id) {
    if (id >= 0 && id <= 10) return 'bottom';
    if (id > 10 && id < 20) return 'left';
    if (id >= 20 && id <= 30) return 'top';
    return 'right';
}

function getGridArea(id) {
    // CSS Grid is 1-indexed
    // 11x11 grid
    if (id >= 0 && id <= 10) return `11 / ${11 - id}`; // Bottom
    if (id > 10 && id < 20) return `${11 - (id - 10)} / 1`; // Left
    if (id >= 20 && id <= 30) return `1 / ${id - 19}`; // Top
    if (id > 30 && id < 40) return `${id - 29} / 11`; // Right
}

export function renderPlayers(board, players) {
    // Remove existing tokens
    document.querySelectorAll('.player-token').forEach(t => t.remove());
    
    players.forEach(player => {
        const space = document.getElementById(`space-${player.position}`);
        if (space) {
            const token = document.createElement('div');
            token.className = 'player-token';
            token.innerText = player.icon;
            token.style.backgroundColor = player.color;
            token.dataset.name = player.name;
            
            // Offset tokens if multiple on same space
            const offset = players.filter(p => p.position === player.position).indexOf(player);
            token.style.transform = `translate(${offset * 5}px, ${offset * 5}px)`;
            
            space.appendChild(token);
        }
    });
}

export function renderBankAccounts(container, players) {
    container.innerHTML = '';
    players.forEach(player => {
        const div = document.createElement('div');
        div.className = 'bank-item';
        div.innerHTML = `<span>${player.icon}</span> <span>$${player.balance}</span>`;
        div.style.borderBottom = `2px solid ${player.color}`;
        container.appendChild(div);
    });
}

export function renderHistory(container, history) {
    container.innerHTML = '';
    [...history].reverse().forEach(item => {
        const div = document.createElement('div');
        div.className = 'history-item';
        div.style.borderLeftColor = `var(--accent-color)`; // Simplified

        const header = document.createElement('div');
        header.className = 'header';

        const playerSpan = document.createElement('span');
        playerSpan.textContent = `${item.playerIcon || ''} ${item.playerName || 'unknown'}`.trim();

        const timeSpan = document.createElement('span');
        timeSpan.textContent = item.timestamp || '';

        header.appendChild(playerSpan);
        header.appendChild(timeSpan);

        const message = document.createElement('div');
        message.textContent = item.message || '';

        div.appendChild(header);
        div.appendChild(message);

        if (item.reason) {
            const reason = document.createElement('div');
            reason.textContent = `Reason: ${item.reason}`;
            reason.style.marginTop = '6px';
            reason.style.opacity = '0.75';
            div.appendChild(reason);
        }

        container.appendChild(div);
    });
}

export function showPropertyCard(container, spaceId, propertyState) {
    const space = BOARD_DATA.find(s => s.id === spaceId);
    if (!space || (space.type !== 'property' && space.type !== 'railroad' && space.type !== 'utility')) {
        container.innerHTML = '';
        return;
    }

    const houses = propertyState ? propertyState.houses : 0;

    if (space.type === 'railroad') {
        container.innerHTML = `
            <div class="property-card">
                <button id="close-card" class="close-card">&times;</button>
                <div class="card-header railroad" style="background-color: transparent; border: none; padding-bottom: 0; color: black;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🚂</div>
                    <h3 style="font-size: 1.2rem;">${space.name}</h3>
                </div>
                <hr style="border-top: 2px solid black; margin: 10px 0;">
                <div class="rent-line">
                    <span>Rent</span> <span>$${space.rent[0]}</span>
                </div>
                <div class="rent-line">
                    <span>If 2 Railroads are owned</span> <span>$${space.rent[1]}</span>
                </div>
                <div class="rent-line">
                    <span>If 3 Railroads are owned</span> <span>$${space.rent[2]}</span>
                </div>
                <div class="rent-line">
                    <span>If 4 Railroads are owned</span> <span>$${space.rent[3]}</span>
                </div>
                <hr style="border-top: 1px solid black; margin: 10px 0;">
                <div style="text-align:center; font-size: 0.8rem; margin-top: 10px;">
                    Mortgage Value $100
                </div>
            </div>
        `;
    } else if (space.type === 'utility') {
         container.innerHTML = `
            <div class="property-card">
                <button id="close-card" class="close-card">&times;</button>
                <div class="card-header utility" style="background-color: transparent; border: none; padding-bottom: 0; color: black;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">${space.id === 12 ? '💡' : '🚰'}</div>
                    <h3 style="font-size: 1.2rem;">${space.name}</h3>
                </div>
                <hr style="border-top: 2px solid black; margin: 10px 0;">
                <div style="font-size: 0.8rem; text-align: center; margin-bottom: 15px; font-family: Montserrat, sans-serif;">
                    If one "Utility" is owned rent is 4 times amount shown on dice.
                </div>
                <div style="font-size: 0.8rem; text-align: center; margin-bottom: 15px; font-family: Montserrat, sans-serif;">
                    If both "Utilities" are owned rent is 10 times amount shown on dice.
                </div>
                <hr style="border-top: 1px solid black; margin: 10px 0;">
                <div style="text-align:center; font-size: 0.8rem; margin-top: 10px;">
                    Mortgage Value $75
                </div>
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="property-card">
                <button id="close-card" class="close-card">&times;</button>
                <div class="card-header ${space.group}">
                    <small>Title Deed</small>
                    <h3>${space.name}</h3>
                </div>
                <div class="rent-line ${houses === 0 ? 'active' : ''}">
                    <span>Rent</span> <span>$${space.rent[0]}</span>
                </div>
                <div class="rent-line ${houses === 1 ? 'active' : ''}">
                    <span>With 1 House</span> <span>$${space.rent[1]}</span>
                </div>
                <div class="rent-line ${houses === 2 ? 'active' : ''}">
                    <span>With 2 Houses</span> <span>$${space.rent[2]}</span>
                </div>
                <div class="rent-line ${houses === 3 ? 'active' : ''}">
                    <span>With 3 Houses</span> <span>$${space.rent[3]}</span>
                </div>
                <div class="rent-line ${houses === 4 ? 'active' : ''}">
                    <span>With 4 Houses</span> <span>$${space.rent[4]}</span>
                </div>
                <div class="rent-line ${houses === 5 ? 'active' : ''}">
                    <span>With HOTEL</span> <span>$${space.rent[5]}</span>
                </div>
                <hr>
                <div style="text-align:center; font-size: 0.7rem; margin-top: 10px;">
                    House Cost $${space.housePrice} each
                </div>
            </div>
        `;
    }
}
