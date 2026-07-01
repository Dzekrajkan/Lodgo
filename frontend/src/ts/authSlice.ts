import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from 'axios'
import api from "../ts/axiosInstance";
import type { Hotel } from "../utils/types";
const apiUrl = import.meta.env.VITE_API_URL;

interface RegisterState {
    username: string,
    email: string,
    password1: string,
    password2: string
}

interface LoginState {
    email: string,
    password: string
}

interface User {
    id: number,
    username: string,
    email: string,
    password_hash: string,
    is_verified: boolean,
    create_at: string,
    avatar_url: string
}

interface FavoriteHotel {
    id: number
    user_id: number,
    hotel_id: number,
    created_at: string
    hotel: Hotel
}

interface stateInitial {
    user: User | null,
    isAuthenticated: boolean | null,
    checked: boolean | null,
    favorites: FavoriteHotel[] | null,

    loading: boolean,
    error: string | null,
    msg: string | null,
    success: string | null
}

const initialState: stateInitial = {
    user: null,
    isAuthenticated: false,
    checked: false,
    favorites: null,

    loading: false,
    error: null,
    msg: null,
    success: null
}

export const fetchMe = createAsyncThunk<User, void, { rejectValue: string }>("auth/me", async (_, { rejectWithValue }) => {
    try {
      const res = await api.get("/me");
      return res.data;
    } catch (err) {
      return rejectWithValue("unauthorized");
    }
  }
);

export const fetchRegister = createAsyncThunk< void, RegisterState, { rejectValue: string }>("auth/register", async ({ username, email, password1, password2 }, { rejectWithValue }) => {
    try {

      const res = await axios.post(`${apiUrl}/register`, { username, email, password1, password2 }, {
        headers: { "Content-Type": "application/json" },
        withCredentials: true,
      });
      
      return res.data;
    } catch (err) {
      if (axios.isAxiosError(err)) {
        return rejectWithValue(
          err.response?.data?.detail || "Registration failed"
        );
      }
      return rejectWithValue("Unknown error");
    }
});

export const fetchLogin = createAsyncThunk<User, LoginState, { rejectValue: string }>("auth/login", async ({ email, password }, {rejectWithValue}) => {
    try {

      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      await axios.post(`${apiUrl}/login`, formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        withCredentials: true,
      });

      const me = await api.get("/me");
      
      return me.data;
    } catch (err) {
      if (axios.isAxiosError(err)) {
        return rejectWithValue(
          err.response?.data?.detail || "Login error"
        );
      }
      return rejectWithValue("Unknown error");
    }
})

export const fetchLogout = createAsyncThunk< void, void, { rejectValue: string }>("auth/logout", async ( _, {rejectWithValue} ) => {
    try{

        axios.post(`${apiUrl}/logout`, {}, {
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            withCredentials: true,
        })

    } catch (err) {
      if (axios.isAxiosError(err)) {
        return rejectWithValue(
          err.response?.data?.detail || "Logout error"
        );
      }
      return rejectWithValue("Unknown error");
    }
})

export const fetchFavoriteHotel = createAsyncThunk<FavoriteHotel[], void, { rejectValue: string }>("auth/favorite_hotel", async ( _, {rejectWithValue} ) => {
    try {
        const res = await api.get(`/favorite`, {
            headers: { "Content-Type": "application/json" },
            withCredentials: true,
        })

        return res.data
    } catch(err) {
      if (axios.isAxiosError(err)) {
        return rejectWithValue(
          err.response?.data?.detail || "Get favorite hotel error"
        );
      }
      return rejectWithValue("Unknown error");
    }
})

export const authSlice = createSlice({
    name: "auth",
    initialState,
    reducers: {
        setFavorites: (state, action) => {
            state.favorites = action.payload
        },
        setError: (state, action) => {
            state.error = action.payload;
        },
        setMsg: (state, action) => {
            state.msg = action.payload;
        },
        setSuccess: (state, action) => {
            state.success = action.payload
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchRegister.pending, state => {
                state.loading = true
                state.error = null
                state.success = null
            })
            .addCase(fetchLogin.pending, state => {
                state.loading = true
                state.error = null
                state.success = null
            })
            .addCase(fetchLogout.pending, state => {
                state.loading = true
                state.error = null
                state.success = null
            })
            .addCase(fetchFavoriteHotel.pending, state => {
                state.favorites = null
                state.loading = true
                state.error = null
                state.success = null
            })
            .addCase(fetchMe.fulfilled, (state, action) => {
                state.user = action.payload;
                state.isAuthenticated = true;
                state.checked = true;
            })
            .addCase(fetchRegister.fulfilled, (state) => {
                state.loading = false;
                state.success = "Registration successful, confirmation email sent to email";
            })
            .addCase(fetchLogin.fulfilled, (state, action) => {
                state.loading = false;
                state.user = action.payload;
                state.isAuthenticated = true;
                state.success = "Login was successful!";
            })
            .addCase(fetchFavoriteHotel.fulfilled, (state, action) => {
                state.loading = false;
                state.favorites = action.payload
                state.success = "Get favorite hotel was successful!";
            })
            .addCase(fetchLogout.fulfilled, (state) => {
                state.loading = false;
                state.user = null;
                state.isAuthenticated = false;
                state.success = "The exit was successful!";
            })
            .addCase(fetchMe.rejected, (state) => {
                state.user = null;
                state.isAuthenticated = false;
                state.checked = true;
            })
            .addCase(fetchRegister.rejected, (state, action) => {
                state.loading = false
                state.error = action.payload || action.error.message || null;
            })
            .addCase(fetchLogin.rejected, (state, action) => {
                state.loading = false
                state.error = action.payload || action.error.message || null;
            })
            .addCase(fetchLogout.rejected, (state, action) => {
                state.loading = false
                state.error = action.payload || action.error.message || null;
            })
            .addCase(fetchFavoriteHotel.rejected, (state, action) => {
                state.favorites = null
                state.loading = false
                state.error = action.payload || action.error.message || null;
            })
    }
})

export const { setFavorites, setError, setSuccess, setMsg } = authSlice.actions
export default authSlice.reducer