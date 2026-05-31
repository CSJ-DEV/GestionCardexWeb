// Helpers de formatage pour l'app GestionCardex.

/**
 * Formate un nombre au format français-canadien avec espace comme séparateur
 * de milliers : 99999 → "99 999", 1234567 → "1 234 567".
 * Remplace l'espace insécable retourné par Intl par un espace classique
 * (plus prévisible pour les tests et le copier-coller).
 */
export const fmt = (n) =>
    Number(n ?? 0)
        .toLocaleString("fr-CA")
        .replace(/\u00A0/g, " ")
        .replace(/,/g, " ");
