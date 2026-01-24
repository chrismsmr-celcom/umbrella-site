const express = require('express');
const multer = require('multer');
const QRCode = require('qrcode');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 3000;

// Pour accepter les requêtes depuis n'importe quel frontend
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Multer pour fichiers uploadés
const upload = multer({ storage: multer.memoryStorage() });

// Endpoint pour générer QR code
app.post('/generate', upload.single('file'), async (req, res) => {
    try {
        let data = req.body.text || '';

        // Si c'est un fichier
        if (req.file) {
            const mimeType = req.file.mimetype;
            const base64 = req.file.buffer.toString('base64');
            data = `data:${mimeType};base64,${base64}`;
        }

        // Générer QR code en Data URL
        const qrDataURL = await QRCode.toDataURL(data, {
            errorCorrectionLevel: 'H',
            width: 400, // taille QR code
            margin: 2
        });

        res.json({ qr: qrDataURL });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Health check
app.get('/', (req, res) => {
    res.send('Backend QR Code est en ligne !');
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
