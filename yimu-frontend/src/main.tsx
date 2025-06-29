// @ts-ignore
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

console.log('main.tsx: Starting application');

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <App />
);
