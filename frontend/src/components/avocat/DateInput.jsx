import { forwardRef } from "react";
import { Input } from "@/components/ui/input";

/**
 * Champ de saisie de date au format ISO (AAAA-MM-JJ).
 *
 * Avantage vs `<input type="date">` natif : on peut taper 8 chiffres en continu
 * (ex. "20260308") sans avoir à passer entre année / mois / jour à la flèche.
 * Les tirets sont insérés automatiquement aux positions 4 et 7.
 *
 * Émet la même valeur ISO que `<input type="date">`, donc parfaitement
 * compatible avec le backend (`datedeb`, `dateinsc`, etc.).
 *
 * Props :
 *   - value: string ISO "AAAA-MM-JJ" ou ""
 *   - onChange: (iso: string) => void
 *   - disabled, className, placeholder, ...rest
 */
export const DateInput = forwardRef(({ value, onChange, className, placeholder, disabled, ...rest }, ref) => {
    // Garde uniquement les chiffres, max 8
    const digitsOnly = (str) => (str || "").replace(/\D/g, "").slice(0, 8);

    // Formate AAAAMMJJ → AAAA-MM-JJ (au fil de la saisie)
    const format = (digits) => {
        if (digits.length <= 4) return digits;
        if (digits.length <= 6) return `${digits.slice(0, 4)}-${digits.slice(4)}`;
        return `${digits.slice(0, 4)}-${digits.slice(4, 6)}-${digits.slice(6)}`;
    };

    const handleChange = (e) => {
        const next = digitsOnly(e.target.value);
        // Émet la valeur formatée ; ce sera "" si vide, "AAAA" partiel, ou "AAAA-MM-JJ" complet
        onChange?.(format(next));
    };

    // Affiche la valeur formatée (le parent stocke déjà au format ISO)
    const displayed = format(digitsOnly(value));

    return (
        <Input
            ref={ref}
            type="text"
            inputMode="numeric"
            value={displayed}
            onChange={handleChange}
            placeholder={placeholder ?? "AAAA-MM-JJ"}
            maxLength={10}
            disabled={disabled}
            className={className}
            {...rest}
        />
    );
});
DateInput.displayName = "DateInput";
