import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import { initializeSystem, analyzePackaging, logProductionData,  analyzeReliability } from './app_engine';

const http = requrie('socket.io');
const app = express();
const server = http.createServer(app);
const io = new Server(server);

initializeSystem();

// Serve a simple dashboard (UI)
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

// Handling data from ESP32-CAM
io.on('connection', (socket) => {
    console.log('Production Line Connected');

    // Simulate Receiving Data from ESP32-CAM Serial/WiFi
    setInterval(() => {
        const avgT = 215 + Math.random() * 5;
        const spread = Math.random() > 0.85 ? 9.5 : 2.5; // Occasional Concentration

        const result = engine.analyzeReliability(spread);
        engine.saveReport(avgT, result.errorRange, result.diagnosis);

        io.emit('update', {
            avgT: avgT.toFixed(2),
            spread: spread.toFixed(2),
            error: result.errorRange,
            status: result.diagnosis,
            // In a real setup, send the Buffer from ESP32-CAM here
            img: "https://via.placeholder.com/400x300?text=Live+Semiconductor+Feed" 
        });
    }, 2000);
});

// Simulation of receiving data from the sensor
setInterval(() => {
    const avg_t = 210 + (Math.random() * 4 - 2);
    const spread = Math.random() > 0.9 ? 8.5 : Math.random() * 3; // Simulate occasional defect
    const max_t = avg_t + spread;

    const result = analyzePackaging(avg_t, max_t, spread);
    
    // Save to Database
    logProductionData(avg_t, max_t, spread, result.status, result.score);

    // Send to UI in real-time
    io.emit('sensor-update', {
        avg_t,
        spread,
        status: result.status,
        score: result.score
    });
}, 2000);

server.listen(3000, () => {
    console.log('Company Dashboard running at http://localhost:3000');
});