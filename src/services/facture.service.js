const { v4: uuidv4 } = require('uuid');

/**
 * Génère un numéro de facture lisible et unique.
 * Format : FACT-<année>-<8 caractères>
 */
function genererNumeroFacture() {
  const annee = new Date().getFullYear();
  const suffixe = uuidv4().split('-')[0].toUpperCase();
  return `FACT-${annee}-${suffixe}`;
}

module.exports = { genererNumeroFacture };
