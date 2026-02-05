from g2p_en import G2p
import json

# Oculus Lip Sync Viseme Mapping
# Mappings from ARPABET (g2p_en output) to Oculus Visemes
# sil, PP, FF, TH, DD, kk, CH, SS, nn, RR, aa, E, ih, oh, ou
ARPABET_TO_VISEME = {
    'B': 'PP', 'M': 'PP', 'P': 'PP',
    'F': 'FF', 'V': 'FF',
    'TH': 'TH', 'DH': 'TH',
    'D': 'DD', 'T': 'DD', 'N': 'DD', 'NG': 'DD',
    'K': 'kk', 'G': 'kk', 'Y': 'kk', 'HH': 'kk',
    'CH': 'CH', 'JH': 'CH', 'SH': 'CH', 'ZH': 'CH',
    'S': 'SS', 'Z': 'SS',
    'R': 'RR', 'ER': 'RR', 'L': 'RR',
    'AA': 'aa', 'AO': 'aa', 'AH': 'aa',
    'AE': 'E', 'EH': 'E', 'EY': 'E',
    'IH': 'ih', 'IY': 'ih',
    'AW': 'oh', 'OW': 'oh', 'UW': 'oh',
    'OY': 'ou', 'UH': 'ou',
    ' ': 'sil' # Space treated as silence
}

VISUAL_TARGETS = [
    "sil", "PP", "FF", "TH", "DD", "kk", "CH", "SS", "nn", "RR", "aa", "E", "ih", "oh", "ou"
]

class VisemeMapper:
    def __init__(self):
        self.g2p = G2p()

    def map_text_to_visemes(self, text):
        """
        Converts text to a list of viseme events.
        Estimates timing based on phoneme count (crude approximation).
        """
        if not text:
            return []

        phonemes = self.g2p(text)
        visemes = []
        
        # Filter out numbers/symbols if g2p leaves them, though g2p usually handles them.
        # g2p output list like ['HH', 'AH', '0', 'L', 'OW', '1'] (numbers are stress)
        
        current_time = 0.0
        duration_per_phoneme = 0.1 # Base duration in seconds

        for p in phonemes:
            # Remove stress digits
            p_clean = ''.join([c for c in p if not c.isdigit()])
            
            if p_clean in ARPABET_TO_VISEME:
                viseme = ARPABET_TO_VISEME[p_clean]
                visemes.append({
                    "value": viseme,
                    "time": current_time,
                    "duration": duration_per_phoneme 
                })
                current_time += duration_per_phoneme
            elif p_clean == ' ':
                visemes.append({
                    "value": "sil",
                    "time": current_time,
                    "duration": 0.05
                })
                current_time += 0.05
        
        return visemes

if __name__ == "__main__":
    mapper = VisemeMapper()
    print(mapper.map_text_to_visemes("Hello there"))
