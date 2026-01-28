import express from "express";
import cors from "cors";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

/* ================= MIDDLEWARE ================= */
app.use(cors());
app.use(express.json());

/* ================= TEST ================= */
app.get("/", (req, res) => {
  res.send("Umbrella Luce Backend is running");
});

app.get("/api/luce", (req, res) => {
  res.json({
    status: "OK",
    message: "Luce backend is ready. Use POST."
  });
});

/* ================= LUCE API ================= */
app.post("/api/luce", async (req, res) => {
  const { message } = req.body;

  if (!message) {
    return res.status(400).json({ error: "Message manquant" });
  }

  if (!process.env.GEMINI_API_KEY) {
    return res.status(500).json({ error: "Clé Gemini absente" });
  }

const { GoogleGenerativeAI } = require("@google/generative-ai");

// Initialisez avec la version v1beta
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel(
  { model: "gemini-1.5-flash" }, 
  { apiVersion: 'v1beta' } // <--- Ajoutez ceci
);


  try {
    const response = await fetch(GEMINI_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              {
                text:
                  "Tu es Luce, l'IA d'Umbrella. Ton ton est pro et chaleureux. Réponds court.\n\nUtilisateur: " +
                  message
              }
            ]
          }
        ]
      })
    });

    const data = await response.json();

    if (!response.ok) {
      console.error("Gemini error:", data);
      return res.status(500).json({ error: "Erreur Gemini API" });
    }

    const reply =
      data?.candidates?.[0]?.content?.parts?.[0]?.text ||
      "Je n’ai pas compris votre demande.";

    res.json({ reply });
  } catch (err) {
    console.error("Erreur serveur:", err);
    res.status(500).json({ error: "Erreur serveur Luce" });
  }
});

/* ================= START ================= */
app.listen(PORT, () => {
  console.log("Luce backend running on port", PORT);
});
