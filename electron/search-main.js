const { app, BrowserWindow } = require("electron");
const path = require("path");

let searchWindow = null;

function createSearchWindow() {
  searchWindow = new BrowserWindow({
    width: 1320,
    height: 900,
    minWidth: 980,
    minHeight: 720,
    backgroundColor: "#f3efe4",
    autoHideMenuBar: true,
    title: "Agent Study Search Window",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  searchWindow.loadFile(path.join(__dirname, "..", "playground", "index.html"));
  searchWindow.on("closed", () => {
    searchWindow = null;
  });
}

const hasLock = app.requestSingleInstanceLock();
if (!hasLock) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (searchWindow) {
      if (searchWindow.isMinimized()) {
        searchWindow.restore();
      }

      searchWindow.show();
      searchWindow.focus();
    }
  });

  app.whenReady().then(() => {
    createSearchWindow();
    app.on("activate", () => {
      if (!searchWindow) {
        createSearchWindow();
      }
    });
  });

  app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
      app.quit();
    }
  });
}
