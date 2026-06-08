window.addEventListener('load', () => {
  setTimeout(() => {
    // Verstecke DWD-Fehler
    document.querySelectorAll('[class*="error"], [class*="offline"]').forEach(el => {
      if (el.textContent.includes('DWD') || el.textContent.includes('offline')) {
        el.style.display = 'none';
      }
    });
    
    // Verstecke Loading-Meldungen
    document.querySelectorAll('[class*="loading"]').forEach(el => {
      if (el.textContent.includes('werden geladen')) {
        el.textContent = 'Open-Meteo-Daten werden geladen...';
      }
    });
    
    console.log('DWD-Fehler versteckt, Open-Meteo wird geladen');
  }, 500);
});
