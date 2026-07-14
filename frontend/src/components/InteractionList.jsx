// InteractionList.jsx
// Shows every logged interaction (from both the form and the agent), newest first.
// Lets you delete a row and inline-edit the sentiment to demonstrate the edit path.

import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { removeInteraction, editInteraction } from "../store/interactionSlice";

export default function InteractionList() {
  const dispatch = useDispatch();
  const items = useSelector((s) => s.interactions.items);

  if (!items.length) {
    return (
      <section className="card list-card">
        <div className="card-head">
          <h2>Logged interactions</h2>
          <span className="card-sub">Nothing logged yet</span>
        </div>
        <p className="empty-note">
          Use the form or chat above to log your first HCP interaction. It will
          appear here.
        </p>
      </section>
    );
  }

  const cycleSentiment = (item) => {
    const order = ["Positive", "Neutral", "Negative"];
    const next = order[(order.indexOf(item.sentiment) + 1) % order.length];
    dispatch(editInteraction({ id: item.id, data: { sentiment: next } }));
  };

  return (
    <section className="card list-card">
      <div className="card-head">
        <h2>Logged interactions</h2>
        <span className="card-sub">{items.length} total</span>
      </div>

      <div className="table">
        {items.map((it) => (
          <div className="row" key={it.id}>
            <div className="row-main">
              <div className="row-top">
                <span className="row-id">#{it.id}</span>
                <span className="row-name">{it.hcp_name}</span>
                <span className="row-type">{it.interaction_type}</span>
                <button
                  className={`sent-tag sent-${(it.sentiment || "neutral").toLowerCase()}`}
                  onClick={() => cycleSentiment(it)}
                  title="Click to change sentiment (edit)"
                >
                  {it.sentiment}
                </button>
              </div>
              {it.ai_summary && <p className="row-summary">{it.ai_summary}</p>}
              {it.topics_discussed && !it.ai_summary && (
                <p className="row-summary">{it.topics_discussed}</p>
              )}
              {it.follow_up_actions?.length > 0 && (
                <div className="row-followups">
                  {it.follow_up_actions.map((f, i) => (
                    <span key={i} className="followup-pill">↳ {f}</span>
                  ))}
                </div>
              )}
            </div>
            <button className="btn-ghost" onClick={() => dispatch(removeInteraction(it.id))}>
              Delete
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
