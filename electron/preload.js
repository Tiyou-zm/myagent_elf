const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("desktopShell", {
  showSearchWindow: () => ipcRenderer.invoke("desktop-shell:show-search"),
  hideSearchWindow: () => ipcRenderer.invoke("desktop-shell:hide-search"),
  quitApp: () => ipcRenderer.invoke("desktop-shell:quit"),
});
