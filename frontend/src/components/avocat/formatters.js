// Formatters et validators spécifiques au Québec / Canada

// --- Code postal canadien : A1A 1A1 (lettre/chiffre alternés) ---
// On accepte la saisie en continu et on insère automatiquement l'espace.
const QC_CP_REGEX = /^[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z][ ]\d[ABCEGHJ-NPRSTV-Z]\d$/;

export const formatCodePostal = (raw) => {
    if (!raw) return "";
    // On ne garde que [A-Z0-9], puis on coupe à 6 caractères
    const cleaned = raw.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 6);
    if (cleaned.length <= 3) return cleaned;
    return `${cleaned.slice(0, 3)} ${cleaned.slice(3)}`;
};

export const isValidCodePostal = (cp) => !cp || QC_CP_REGEX.test(cp);

// --- Téléphone nord-américain : ###-###-#### ---
export const formatTelephone = (raw) => {
    if (!raw) return "";
    const d = raw.replace(/\D/g, "").slice(0, 10);
    if (d.length <= 3) return d;
    if (d.length <= 6) return `${d.slice(0, 3)}-${d.slice(3)}`;
    return `${d.slice(0, 3)}-${d.slice(3, 6)}-${d.slice(6)}`;
};

export const isValidTelephone = (tel) => {
    if (!tel) return true; // facultatif
    const d = tel.replace(/\D/g, "");
    if (d.length === 0) return true;  // que des espaces / caractères non-chiffres → traité comme vide
    return d.length === 10;
};

// --- Courriel ---
// Regex pragmatique (suffisante pour usage métier, pas la RFC 5322 complète)
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
export const isValidEmail = (e) => !e || EMAIL_REGEX.test(e);

// --- Numéro d'assurance sociale (NAS) canadien ---
// Format d'affichage : "### ### ###". Stocké en interne sur 9 chiffres bruts.
export const formatNAS = (raw) => {
    if (!raw) return "";
    const d = String(raw).replace(/\D/g, "").slice(0, 9);
    if (d.length <= 3) return d;
    if (d.length <= 6) return `${d.slice(0, 3)} ${d.slice(3)}`;
    return `${d.slice(0, 3)} ${d.slice(3, 6)} ${d.slice(6)}`;
};

// Validation NAS — algorithme Luhn (identique à la fonction VB legacy
// `funcValidNoAssSoc`, qui est un Luhn standard). Tolère espaces/tirets.
// Retourne true pour une chaîne vide (la validation "obligatoire" est gérée
// ailleurs ; ici on ne valide que la cohérence du numéro saisi).
export const isValidNAS = (raw) => {
    if (!raw) return true;
    const d = String(raw).replace(/\D/g, "");
    if (d.length === 0) return true;
    if (d.length !== 9) return false;
    let tot = 0;
    for (let i = 1; i <= 8; i++) {
        let c = parseInt(d.charAt(i - 1), 10);
        if (i % 2 === 0) {
            c = c * 2;
            if (c > 9) c = Math.floor(c / 10) + (c % 10);
        }
        tot += c;
    }
    const v = (10 - (tot % 10)) % 10;
    return v === parseInt(d.charAt(8), 10);
};
