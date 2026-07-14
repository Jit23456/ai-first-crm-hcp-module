// App.jsx — the page shell. Loads existing interactions on mount and arranges
// the structured form + AI chat side by side, with the list below.

import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { loadInteractions } from "./store/interactionSlice";
import LogInteractionForm from "./components/LogInteractionForm";
import ChatInterface from "./components/ChatInterface";
import InteractionList from "./components/InteractionList";

export default function App() {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(loadInteractions());
  }, [dispatch]);

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">Rx</div>
          <div>
            <h1>Log HCP Interaction</h1>
            <p>AI-first CRM · Healthcare Professional module</p>
          </div>
        </div>
      </header>

      <main className="layout">
        <div className="col-left">
          <LogInteractionForm />
        </div>
        <div className="col-right">
          <ChatInterface />
        </div>
      </main>

      <div className="list-wrap">
        <InteractionList />
      </div>
    </div>
  );
}
