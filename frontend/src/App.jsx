import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.css";
import MainLayout from "./layouts/MainLayout";
import AgentActivity from "./pages/AgentActivity";
import Dashboard from "./pages/Dashboard";
import Inbox from "./pages/Inbox";
import ThreadWorkspace from "./pages/ThreadWorkspace";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <MainLayout>
              <Dashboard />
            </MainLayout>
          }
        />
        <Route
          path="/inbox"
          element={
            <MainLayout>
              <Inbox />
            </MainLayout>
          }
        />
        <Route
          path="/thread/:id"
          element={
            <MainLayout>
              <ThreadWorkspace />
            </MainLayout>
          }
        />
        <Route
          path="/agent"
          element={
            <MainLayout>
              <AgentActivity />
            </MainLayout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
