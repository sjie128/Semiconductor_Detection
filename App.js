const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./factory_reliability.db');

// 1. Initialize Database
function initializeSystem() {
    db.serialize(() => {
        db.run(`CREATE TABLE IF NOT EXISTS production_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            avg_temp REAL,
            max_temp REAL,
            thermal_spread REAL,
            status TEXT,
            reliability_score REAL
        )`);
    });
    console.log("Database Initialized.");
}

// 2. AI/Logic: Detect Concentration (The "Brain")
function analyzePackaging(avg_t, max_t, spread) {
    // We use a Statistical Threshold for "Hot Spot" detection
    // If the spread is > 3 standard deviations from the norm, it's a defect.
    const threshold = 5.0; 
    let status = "OPTIMAL";
    let score = (spread / threshold).toFixed(2);

    if (spread > threshold) {
        status = "DEFECT DETECTED: Localized Heat";
    } else if (avg_t > 250) {
        status = "WARNING: Overheating";
    }

    return { status, score };
}

// Calculate thermal stress
function analyzeReliability(observedSpread) {
    const THEORETICAL_LIMIT = 5.0; // Max safe Delta T in Celsius
    
    // Calculate Error Range: Deviation from safe uniform heat
    let errorRange = (Math.abs(observedSpread - THEORETICAL_LIMIT) / THEORETICAL_LIMIT) * 100;
    
    let diagnosis = "GOOD";
    // If Error is > 10% and heat is concentrated (spread is high)
    if (observedSpread > THEORETICAL_LIMIT && errorRange > 10.0) {
        diagnosis = "BREAK / DEFECT DETECTED";
    }

    return { 
        errorRange: errorRange.toFixed(2), 
        diagnosis: diagnosis 
    };
}

// 3. Log Data to SQL
function logProductionData(avg_t, max_t, spread, status, score) {
    const stmt = db.prepare(`INSERT INTO production_logs 
        (avg_temp, max_temp, thermal_spread, status, reliability_score) 
        VALUES (?, ?, ?, ?, ?)`);
    stmt.run(avg_t, max_t, spread, status, score);
    stmt.finalize();
}

// 4. Export for use in the UI
export default { initializeSystem, analyzePackaging, logProductionData, analyzeReliability };