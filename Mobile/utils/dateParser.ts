export const parseDate = (input: string): string | null => {
    // Temizle ve boşlukları/noktaları tire ile değiştir
    const cleanInput = input.trim().replace(/[\s\.]/g, '-');

    // YYYY-MM-DD formatı kontrolü
    if (/^\d{4}-\d{2}-\d{2}$/.test(cleanInput)) return cleanInput;

    // DD-MM-YYYY veya DD-MM-YY formatı
    const parts = cleanInput.split('-');
    if (parts.length === 3) {
        let [day, month, year] = parts;

        // Yıl 2 haneli ise 20xx yap
        if (year.length === 2) year = '20' + year;

        // Basit validasyon
        if (parseInt(day) > 31 || parseInt(month) > 12) return null;

        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    }

    // 190226 gibi bitişik yazım (6 hane)
    if (/^\d{6}$/.test(cleanInput)) {
        const day = cleanInput.substring(0, 2);
        const month = cleanInput.substring(2, 4);
        const year = '20' + cleanInput.substring(4, 6);
        return `${year}-${month}-${day}`;
    }

    return null;
};
