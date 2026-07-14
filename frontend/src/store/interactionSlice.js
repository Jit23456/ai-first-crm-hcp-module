// interactionSlice.js
// Redux Toolkit slice. This is our state management (assignment requires Redux).
// It holds: the list of interactions, the chat transcript, and loading/error flags.
// Async thunks wrap the API calls so components just dispatch actions.

import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import {
  createInteraction,
  fetchInteractions,
  updateInteraction,
  deleteInteraction,
  sendChatMessage,
} from "../api/api";

// ----- Async thunks (side effects) -----
export const loadInteractions = createAsyncThunk(
  "interactions/load",
  async () => await fetchInteractions()
);

export const addInteraction = createAsyncThunk(
  "interactions/add",
  async (data) => await createInteraction(data)
);

export const editInteraction = createAsyncThunk(
  "interactions/edit",
  async ({ id, data }) => await updateInteraction(id, data)
);

export const removeInteraction = createAsyncThunk(
  "interactions/remove",
  async (id) => {
    await deleteInteraction(id);
    return id;
  }
);

export const chat = createAsyncThunk(
  "interactions/chat",
  async (message) => await sendChatMessage(message)
);

const initialState = {
  items: [],
  messages: [
    {
      role: "assistant",
      text:
        "Log interaction details here (e.g. \"Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure\") or ask for help.",
    },
  ],
  status: "idle",
  chatStatus: "idle",
  error: null,
};

const interactionSlice = createSlice({
  name: "interactions",
  initialState,
  reducers: {
    // Add the user's typed message to the transcript immediately (optimistic).
    pushUserMessage: (state, action) => {
      state.messages.push({ role: "user", text: action.payload });
    },
  },
  extraReducers: (builder) => {
    builder
      // load
      .addCase(loadInteractions.fulfilled, (state, action) => {
        state.items = action.payload;
      })
      // add (form)
      .addCase(addInteraction.pending, (state) => {
        state.status = "loading";
      })
      .addCase(addInteraction.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.items.unshift(action.payload);
      })
      .addCase(addInteraction.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      })
      // edit
      .addCase(editInteraction.fulfilled, (state, action) => {
        const idx = state.items.findIndex((i) => i.id === action.payload.id);
        if (idx !== -1) state.items[idx] = action.payload;
      })
      // remove
      .addCase(removeInteraction.fulfilled, (state, action) => {
        state.items = state.items.filter((i) => i.id !== action.payload);
      })
      // chat (agent)
      .addCase(chat.pending, (state) => {
        state.chatStatus = "loading";
      })
      .addCase(chat.fulfilled, (state, action) => {
        state.chatStatus = "succeeded";
        const { reply, interaction, tool_used } = action.payload;
        state.messages.push({ role: "assistant", text: reply, tool: tool_used });
        // If the agent created/edited an interaction, reflect it in the list.
        if (interaction) {
          const idx = state.items.findIndex((i) => i.id === interaction.id);
          if (idx !== -1) state.items[idx] = interaction;
          else state.items.unshift(interaction);
        }
      })
      .addCase(chat.rejected, (state, action) => {
        state.chatStatus = "failed";
        state.messages.push({
          role: "assistant",
          text: "Something went wrong reaching the agent. Check the backend is running.",
        });
        state.error = action.error.message;
      });
  },
});

export const { pushUserMessage } = interactionSlice.actions;
export default interactionSlice.reducer;
