// store.js — configures the Redux store with our single slice.
import { configureStore } from "@reduxjs/toolkit";
import interactionReducer from "./interactionSlice";

export const store = configureStore({
  reducer: {
    interactions: interactionReducer,
  },
});
