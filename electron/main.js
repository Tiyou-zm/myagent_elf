const { app, BrowserWindow, ipcMain, screen } = require("electron");
const path = require("path");

let petWindow = null;
let searchWindow = null;
let petState = "idle";

const PET_STATES = {
  idle: {
    label: "待机",
    description: "绯铃会安静待在桌面角落，等你开口。",
  },
  happy_soft: {
    label: "开心",
    description: "绯铃轻轻回应你，像是在说“我在”。",
  },
  thinking: {
    label: "思考",
    description: "绯铃正在认真想事情，适合检索和判断中的状态。",
  },
  confused: {
    label: "困惑",
    description: "绯铃暂时没完全理解你的意思，等你再说清楚一点。",
  },
  smug: {
    label: "小得意",
    description: "绯铃带一点轻微得意，但还是偏袒你的。",
  },
};

function positionPetWindow(window) {
  const { workArea } = screen.getPrimaryDisplay();
  const [width, height] = window.getSize();
  const x = Math.round(workArea.x + workArea.width - width - 24);
  const y = Math.round(workArea.y + workArea.height - height - 24);
  window.setPosition(x, y);
}

function normalizePetState(nextState) {
  if (nextState && PET_STATES[nextState]) {
    return nextState;
  }

  return "idle";
}

function setPetState(nextState) {
  petState = normalizePetState(nextState);
  syncShellState();
}

function getShellState() {
  return {
    searchVisible: Boolean(searchWindow && searchWindow.isVisible()),
    petState,
    petStateLabel: PET_STATES[petState].label,
    petDescription: PET_STATES[petState].description,
    availableStates: Object.keys(PET_STATES),
  };
}

function syncShellState() {
  if (petWindow && !petWindow.isDestroyed() && !petWindow.webContents.isDestroyed()) {
    petWindow.webContents.send("desktop-shell:state", getShellState());
  }
}

function createPetWindow() {
  petWindow = new BrowserWindow({
    width: 296,
    height: 478,
    minWidth: 296,
    minHeight: 478,
    maxWidth: 296,
    maxHeight: 478,
    frame: false,
    transparent: true,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    maximizable: false,
    minimizable: false,
    fullscreenable: false,
    thickFrame: false,
    title: "Feiling Desktop Pet",
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
    setPetState("happy_soft");
  });
  searchWindow.on("hide", () => {
    setPetState("idle");
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

ipcMain.handle("desktop-shell:set-pet-state", (_event, nextState) => {
  setPetState(nextState);
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
