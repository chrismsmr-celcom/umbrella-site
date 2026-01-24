const QRCode = require("qrcode");

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const { text, file, color = "#000000", size = 400 } = req.body;

    if (!text && !file) {
      return res.status(400).json({ error: "No data provided" });
    }

    // Données à encoder
    const data = text || file;

    // Génération du QR code avec options dynamiques
    const qrDataURL = await QRCode.toDataURL(data, {
      errorCorrectionLevel: "H",
      width: parseInt(size),
      color: {
        dark: color,      // Couleur du QR code
        light: "#ffffff"  // Fond blanc
      },
      margin: 2
    });

    res.status(200).json({ qr: qrDataURL });

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

