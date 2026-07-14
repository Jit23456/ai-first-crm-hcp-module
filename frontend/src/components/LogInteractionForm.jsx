// LogInteractionForm.jsx
// The STRUCTURED way to log an interaction (left panel). Mirrors the fields in
// the assignment's mockup. On submit it dispatches the Redux addInteraction thunk.

import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { addInteraction } from "../store/interactionSlice";

const EMPTY = {
  hcp_name: "",
  interaction_type: "Meeting",
  date: "",
  time: "",
  attendees: "",
  topics_discussed: "",
  materials_shared: "",
  samples_distributed: "",
  sentiment: "Neutral",
  outcomes: "",
  follow_up_actions: "",
};

// Turn "a, b, c" into ["a","b","c"], ignoring blanks.
const toList = (s) =>
  s
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);

export default function LogInteractionForm() {
  const dispatch = useDispatch();
  const status = useSelector((s) => s.interactions.status);
  const [form, setForm] = useState(EMPTY);
  const [saved, setSaved] = useState(false);

  const update = (field) => (e) =>
    setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async () => {
    const payload = {
      ...form,
      attendees: toList(form.attendees),
      materials_shared: toList(form.materials_shared),
      samples_distributed: toList(form.samples_distributed),
      follow_up_actions: toList(form.follow_up_actions),
    };
    const result = await dispatch(addInteraction(payload));
    if (addInteraction.fulfilled.match(result)) {
      setForm(EMPTY);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    }
  };

  return (
    <section className="card form-card">
      <div className="card-head">
        <h2>Interaction details</h2>
        <span className="card-sub">Log a structured HCP interaction</span>
      </div>

      <div className="grid-2">
        <Field label="HCP name">
          <input
            className="input"
            placeholder="Search or select HCP…"
            value={form.hcp_name}
            onChange={update("hcp_name")}
          />
        </Field>
        <Field label="Interaction type">
          <select
            className="input"
            value={form.interaction_type}
            onChange={update("interaction_type")}
          >
            <option>Meeting</option>
            <option>Call</option>
            <option>Email</option>
            <option>Conference</option>
            <option>Other</option>
          </select>
        </Field>
      </div>

      <div className="grid-2">
        <Field label="Date">
          <input
            className="input"
            type="date"
            value={form.date}
            onChange={update("date")}
          />
        </Field>
        <Field label="Time">
          <input
            className="input"
            type="time"
            value={form.time}
            onChange={update("time")}
          />
        </Field>
      </div>

      <Field label="Attendees">
        <input
          className="input"
          placeholder="Enter names, comma separated…"
          value={form.attendees}
          onChange={update("attendees")}
        />
      </Field>

      <Field label="Topics discussed">
        <textarea
          className="input textarea"
          placeholder="Enter key discussion points…"
          value={form.topics_discussed}
          onChange={update("topics_discussed")}
        />
      </Field>

      <div className="grid-2">
        <Field label="Materials shared">
          <input
            className="input"
            placeholder="e.g. Product X brochure"
            value={form.materials_shared}
            onChange={update("materials_shared")}
          />
        </Field>
        <Field label="Samples distributed">
          <input
            className="input"
            placeholder="e.g. Sample A x5"
            value={form.samples_distributed}
            onChange={update("samples_distributed")}
          />
        </Field>
      </div>

      <Field label="Observed / inferred HCP sentiment">
        <div className="sentiment-row">
          {["Positive", "Neutral", "Negative"].map((s) => (
            <label key={s} className={`chip chip-${s.toLowerCase()} ${form.sentiment === s ? "chip-active" : ""}`}>
              <input
                type="radio"
                name="sentiment"
                value={s}
                checked={form.sentiment === s}
                onChange={update("sentiment")}
              />
              {s}
            </label>
          ))}
        </div>
      </Field>

      <Field label="Outcomes">
        <textarea
          className="input textarea"
          placeholder="Key outcomes or agreements…"
          value={form.outcomes}
          onChange={update("outcomes")}
        />
      </Field>

      <Field label="Follow-up actions">
        <input
          className="input"
          placeholder="Next steps, comma separated…"
          value={form.follow_up_actions}
          onChange={update("follow_up_actions")}
        />
      </Field>

      <div className="form-footer">
        {saved && <span className="saved-note">Interaction saved.</span>}
        {status === "failed" && !saved && (
          <span className="saved-note" style={{ color: "#c0392b" }}>
            Could not save — is the backend running on port 8000?
          </span>
        )}
        <button
          className="btn btn-primary"
          onClick={handleSubmit}
          disabled={status === "loading" || !form.hcp_name}
        >
          {status === "loading" ? "Saving…" : "Log interaction"}
        </button>
      </div>
    </section>
  );
}

function Field({ label, children }) {
  return (
    <div className="field">
      <label className="field-label">{label}</label>
      {children}
    </div>
  );
}
