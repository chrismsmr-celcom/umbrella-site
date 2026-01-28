import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { GoogleGenerativeAI } from '@google/generative-ai';

// Chargement des variables d'environnement
dotenv.config();

const app = express();
const port = process.env.PORT || 10000;

// Middlewares
app.use(cors());
app.use(express.json());

// Initialisation de Gemini avec le modèle 1.5 Flash
// On utilise 'v1beta' car c'est la version la plus stable pour ce modèle
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel(
    { model: "gemini-1.5-flash" },
    { apiVersion: "v1beta" }
);

// Route de test
app.get('/', (req, res) => {
    res.send('Luce Backend opérationnel ! 🚀');
});

// Route pour parler à l'IA
app.post('/chat', async (req, res) => {
    const { message } = req.body;

    if (!message) {
        return res.status(400).json({ error: "Le message est vide." });
    }

    try {
        const result = await model.generateContent(message);
        const response = await result.response;
        const text = response.text();

        res.json({ reply: text });
    } catch (error) {
        console.error("Erreur Gemini détaillée:", error);
        res.status(500).json({ 
            error: "Erreur lors de la communication avec l'IA",
            details: error.message 
        });
    }
});

app.listen(port, () => {
    console.log(`Serveur lancé sur le port ${port}`);
});
