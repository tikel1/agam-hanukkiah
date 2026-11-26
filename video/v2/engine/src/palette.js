/* Palette of the film. Source: video/storyboard/storyboard.md §1.2 (fountain palette + logo dots). */
export const PAPER = 0xF7F5EE;      // warm white background
export const WHITE = 0xFFFFFF;
export const INK = 0x232C5E;        // logo navy: titles, subtitles
export const NAVY = 0x2B2F6B;       // fountain navy: dark shapes
export const NIGHT = 0x232C5E;

export const FOUNTAIN = {
  white: 0xF4F1E4, yellow: 0xF2C94C, orange: 0xE8893F, coral: 0xE8655C, brick: 0xA8322A, rose: 0xDC8A86,
  lilac: 0x9A8CC0, periwinkle: 0x7484C4, light_blue: 0xA3C1E0, blue: 0x3E5FB0, navy: 0x2B2F6B,
  mint: 0xA8DDB5, teal: 0x3E8F7C, green: 0x4E9E5E, grey: 0xA9B3B6,
};
const F = FOUNTAIN;
/** 12 stripe colours in colour-wheel order. */
export const SPECTRUM = [F.yellow, F.orange, F.coral, F.brick, F.rose, F.lilac, F.periwinkle, F.blue, F.light_blue, F.mint, F.teal, F.green];
/** Dots of the logo, ordered so neighbours never repeat. */
export const DOTS = [0xE4432F, 0xF6D21C, 0x1FA3A8, 0x6A5EA8, 0x6BB7E6, 0x1B7F3E, 0xA81F2A, 0x4F63B0, 0xCFA3D1, 0xF39A1E];
export const FLAME = { outer: 0xF39A1E, inner: 0xF6D21C, core: 0xFFF6C8 };

export const hexToRgb = (hex) => [((hex >> 16) & 255) / 255, ((hex >> 8) & 255) / 255, (hex & 255) / 255];

/* v2 additions (storyboard v2 §2.1, §2.2) */
export const NIGHT_SKY = 0x1E2452;   // night ground of v2, a step under INK
export const NIGHT_SLAT = 0x2E3570;  // subtitle slat and frame "white" at night
export const GOLD = 0xD9B24A;        // candle cups
export const GROUND = { paper: PAPER, sky: 0xDCE7F2, memory: 0xF4E7D0, amber: 0xF6B54A, amberDim: 0xF3D9A4, study: 0xE6E2D6, screen: INK, workshop: 0xDCE2E6, night: NIGHT_SKY };
export const CLAUDE = { body: 0xD97757, shade: 0xB95F42, eye: 0x1F1E1D };
export const HOLO = 0x8FD3E8;
export const PRINT_WHITE = { a: 0xFBFAF6, b: 0xEDEBE4, cap: 0xF4F1E4 };   // the unpainted print
