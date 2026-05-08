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
    return d.length === 10;
};

// --- Courriel ---
// Regex pragmatique (suffisante pour usage métier, pas la RFC 5322 complète)
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
export const isValidEmail = (e) => !e || EMAIL_REGEX.test(e);
