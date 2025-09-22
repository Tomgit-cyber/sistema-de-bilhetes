// src/firebase-config.js
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Substitua pela sua configuração real do Firebase
const firebaseConfig = {
  apiKey: "AIzaSyDHdtk8bqgYX92l1FzbBa46xtRWf-NlBrM",
  authDomain: "sistema-bilhetes-app.firebaseapp.com",
  projectId: "sistema-bilhetes-app",
  storageBucket: "sistema-bilhetes-app.appspot.com",
  messagingSenderId: "467620499912",
  appId: "YOUR_APP_ID_HERE" // <<< SUBSTITUIR PELO APP ID REAL >>>
};

// Inicializa o Firebase
const app = initializeApp(firebaseConfig);

// Exporta os serviços utilizados
export const auth = getAuth(app);
export const db = getFirestore(app);

export default app;