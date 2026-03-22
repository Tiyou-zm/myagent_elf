const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");

let petWindow = null;
let searchWindow = null;

function createPetWindow() {
  petWindow = new BrowserWindow({
    width: 240,
    height: 280,
    minWidth: 220,
    minHeight: 260,
    maxWidth: 300,
    maxHeight: 340,
    frame: false,
    transparent: true,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: false,
    title: "Agent Study Pet Shell",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  petWindow.loadFile(path.join(__dirname, "pet.html"));
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
  searchWindow.on("close", (event) => {
    if (!app.isQuiting) {
      event.preventDefault();
      searchWindow.hide();
    }
  });
  searchWindow.on("closed", () => {
    searchWindow = null;
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

ipcMain.handle("desktop-shell:quit", () => {
  app.isQuiting = true;
  app.quit();
});

app.whenReady().then(() => {
  createPetWindow();
  createSearchWindow();

  app.on("activate", () => {
    if (!petWindow) {
      createPetWindow();
    }
    if (!searchWindow) {
      createSearchWindow();
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
