const axios = require('axios');

const CATALOG_BASE_URL = process.env.CATALOG_SERVICE_URL || '';
const MOCK_MODE = process.env.CATALOG_SERVICE_MOCK === 'true' || !CATALOG_BASE_URL;

// Petit catalogue simulé, utilisé tant que le Groupe 2 n'expose pas encore
// son API. A retirer une fois CATALOG_SERVICE_URL renseignée et
// CATALOG_SERVICE_MOCK=false.
const CATALOGUE_SIMULE = {
  'produit-demo-1': { prix: 1500, stock: 25, nom: 'Riz 5kg' },
  'produit-demo-2': { prix: 750, stock: 3, nom: 'Huile 1L' },
};

/**
 * Récupère le prix et le stock disponible d'un produit.
 * @param {string} produitId
 * @returns {Promise<{prix: number, stockDisponible: number}>}
 */
async function getInfoProduit(produitId) {
  if (MOCK_MODE) {
    const produit = CATALOGUE_SIMULE[produitId];
    if (!produit) {
      const err = new Error(`Produit ${produitId} introuvable (mode simulation)`);
      err.status = 404;
      throw err;
    }
    return { prix: produit.prix, stockDisponible: produit.stock };
  }

  const { data } = await axios.get(`${CATALOG_BASE_URL}/produits/${produitId}`);
  return { prix: data.prix, stockDisponible: data.stock };
}

/**
 * Vérifie que la quantité demandée est disponible en stock.
 * Lève une erreur (status 409) si le stock est insuffisant.
 */
async function verifierDisponibilite(produitId, quantite) {
  const { stockDisponible } = await getInfoProduit(produitId);
  if (quantite > stockDisponible) {
    const err = new Error(
      `Stock insuffisant pour le produit ${produitId} (demandé: ${quantite}, disponible: ${stockDisponible})`
    );
    err.status = 409;
    throw err;
  }
  return true;
}

module.exports = { getInfoProduit, verifierDisponibilite };
