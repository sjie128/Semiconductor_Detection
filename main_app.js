const { app, BrowserWindow } = require('electron');
const path = require('path');
const { fork } = require('child_process');

let mainWindow;
let serverProcess;

function createWindow() {
  // 1. Start the backend server as a hidden background process
  serverProcess = fork(path.join(__dirname, 'server.js'));

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 850,
    title: "Reliability Guard Enterprise",
    autoHideMenuBar: true, // Commercial look
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // Load the UI
  mainWindow.loadURL('http://localhost:3000');

  mainWindow.on('closed', () => {
    if (serverProcess) serverProcess.kill();
    mainWindow = null;
  });
}

app.on('ready', createWindow);