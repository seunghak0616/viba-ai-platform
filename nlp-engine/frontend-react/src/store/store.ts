import { configureStore } from '@reduxjs/toolkit';
import authSlice from './slices/authSlice';
import projectSlice from './slices/projectSlice';
import designSlice from './slices/designSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    projects: projectSlice,
    design: designSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;