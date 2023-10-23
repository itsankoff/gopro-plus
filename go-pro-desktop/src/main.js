const { app, BrowserWindow, globalShortcut } = require('electron');

try {
  require('electron-reloader')(module)
} catch (_) {}

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  globalShortcut.register('f5', function() {
    console.log('f5 is pressed')
    win.reload()
  })
  globalShortcut.register('CommandOrControl+R', function() {
    console.log('CommandOrControl+R is pressed')
    win.reload()
  })

  win.loadFile('src/index.html');
}

app.whenReady().then(createWindow);
