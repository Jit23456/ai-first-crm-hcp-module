// ChatInterface.jsx
// The CONVERSATIONAL way to log an interaction (right panel). Sends the typed
// message to the LangGraph agent via the Redux chat thunk and shows the reply.
// When the agent uses a tool, we display a small badge so the demo is obvious.

import React, { useState, useRef, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { chat, pushUserMessage } from "../store/interactionSlice";

export default function ChatInterface() {
  const dispatch = useDispatch();
  const messages = useSelector((s) => s.interactions.messages);
  const chatStatus = useSelector((s) => s.interactions.chatStatus);
  const [text, setText] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [messages, chatStatus]);

  const send = () => {
    const msg = text.trim();
    if (!msg) return;
    dispatch(pushUserMessage(msg));
    dispatch(chat(msg));
    setText("");
  };

  const onKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <section className="card chat-card">
      <div className="card-head chat-head">
        <div className="ai-dot" />
        <div>
          <h2>AI assistant</h2>
          <span className="card-sub">Log interaction via chat</span>
        </div>
      </div>

      <div className="chat-log" ref={scrollRef}>
        {messages.map((m, i) => (
          <div key={i} className={`bubble bubble-${m.role}`}>
            {m.tool && <span className="tool-badge">tool: {m.tool}</span>}
            <p>{m.text}</p>
          </div>
        ))}
        {chatStatus === "loading" && (
          <div className="bubble bubble-assistant">
            <p className="typing">Thinking…</p>
          </div>
        )}
      </div>

      <div className="chat-input-row">
        <input
          className="input"
          placeholder="Describe interaction…"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKey}
        />
        <button className="btn btn-primary" onClick={send} disabled={chatStatus === "loading"}>
          Log
        </button>
      </div>
    </section>
  );
}
