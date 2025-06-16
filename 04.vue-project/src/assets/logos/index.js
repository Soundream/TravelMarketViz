// Define the base path for logos
const BASE_PATH = '/src/assets/logos';

// Define a fallback logo URL (you should add a default logo file)
const DEFAULT_LOGO = new URL('./Wego_logo.png', import.meta.url).href;

// Define company codes and their corresponding logo filenames
const COMPANY_LOGOS = {
  'ABNB': 'ABNB_logo.png',
  'Almosafer': 'Almosafer_logo.png',
  'BKNG': 'BKNG_logo.png',
  'Cleartrip': 'Cleartrip_logo.png',
  'DESP': 'DESP_logo.png',
  'EaseMyTrip': 'EASEMYTRIP_logo.png',
  'EDR': 'EDR_logo.png',
  'Etraveli': 'Etraveli_logo.png',
  'EXPE': 'EXPE_logo.png',
  'FLT': 'FlightCentre_logo.png',
  'IXIGO': 'IXIGO_logo.png',
  'Kiwi': 'Kiwi_logo.png',
  'LMN': 'LMN_logo.png',
  'MMYT': 'MMYT_logo.png',
  'OWW': 'Orbitz_logo.png',
  'PCLN': 'PCLN_logo.png',
  'SEERA': 'SEERA_logo.png',
  'Skyscanner': 'Skyscanner_logo.png',
  'TCOM': 'TCOM_logo.png',
  'Travelocity': 'Travelocity_logo.png',
  'Traveloka': 'Traveloka_logo.png',
  'TRIP': 'TRIP_logo.png',
  'TRVG': 'TRVG_logo.png',
  'WEB': 'Webjet_logo.png',
  'Wego': 'Wego_logo.png',
  'YTRA': 'Yatra_logo.png'
};

// Function to get logo URL
function getLogoUrl(companyCode) {
  const filename = COMPANY_LOGOS[companyCode];
  if (!filename) {
    console.warn(`No logo filename defined for company code: ${companyCode}`);
    return '/images/logos/Wego_logo.png'; // Default logo with absolute path
  }
  return `/images/logos/${filename}`;
}

// Export individual logo URLs
export const ABNB_LOGO = getLogoUrl('ABNB');
export const ALMOSAFER_LOGO = getLogoUrl('Almosafer');
export const BKNG_LOGO = getLogoUrl('BKNG');
export const CLEARTRIP_LOGO = getLogoUrl('Cleartrip');
export const DESP_LOGO = getLogoUrl('DESP');
export const EASEMYTRIP_LOGO = getLogoUrl('EaseMyTrip');
export const EDR_LOGO = getLogoUrl('EDR');
export const ETRAVELI_LOGO = getLogoUrl('Etraveli');
export const EXPE_LOGO = getLogoUrl('EXPE');
export const FLT_LOGO = getLogoUrl('FLT');
export const IXIGO_LOGO = getLogoUrl('IXIGO');
export const KIWI_LOGO = getLogoUrl('Kiwi');
export const LMN_LOGO = getLogoUrl('LMN');
export const MMYT_LOGO = getLogoUrl('MMYT');
export const OWW_LOGO = getLogoUrl('OWW');
export const PCLN_LOGO = getLogoUrl('PCLN');
export const SEERA_LOGO = getLogoUrl('SEERA');
export const SKYSCANNER_LOGO = getLogoUrl('Skyscanner');
export const TCOM_LOGO = getLogoUrl('TCOM');
export const TRAVELOCITY_LOGO = getLogoUrl('Travelocity');
export const TRAVELOKA_LOGO = getLogoUrl('Traveloka');
export const TRIP_LOGO = getLogoUrl('TRIP');
export const TRVG_LOGO = getLogoUrl('TRVG');
export const WEB_LOGO = getLogoUrl('WEB');
export const WEGO_LOGO = getLogoUrl('Wego');
export const YTRA_LOGO = getLogoUrl('YTRA');

// Export the mapping object
export const logoMap = Object.fromEntries(
  Object.keys(COMPANY_LOGOS).map(code => [code, getLogoUrl(code)])
); 