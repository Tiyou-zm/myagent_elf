const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("desktopShell", {
  showSearchWindow: () => ipcRenderer.invoke("desktop-shell:show-search"),
  hideSearchWindow: () => ipcRenderer.invoke("desktop-shell:hide-search"),
  toggleSearchWindow: () => ipcRenderer.invoke("desktop-shell:toggle-search"),
  quitApp: () => ipcRenderer.invoke("desktop-shell:quit"),
  getShellState: () => ipcRenderer.invoke("desktop-shell:get-state"),
  onShellState: (callback) => {
    ipcRenderer.on("desktop-shell:state", (_event, state) => callback(state));
  },
});
