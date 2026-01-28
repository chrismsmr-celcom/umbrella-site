import express from "express";
import cors from "cors";
import fetch from "node-fetch";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

/* ================= MIDDLEWARE ================= */
app.use(cors());
app.use(express.json());

/* ================= TEST ROUTE ================= */
app.get("/", (req, res) => {
  res.send("Umbrella Luce Backend is running");
});

app.get("/api/luce", (req, res) => {
  res.json({
    status: "OK",
    message: "Luce backend is ready. Use POST to talk."
  });
});

/* ================= LUCE API ================= */
app.post("/api/luce", async (req, res) => {
  const userMessage = req.body.message;

  if (!userMessage) {
    return res.status(400).json({ error: "Message manquant" });
  }

  if (!process.env.GEMINI_API_KEY) {
    return res.status(500).json({ error: "Clé API Gemini manquante" });
  }

  const GEMINI_URL =
    "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=" +
    process.env.GEMINI_API_KEY;

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
                  "Tu es Luce, l'IA d'Umbrella. Ton ton est pro, clair et chaleureux. Réponds court.\n\nUtilisateur: " +
                  userMessage
              }
            ]
          }
        ]
      })
    });

    const data = await response.json();

    if (!response.ok) {
      console.error("Gemini API error:", data);
      return res.status(500).json({ error: "Erreur Gemini API" });
    }

    const text =
      data?.candidates?.[0]?.content?.parts?.[0]?.text ||
      "Je n'ai pas compris votre demande.";

    res.json({ reply: text });
  } catch (err) {
    console.error("Server error:", err);
    res.status(500).json({ error: "Erreur serveur Luce" });
  }
});

/* ================= START ================= */
app.listen(PORT, () => {
  console.log(`Luce backend running on port ${PORT}`);
});
