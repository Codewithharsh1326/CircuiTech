import axios from "axios";
import { v4 as uuidv4 } from "uuid";

const SESSION_ID = uuidv4();

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
    "X-Session-ID": SESSION_ID,
  },
});

export { SESSION_ID };
export default api;
