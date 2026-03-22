const { app, BrowserWindow, ipcMain, screen } = require("electron");
const path = require("path");

let petWindow = null;
let searchWindow = null;

function positionPetWindow(window) {
  const { workArea } = screen.getPrimaryDisplay();
  const [width, height] = window.getSize();
  const x = Math.round(workArea.x + workArea.width - width - 28);
  const y = Math.round(workArea.y + workArea.height - height - 36);
  window.setPosition(x, y);
}

function getShellState() {
  return {
    searchVisible: Boolean(searchWindow && searchWindow.isVisible()),
  };
}

function syncShellState() {
  if (petWindow && !petWindow.isDestroyed() && !petWindow.webContents.isDestroyed()) {
    petWindow.webContents.send("desktop-shell:state", getShellState());
  }
}

function createPetWindow() {
  petWindow = new BrowserWindow({
    width: 228,
    height: 312,
    minWidth: 228,
    minHeight: 312,
    maxWidth: 228,
    maxHeight: 312,
    frame: false,
    transparent: true,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    maximizable: false,
    minimizable: false,
    fullscreenable: false,
    thickFrame: false,
    title: "Agent Study Pet Shell",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  petWindow.loadFile(path.join(__dirname, "pet.html"));
  petWindow.once("ready-to-show", () => {
    positionPetWindow(petWindow);
    petWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
    syncShellState();
  });
  petWindow.on("closed", () => {
    petWindow = null;
  });
}

function createSearchWindow() {
  searchWindow = new BrowserWindow({
    width: 1320,
    height: 900,
    minWidth: 980,
    minHeight: 720,
    backgroundColor: "#f3efe4",
    autoHideMenuBar: true,
    show: false,
    title: "Agent Study Search Window",
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  searchWindow.loadFile(path.join(__dirname, "..", "playground", "index.html"));
  searchWindow.on("show", () => {
    syncShellState();
  });
  searchWindow.on("hide", () => {
    syncShellState();
  });
  searchWindow.on("close", (event) => {
    if (!app.isQuiting) {
      event.preventDefault();
      searchWindow.hide();
    }
  });
  searchWindow.on("closed", () => {
    searchWindow = null;
    syncShellState();
  });
}

function showSearchWindow() {
  if (!searchWindow) {
    createSearchWindow();
  }

  searchWindow.show();
  searchWindow.focus();
}

function hideSearchWindow() {
  if (searchWindow) {
    searchWindow.hide();
  }
}

ipcMain.handle("desktop-shell:show-search", () => {
  showSearchWindow();
});

ipcMain.handle("desktop-shell:hide-search", () => {
  hideSearchWindow();
});

ipcMain.handle("desktop-shell:get-state", () => {
  return getShellState();
});

ipcMain.handle("desktop-shell:toggle-search", () => {
  if (searchWindow && searchWindow.isVisible()) {
    hideSearchWindow();
    return getShellState();
  }

  showSearchWindow();
  return getShellState();
});

ipcMain.handle("desktop-shell:quit", () => {
  app.isQuiting = true;
  app.quit();
});

app.whenReady().then(() => {
  createPetWindow();
  syncShellState();

  app.on("activate", () => {
    if (!petWindow) {
      createPetWindow();
    }
  });
});

app.on("before-quit", () => {
  app.isQuiting = true;
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
