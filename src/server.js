require('dotenv').config();
const express = require('express');
const { sequelize } = require('./models');

const app = express();
app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok', module: 'panier-commandes-livraison' });
});

// Les routes (panier, commandes, livraison, factures) seront branchées ici
// au fur et à mesure du développement.

const PORT = process.env.PORT || 3000;

async function start() {
  await sequelize.authenticate();
  await sequelize.sync();
  app.listen(PORT, () => {
    console.log(`Serveur Groupe 3 démarré sur le port ${PORT}`);
  });
}

if (require.main === module) {
  start();
}

module.exports = app;
