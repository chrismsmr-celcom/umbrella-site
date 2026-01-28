import express from "express";
import cors from "cors";
import { GoogleGenerativeAI } from "@google/generative-ai";

const app = express();
app.use(cors());
app.use(express.json());

/* 🔐 CLÉ GEMINI STOCKÉE SUR RENDER */
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

const model = genAI.getGenerativeModel({
  model: "gemini-2.0-flash",
  systemInstruction:
    "Tu es Luce, l'IA d'Umbrella. Ton ton est professionnel, clair et concis."
});

/* ENDPOINT LUCE */
app.post("/luce", async (req, res) => {
  try {
    const { prompt } = req.body;
    if (!prompt) return res.status(400).json({ error: "Prompt manquant" });

    const result = await model.generateContent(prompt);
    const response = await result.response;

    res.json({ text: response.text() });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Erreur Luce" });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log("Umbrella API sécurisée"));
